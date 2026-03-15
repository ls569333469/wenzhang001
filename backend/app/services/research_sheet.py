"""
P32-B: 投研记录 Google Sheets 服务
读写 "投研记录" Tab，提供去重过滤和分析回写功能。
复用现有 google_sheets_source 的连接。
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.core.config import get_logger, cn_now, CN_TZ
from app.services.google_sheets_source import google_sheets_source

logger = get_logger("services.research_sheet")

TAB_NAME = "投研记录"
SCOUT_TAB_NAME = "侦察源"
DEDUP_HOURS = 24  # 去重窗口（小时）

# 列顺序（与 Sheets 表头一致）
COLUMNS = ["项目名", "Twitter", "赛道", "上次分析时间", "催化剂摘要", "评级", "一句话摘要", "发布状态", "侦察次数"]


class ResearchSheetService:
    """投研记录 Sheets 服务"""

    def __init__(self):
        self._cache: Optional[List[Dict]] = None
        self._cache_time: float = 0

    def _get_worksheet(self):
        """获取 投研记录 worksheet"""
        source = google_sheets_source
        if not source._init_client():
            logger.warning("[ResearchSheet] Google Sheets 未连接")
            return None
        try:
            return source._spreadsheet.worksheet(TAB_NAME)
        except Exception as e:
            logger.error(f"[ResearchSheet] 无法打开 Tab '{TAB_NAME}': {e}")
            return None

    def get_all_records(self, use_cache: bool = True) -> List[Dict]:
        """读取所有投研记录"""
        import time
        now = time.time()

        # 5 分钟缓存
        if use_cache and self._cache is not None and (now - self._cache_time) < 300:
            return self._cache

        ws = self._get_worksheet()
        if not ws:
            return []

        try:
            records = ws.get_all_records()
            self._cache = records
            self._cache_time = now
            logger.info(f"[ResearchSheet] 读取 {len(records)} 条投研记录")
            return records
        except Exception as e:
            logger.error(f"[ResearchSheet] 读取失败: {e}")
            return []

    def dedup_filter(self, scout_projects: List[Dict]) -> List[Dict]:
        """
        去重过滤：对比侦察官输出和 Sheets 历史记录。

        规则：
        1. 从未分析过 → 保留
        2. 上次分析 > DEDUP_HOURS → 保留
        3. 上次分析 ≤ DEDUP_HOURS 但有新催化剂（buzz 不同）→ 保留
        4. 否则 → 跳过

        Args:
            scout_projects: 侦察官输出的项目列表 [{name, twitter, category, buzz, ...}]

        Returns:
            过滤后的项目列表
        """
        records = self.get_all_records(use_cache=False)  # 去重必须读最新

        # 建立 name → record 映射（不区分大小写）
        history_map: Dict[str, Dict] = {}
        for r in records:
            name = r.get("项目名", "").strip().lower()
            if name:
                history_map[name] = r

        now = cn_now()
        kept = []
        skipped = []

        def _normalize_name(n: str) -> str:
            """去除 (@handle) 后缀，提取纯项目名"""
            n = re.sub(r"\s*\(@[^)]*\)\s*$", "", n).strip()
            return n.lower()

        def _find_in_history(name_key: str) -> Optional[Dict]:
            """多级匹配: 精确 → 去handle → 子串"""
            # 1) 精确匹配
            if name_key in history_map:
                return history_map[name_key]
            # 2) 去掉 (@handle) 后匹配
            clean = _normalize_name(name_key)
            if clean != name_key and clean in history_map:
                return history_map[clean]
            # 3) 子串匹配（项目名包含在历史名中，或反过来）
            for h_name, h_record in history_map.items():
                if clean in h_name or h_name in clean:
                    return h_record
            return None

        for p in scout_projects:
            name = p.get("name", "").strip()
            name_key = name.lower()

            # 规则 1: 从未分析过（多级匹配）
            record = _find_in_history(name_key)
            if record is None:
                kept.append(p)
                logger.info(f"  ✅ {name}: 新项目，保留")
                continue

            last_time_str = record.get("上次分析时间", "")

            # 解析上次分析时间
            last_time = self._parse_datetime(last_time_str)
            if last_time is None:
                kept.append(p)
                logger.info(f"  ✅ {name}: 无有效分析时间，保留")
                continue

            hours_ago = (now - last_time).total_seconds() / 3600

            # 规则 2: 超过去重窗口
            if hours_ago > DEDUP_HOURS:
                kept.append(p)
                logger.info(f"  ✅ {name}: 上次分析 {hours_ago:.0f}h 前（>{DEDUP_HOURS}h），保留")
                continue

            # 规则 3: 窗口内 → 直接跳过
            # 注: buzz(侦察官原始) vs 催化剂摘要(enrichment后) 格式不同，
            #      比较永远不等，导致去重失效。改为窗口内一律跳过。
            skipped.append(name)
            logger.info(f"  ❌ {name}: {hours_ago:.0f}h 前已分析，跳过")

        logger.info(
            f"[ResearchSheet] 去重结果: {len(kept)}/{len(scout_projects)} 保留, "
            f"{len(skipped)} 跳过 ({', '.join(skipped) if skipped else '无'})"
        )
        return kept

    def write_analysis_records(self, enriched_projects: List[Dict], date_str: str):
        """
        分析完成后回写记录到 Sheets。
        如果项目已存在则更新行，否则追加新行。

        Args:
            enriched_projects: 策略官输出的 enriched 项目列表
            date_str: 日期字符串如 "20260303"
        """
        ws = self._get_worksheet()
        if not ws:
            logger.warning("[ResearchSheet] 无法回写 — Sheets 未连接")
            return

        # 读取现有记录找到行号
        try:
            all_values = ws.get_all_values()  # 含表头
        except Exception as e:
            logger.error(f"[ResearchSheet] 读取失败: {e}")
            return

        # 建立 name → row_index 映射（1-indexed，跳过表头）
        name_to_row: Dict[str, int] = {}
        for i, row in enumerate(all_values):
            if i == 0:
                continue  # 跳过表头
            if row:
                name_to_row[row[0].strip().lower()] = i + 1  # gspread 1-indexed

        now_str = cn_now().strftime("%Y-%m-%d %H:%M")
        updated = 0
        appended = 0

        for p in enriched_projects:
            name = p.get("name", "Unknown")
            name_key = name.lower().strip()
            twitter = p.get("twitter", "")
            category = p.get("category", "")
            catalyst = p.get("catalyst", "")
            summary = p.get("summary", p.get("buzz", ""))
            # 评级从策略官报告中尝试提取（暂留空）
            rating = ""

            row_data = [name, twitter, category, now_str, catalyst, rating, summary, "已分析"]

            if name_key in name_to_row:
                # 更新已有行（保留侦察次数并+1）
                row_idx = name_to_row[name_key]
                existing_row = all_values[row_idx - 1] if row_idx <= len(all_values) else []
                old_count = 0
                if len(existing_row) >= 9:
                    try:
                        old_count = int(existing_row[8])
                    except (ValueError, IndexError):
                        old_count = 0

                row_data.append(str(old_count + 1))
                try:
                    ws.update(f"A{row_idx}:I{row_idx}", [row_data])
                    updated += 1
                except Exception as e:
                    logger.error(f"  更新 {name} 失败: {e}")
            else:
                # 追加新行
                row_data.append("1")  # 侦察次数=1
                try:
                    ws.append_row(row_data)
                    appended += 1
                except Exception as e:
                    logger.error(f"  追加 {name} 失败: {e}")

        # 清除缓存
        self._cache = None
        logger.info(f"[ResearchSheet] 回写完成: {updated} 更新, {appended} 新增")

    def _parse_datetime(self, s: str) -> Optional[datetime]:
        """解析多种时间格式"""
        if not s or not s.strip():
            return None
        s = s.strip()
        for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y%m%d", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.replace(tzinfo=CN_TZ)
            except ValueError:
                continue
        return None

    def get_scout_sources(self) -> List[Dict]:
        """
        P32-C: 从 Sheets '侦察源' Tab 读取启用的 X 账号列表。
        
        Tab 结构: | 账号 | 描述 | 启用 |
        
        Returns:
            [{handle: "@xxx", desc: "描述"}, ...]
        """
        # 默认账号（Sheets 不可用时 fallback）
        DEFAULTS = [
            {"handle": "@leakmealpha", "desc": "Crypto KOL Tracker，追踪 KOL 新关注行为"},
            {"handle": "@top7ico", "desc": "项目早期融资与 ICO 信息"},
            {"handle": "@Eli5defi", "desc": "DeFi 项目科普与分析"},
            {"handle": "@Web3Alerts", "desc": "Web3 生态动态与项目预警"},
            {"handle": "@WY_mask", "desc": "中文 Crypto 投研与项目分析"},
        ]

        source = google_sheets_source
        # 尝试初始化（可能已经在其他地方初始化过）
        if not source._initialized:
            source._init_client()
        
        if not source._initialized or not source._spreadsheet:
            logger.warning("[ResearchSheet] Sheets 未连接，使用默认信源")
            return DEFAULTS

        try:
            ws = source._spreadsheet.worksheet(SCOUT_TAB_NAME)
            records = ws.get_all_records()
            enabled = []
            for r in records:
                handle = str(r.get("账号", "")).strip()
                desc = str(r.get("描述", "")).strip()
                is_enabled = str(r.get("启用", "TRUE")).strip().upper()
                if handle and is_enabled in ("TRUE", "是", "1", "YES"):
                    enabled.append({"handle": handle, "desc": desc})
            
            if not enabled:
                logger.warning("[ResearchSheet] 侦察源 Tab 无启用账号，使用默认")
                return DEFAULTS

            logger.info(f"[ResearchSheet] 读取 {len(enabled)} 个侦察源")
            return enabled
        except Exception as e:
            logger.warning(f"[ResearchSheet] 读取侦察源失败: {e}，使用默认")
            return DEFAULTS

    def refresh_cache(self):
        """清除缓存"""
        self._cache = None
        self._cache_time = 0


# Singleton
research_sheet_service = ResearchSheetService()
