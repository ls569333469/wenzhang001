"""
Material Sheet Service - materials Tab 读写服务
P23 Phase 1c: Google Sheets materials 工作表管理

独立于现有 GoogleSheetsDataSource，专为 materials Tab 服务。
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Set

from dotenv import load_dotenv
from app.core.config import get_logger
load_dotenv()

logger = get_logger("material_sheet")

# Lazy imports
gspread = None
Credentials = None


def _ensure_gspread():
    global gspread, Credentials
    if gspread is None:
        import gspread as gs
        from google.oauth2.service_account import Credentials as Creds
        gspread = gs
        Credentials = Creds


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]

# materials Tab 的 17 列字段
MATERIAL_COLUMNS = [
    "抓取日期",
    "发布时间",
    "时效性",
    "来源",
    "内容类型",
    "标题",
    "URL",
    "正文原文",
    "核心摘要",
    "质量评分",
    "评分理由",
    "事实类型",
    "关键词",
    "项目/人名/代币",
    "推荐模式",
    "内容指纹",
    "状态",
]


class MaterialSheetService:
    """materials 工作表的读写服务"""

    def __init__(self):
        self._worksheet = None
        self._initialized = False
        # P23: TTL cache to avoid repeated Sheets API calls
        self._cache_records = None
        self._cache_time = 0
        self._cache_ttl = 300  # seconds (5 min – material data changes infrequently)

    def _init(self):
        """懒初始化 Sheets 连接"""
        if self._initialized:
            return True

        try:
            _ensure_gspread()
            creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "config/google_service_account.json")
            spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET", "")

            if not os.path.exists(creds_path):
                logger.info(f"[MaterialSheet] Credentials not found: {creds_path}")
                return False

            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            gc = gspread.authorize(creds)

            if len(spreadsheet_id) > 40:
                spreadsheet = gc.open_by_key(spreadsheet_id.strip())
            else:
                spreadsheet = gc.open(spreadsheet_id)

            self._worksheet = spreadsheet.worksheet("materials")
            self._initialized = True
            logger.info("[MaterialSheet] Connected to materials worksheet")
            # Pre-warm cache to avoid cold start delay on first request
            try:
                self._cache_records = self._worksheet.get_all_records()
                self._cache_time = time.time()
                logger.info(f"[MaterialSheet] Cache pre-warmed: {len(self._cache_records)} records")
            except Exception:
                pass
            return True

        except Exception as e:
            logger.error(f"[MaterialSheet] Init failed: {e}")
            return False

    def get_existing_urls(self) -> Set[str]:
        """获取已有 URL，用于去重"""
        if not self._init():
            return set()

        try:
            # URL 在第 7 列 (G列)
            url_col = self._worksheet.col_values(7)
            # Skip header
            return set(url_col[1:]) if len(url_col) > 1 else set()
        except Exception as e:
            logger.error(f"[MaterialSheet] Error reading URLs: {e}")
            return set()

    def write_materials(self, materials: List[Dict]) -> int:
        """
        批量写入素材到 materials Tab

        Args:
            materials: 已分析的素材列表

        Returns:
            写入行数
        """
        if not self._init():
            return 0

        if not materials:
            return 0

        # Convert to rows
        rows = []
        for mat in materials:
            row = [
                datetime.now().strftime("%Y-%m-%d"),           # 抓取日期
                mat.get("published_at", ""),                    # 发布时间
                mat.get("timeliness", "unknown"),               # 时效性
                mat.get("source", ""),                          # 来源
                mat.get("content_type", ""),                    # 内容类型
                mat.get("title", ""),                           # 标题
                mat.get("url", ""),                             # URL
                mat.get("content", "")[:3000],                  # 正文原文 (cap for Sheets cell limit)
                mat.get("summary", ""),                         # 核心摘要
                mat.get("quality_score", 5),                    # 质量评分
                mat.get("score_reason", ""),                    # 评分理由
                mat.get("fact_type", ""),                       # 事实类型
                ", ".join(mat.get("keywords", [])),             # 关键词
                ", ".join(mat.get("entities", [])),             # 项目/人名/代币
                ", ".join(mat.get("suggested_modes", [])),      # 推荐模式
                mat.get("fingerprint", ""),                     # 内容指纹
                mat.get("status", "未使用"),                    # 状态
            ]
            rows.append(row)

        # Batch write — split into chunks of 50 to avoid API limits
        written = 0
        chunk_size = 50

        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            try:
                self._worksheet.append_rows(chunk, value_input_option="RAW")
                written += len(chunk)
                logger.info(f"[MaterialSheet] 写入 {written}/{len(rows)} 行")
            except Exception as e:
                logger.error(f"[MaterialSheet] Write error at chunk {i}: {e}")
                break
        logger.info(f"[MaterialSheet] 写入 {written}/{len(rows)} 行")

        # P23: Invalidate cache after write
        self._cache_records = None
        self._cache_time = 0

        return written

    def list_materials(
        self,
        date: str = None,
        source: str = None,
        min_score: int = 0,
        content_type: str = None,
        status: str = None,
        timeliness: str = None,
    ) -> List[Dict]:
        """读取素材列表（带筛选）"""
        if not self._init():
            return []

        # P23: Use cached records if fresh enough
        now = time.time()
        if self._cache_records is None or (now - self._cache_time) > self._cache_ttl:
            try:
                self._cache_records = self._worksheet.get_all_records()
                self._cache_time = now
                logger.info(f"[MaterialSheet] Cache refreshed: {len(self._cache_records)} records")
            except Exception as e:
                logger.error(f"[MaterialSheet] Read error: {e}")
                return []

        records = self._cache_records

        results = []
        for record in records:
            # Apply filters
            if date and record.get("抓取日期", "") != date:
                continue
            if source and record.get("来源", "") != source:
                continue
            if min_score and int(record.get("质量评分", 0)) < min_score:
                continue
            if content_type and record.get("内容类型", "").strip() != content_type:
                continue
            if status and record.get("状态", "") != status:
                continue
            if timeliness and record.get("时效性", "") != timeliness:
                continue

            # Map to internal format
            results.append({
                "fetch_date": record.get("抓取日期", ""),
                "published_at": record.get("发布时间", ""),
                "timeliness": record.get("时效性", ""),
                "source": record.get("来源", ""),
                "content_type": record.get("内容类型", ""),
                "title": record.get("标题", ""),
                "url": record.get("URL", ""),
                "content": record.get("正文原文", ""),
                "summary": record.get("核心摘要", ""),
                "quality_score": int(record.get("质量评分", 0)),
                "score_reason": record.get("评分理由", ""),
                "fact_type": record.get("事实类型", ""),
                "keywords": record.get("关键词", "").split(", ") if record.get("关键词") else [],
                "entities": record.get("项目/人名/代币", "").split(", ") if record.get("项目/人名/代币") else [],
                "suggested_modes": record.get("推荐模式", "").split(", ") if record.get("推荐模式") else [],
                "fingerprint": record.get("内容指纹", ""),
                "status": record.get("状态", ""),
            })

        # P25: newest first so fresh items appear on page 1
        results.reverse()
        return results

    def mark_used(self, url: str) -> bool:
        """标记素材已使用"""
        if not self._init():
            return False

        try:
            cell = self._worksheet.find(url, in_column=7)
            if cell:
                # 状态列 = 第 17 列 (Q列)
                self._worksheet.update_cell(cell.row, 17, "已创作")
                return True
            return False
        except Exception as e:
            logger.error(f"[MaterialSheet] Mark used error: {e}")
            return False
        finally:
            # P23: Invalidate cache after mark-used
            self._cache_records = None
            self._cache_time = 0


# Singleton
material_sheet = MaterialSheetService()
