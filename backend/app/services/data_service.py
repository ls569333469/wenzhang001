"""
P27-P2: DataPanel 数据服务
统一为 3 个 DataPanel (吹捧/嘴撸/投研) 提供 Google Sheets 数据读取

Tab 命名规范 (全中文):
- 吹捧素材: CZ/何一/Binance 推文动态
- 嘴撸项目: Kaito 项目列表
- 嘴撸_{项目名}: 每个项目的角度+情报 (如 嘴撸_Berachain)
- 投研项目: 有融资的 Web3 项目
"""

import time
from typing import List, Dict, Optional
from app.core.config import get_logger
from app.services.google_sheets_source import google_sheets_source

logger = get_logger("services.data")

# 缓存 TTL (秒)
CACHE_TTL = 300  # 5 分钟


class DataService:
    """P27: DataPanel 数据服务"""
    
    def __init__(self):
        self._cache: Dict[str, dict] = {}  # {tab_name: {data, timestamp}}
    
    def _read_tab(self, tab_name: str) -> List[Dict]:
        """
        读取 Google Sheets 指定 Tab，带缓存。
        直接返回原始中文列名的记录（不做 field mapping）。
        """
        now = time.time()
        cached = self._cache.get(tab_name)
        if cached and (now - cached["timestamp"]) < CACHE_TTL:
            return cached["data"]
        
        # 复用 google_sheets_source 的连接
        source = google_sheets_source
        if not source._init_client():
            logger.warning(f"[DataService] Google Sheets 未连接，Tab '{tab_name}' 返回空")
            return []
        
        try:
            worksheet = source._spreadsheet.worksheet(tab_name)
            records = worksheet.get_all_records()
            logger.info(f"[DataService] 读取 Tab '{tab_name}': {len(records)} 条记录")
            self._cache[tab_name] = {"data": records, "timestamp": now}
            return records
        except Exception as e:
            logger.error(f"[DataService] 读取 Tab '{tab_name}' 失败: {e}")
            return []
    
    # ===== 🌸 吹捧模式 =====
    
    def get_bullish_feed(self, category: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        获取吹捧素材 Feed
        Tab: 吹捧素材
        列: 日期, 作者, 内容, 分类, 来源
        """
        records = self._read_tab("吹捧素材")
        
        # 按分类过滤
        if category and category != "all":
            records = [r for r in records if r.get("分类", "") == category]
        
        # 按日期倒序 (最新的在前)
        records.sort(key=lambda r: r.get("日期", ""), reverse=True)
        
        # 格式化返回
        result = []
        for i, r in enumerate(records[:limit]):
            result.append({
                "id": str(i + 1),
                "author": r.get("作者", ""),
                "content": r.get("内容", ""),
                "category": r.get("分类", ""),
                "time": r.get("日期", ""),
                "source": r.get("来源", ""),
            })
        return result
    
    # ===== 🎯 Kaito 嘴撸模式 =====
    
    def get_kaito_projects(self) -> List[Dict]:
        """
        获取嘴撸项目列表
        Tab: 嘴撸项目
        列: 项目ID, 项目名称, 最后写作时间
        """
        records = self._read_tab("嘴撸项目")
        result = []
        for r in records:
            result.append({
                "id": r.get("项目ID", ""),
                "name": r.get("项目名称", ""),
                "last_written": r.get("最后写作时间", ""),
            })
        return result
    
    def get_kaito_intel(self, project_id: str) -> Dict:
        """
        获取某个项目的情报 (角度 + 新闻)
        Tab: 嘴撸_{项目名}
        列: 类型(角度/情报), 标题, 描述, 来源, 时间
        """
        # 先查项目名
        projects = self.get_kaito_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        project_name = project["name"] if project else project_id
        
        tab_name = f"嘴撸_{project_name}"
        records = self._read_tab(tab_name)
        
        angles = []
        news = []
        for i, r in enumerate(records):
            item_type = r.get("类型", "")
            item = {
                "id": f"{item_type[0]}{i+1}" if item_type else f"i{i+1}",
                "title": r.get("标题", ""),
                "desc": r.get("描述", ""),
                "source": r.get("来源", ""),
                "time": r.get("时间", ""),
            }
            if item_type == "角度":
                angles.append(item)
            else:
                news.append(item)
        
        return {
            "project": project_name,
            "last_written": project.get("last_written", "") if project else "",
            "angles": angles,
            "news": news,
        }
    
    # ===== 🔬 投研模式 =====
    
    def get_research_projects(self, query: Optional[str] = None) -> List[Dict]:
        """
        搜索投研项目
        Tab: 投研记录 (P32-B: 替代旧 投研项目 Tab)
        列: 项目名, Twitter, 赛道, 上次分析时间, 催化剂摘要, 评级, 一句话摘要, 发布状态, 侦察次数
        """
        records = self._read_tab("投研记录")
        
        # 搜索过滤
        if query:
            q = query.lower()
            records = [
                r for r in records
                if q in r.get("项目名", "").lower()
                or q in r.get("赛道", "").lower()
                or q in r.get("Twitter", "").lower()
                or q in r.get("催化剂摘要", "").lower()
            ]
        
        # 按上次分析时间倒序（最新的在前）
        records.sort(key=lambda r: r.get("上次分析时间", ""), reverse=True)
        
        result = []
        for i, r in enumerate(records):
            result.append({
                "id": str(i + 1),
                "name": r.get("项目名", ""),
                "twitter": r.get("Twitter", ""),
                "category": r.get("赛道", ""),
                "last_analyzed": r.get("上次分析时间", ""),
                "catalyst": r.get("催化剂摘要", ""),
                "rating": r.get("评级", ""),
                "summary": r.get("一句话摘要", ""),
                "status": r.get("发布状态", ""),
                "scout_count": r.get("侦察次数", 0),
            })
        return result
    
    def refresh(self, tab_name: Optional[str] = None):
        """清除缓存"""
        if tab_name:
            self._cache.pop(tab_name, None)
        else:
            self._cache.clear()
        logger.info(f"[DataService] 缓存已清除 {'(' + tab_name + ')' if tab_name else '(全部)'}")


# Singleton
data_service = DataService()
