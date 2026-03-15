# P28: Google Sheets Data Source for Quantum Studio
# 唯一数据源 — 所有风格样本和知识库数据

import os
import random
from typing import List, Dict, Optional
from pathlib import Path
from app.core.config import get_logger

logger = get_logger("google_sheets")

# Lazy import to avoid startup errors if gspread not installed
gspread = None
Credentials = None

def _ensure_gspread():
    """Lazy load gspread and google-auth"""
    global gspread, Credentials
    if gspread is None:
        import gspread as gs
        from google.oauth2.service_account import Credentials as Creds
        gspread = gs
        Credentials = Creds


class GoogleSheetsDataSource:
    """
    Google Sheets data source for sample retrieval.
    Supports single-sheet mode with filter by 风格标签 column.
    """
    
    # Sheets + Drive readonly: Drive scope needed for open() by name
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.readonly',
    ]
    
    # 字段映射：中文列名 → 内部键名
    FIELD_MAPPING = {
        "内容": "content",
        "博主": "author",
        "风格标签": "style",
        "片段类型": "snippet_type",
        "情绪": "emotional_valence",
        "逻辑公式": "logic_pattern",
        "质量评分": "quality_score",
        "状态": "status"
    }
    
    def __init__(self):
        self._cache: Dict[str, List[Dict]] = {}
        self._initialized = False
        self._spreadsheet = None
        self._sheet_name = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "mimeng")  # Default sheet
        
    def _init_client(self):
        """Initialize Google Sheets client lazily"""
        if self._initialized:
            return True
            
        try:
            _ensure_gspread()
            
            creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "config/google_service_account.json")
            spreadsheet_name = os.getenv("GOOGLE_SHEETS_SPREADSHEET", "Quantum_Samples")
            
            # Check if credentials file exists
            if not Path(creds_path).exists():
                logger.info(f"[GoogleSheets] Credentials file not found: {creds_path}")
                return False
            
            logger.info(f"[GoogleSheets] Loading credentials from {creds_path}")
            logger.info(f"[GoogleSheets] Using scopes: {self.SCOPES}")
            
            creds = Credentials.from_service_account_file(creds_path, scopes=self.SCOPES)
            gc = gspread.authorize(creds)
            logger.info(f"[GoogleSheets] Spreadsheet ID: '{spreadsheet_name}', Length: {len(spreadsheet_name)}")
            
            # Use open_by_key to avoid Drive API requirement
            # If spreadsheet_name looks like an ID (44 chars), use it directly
            if len(spreadsheet_name) > 40 and '/' not in spreadsheet_name:
                logger.info("[GoogleSheets] Opening by key...")
                self._spreadsheet = gc.open_by_key(spreadsheet_name)
            else:
                logger.info("[GoogleSheets] Opening by name (Requires Drive API)...")
                self._spreadsheet = gc.open(spreadsheet_name)
            self._initialized = True
            logger.info(f"[GoogleSheets] Connected to spreadsheet")
            return True
            
        except Exception as e:
            logger.error(f"[GoogleSheets] Init failed: {e}")
            return False
    
    def _map_fields(self, record: Dict) -> Dict:
        """Map Chinese field names to internal keys"""
        mapped = {}
        for ch_key, val in record.items():
            if ch_key in self.FIELD_MAPPING:
                mapped[self.FIELD_MAPPING[ch_key]] = val
            else:
                mapped[ch_key] = val  # Keep unmapped fields
        return mapped
    
    def _load_sheet_data(self, sheet_name: str) -> List[Dict]:
        """Load all records from a sheet"""
        if not self._init_client():
            return []
            
        try:
            worksheet = self._spreadsheet.worksheet(sheet_name)
            records = worksheet.get_all_records()
            # Map field names
            mapped_records = [self._map_fields(r) for r in records]
            logger.info(f"[GoogleSheets] Loaded {len(mapped_records)} records from sheet: {sheet_name}")
            return mapped_records
        except Exception as e:
            logger.error(f"[GoogleSheets] Failed to load sheet {sheet_name}: {e}")
            return []
    
    def get_samples(self, style: str, emotion: str = None, count: int = 3) -> List[Dict]:
        """
        Get random samples matching the style.
        Each style has its own worksheet (mimeng, banfo, etc.)
        """
        # P28: 统一使用中文 Tab 名，方便在 Google Sheets 中维护
        STYLE_TAB_MAP = {
            "mimeng": "风格_咪蒙",
            "banfo": "风格_半佛",
            "insider": "风格_圈内人",
            "xinshixiang": "风格_新世相",
        }
        sheet_name = STYLE_TAB_MAP.get(style.lower(), f"风格_{style}")
        
        # Load data if not cached
        if sheet_name not in self._cache:
            self._cache[sheet_name] = self._load_sheet_data(sheet_name)
        
        all_records = self._cache.get(sheet_name, [])
        if not all_records:
            logger.info(f"[GoogleSheets] No records found in sheet: {sheet_name}")
            return []
        
        # P29 fix: 工作表本身已按风格划分（风格_半佛 = banfo），
        # 表内的 style 列是"逻辑/对比"等风格标签，不是 style identifier，
        # 直接使用工作表内所有记录
        style_matches = all_records
        
        # Filter out PS content (same as SyncService)
        def is_not_ps_content(item):
            content = item.get("content", "")
            if content.strip().startswith("PS") or content.strip().startswith("再PS"):
                return False
            return True
        
        style_matches = [item for item in style_matches if is_not_ps_content(item)]
        
        if not style_matches:
            logger.info(f"[GoogleSheets] No samples found for style: {style}")
            return []
        
        # Filter by emotion if provided
        if emotion:
            emotion_matches = [
                item for item in style_matches
                if item.get("emotional_valence", "").lower() == emotion.lower()
            ]
            if len(emotion_matches) >= count:
                return random.sample(emotion_matches, count)
            elif emotion_matches:
                remaining = count - len(emotion_matches)
                others = [x for x in style_matches if x not in emotion_matches]
                return emotion_matches + random.sample(others, min(len(others), remaining))
        
        return random.sample(style_matches, min(len(style_matches), count))
    
    def get_pattern_menu(self, style: str) -> List[str]:
        """
        P29: 提取当前风格下所有 logic_pattern，按频次排序返回前15个。
        供策略师从中选择写作公式。
        """
        from collections import Counter
        
        STYLE_TAB_MAP = {
            "mimeng": "风格_咪蒙",
            "banfo": "风格_半佛",
            "insider": "风格_圈内人",
            "xinshixiang": "风格_新世相",
        }
        sheet_name = STYLE_TAB_MAP.get(style.lower(), f"风格_{style}")
        
        if sheet_name not in self._cache:
            self._cache[sheet_name] = self._load_sheet_data(sheet_name)
        
        all_records = self._cache.get(sheet_name, [])
        if not all_records:
            return []
        
        # 统计 logic_pattern 频次
        patterns = [r.get("logic_pattern", "") for r in all_records]
        patterns = [p for p in patterns if p]  # 过滤空值
        counter = Counter(patterns)
        
        # 按频次降序，返回前15个
        top_patterns = [p for p, _ in counter.most_common(15)]
        logger.info(f"[GoogleSheets] Pattern menu for {style}: {len(top_patterns)} patterns")
        return top_patterns
    
    def get_targeted_samples(self, style: str, snippet_type: str = None, 
                             logic_pattern: str = None, count: int = 2) -> List[Dict]:
        """
        P29 Phase 2: 按 snippet_type + logic_pattern 精准筛选样本。
        优先精准匹配，匹配不足时放宽条件。
        """
        STYLE_TAB_MAP = {
            "mimeng": "风格_咪蒙",
            "banfo": "风格_半佛",
            "insider": "风格_圈内人",
            "xinshixiang": "风格_新世相",
        }
        sheet_name = STYLE_TAB_MAP.get(style.lower(), f"风格_{style}")
        
        if sheet_name not in self._cache:
            self._cache[sheet_name] = self._load_sheet_data(sheet_name)
        
        all_records = self._cache.get(sheet_name, [])
        if not all_records:
            return []
        
        # 过滤 PS 内容
        records = [r for r in all_records if not r.get("content", "").strip().startswith(("PS", "再PS"))]
        
        # Step 1: 双条件精准匹配
        if snippet_type and logic_pattern:
            exact = [r for r in records 
                     if r.get("snippet_type") == snippet_type 
                     and r.get("logic_pattern") == logic_pattern]
            if len(exact) >= count:
                return random.sample(exact, count)
        
        # Step 2: 退而求其次 — 只按 snippet_type
        if snippet_type:
            by_type = [r for r in records if r.get("snippet_type") == snippet_type]
            if len(by_type) >= count:
                return random.sample(by_type, count)
            elif by_type:
                return by_type[:count]
        
        # Step 3: 退而求其次 — 只按 logic_pattern
        if logic_pattern:
            by_pattern = [r for r in records if r.get("logic_pattern") == logic_pattern]
            if len(by_pattern) >= count:
                return random.sample(by_pattern, count)
            elif by_pattern:
                return by_pattern[:count]
        
        # Step 4: 兜底 — random
        return random.sample(records, min(len(records), count))

    def get_semantic_samples(self, query_text: str, style: str, 
                             snippet_type: str = None, logic_pattern: str = None, 
                             count: int = 2) -> List[Dict]:
        """
        P34: 语义匹配风格样本 — Chroma 优先，回退到 get_targeted_samples。
        
        Args:
            query_text: 素材内容 (用于语义搜索)
            style: 风格 (如 "banfo", "mimeng")
            snippet_type: 片段类型
            logic_pattern: 逻辑公式
            count: 返回数量
        
        Returns:
            [{"content": "...", "metadata": {...}, ...}]
        """
        try:
            from .chroma_service import get_chroma_service
            chroma = get_chroma_service()
            
            results = chroma.get_semantic_samples(
                query_text=query_text,
                n_results=count,
                style_filter=style,
                logic_pattern=logic_pattern,
            )
            
            if results:
                logger.info(f"[GoogleSheets] P34: Chroma 语义匹配 {len(results)} 条 (style={style})")
                return results
            else:
                logger.info("[GoogleSheets] P34: Chroma 无匹配结果, 回退到标签匹配")
        except Exception as e:
            logger.warning(f"[GoogleSheets] P34: Chroma 不可用, 回退到标签匹配: {e}")
        
        # 回退到现有的标签匹配
        return self.get_targeted_samples(style, snippet_type, logic_pattern, count)
    
    def refresh_cache(self, sheet_name: str = None):
        """Clear cache to force reload"""
        if sheet_name:
            self._cache.pop(sheet_name, None)
        else:
            self._cache.clear()
        logger.info("[GoogleSheets] Cache cleared")
    
    def is_available(self) -> bool:
        """Check if Google Sheets is configured and accessible"""
        return self._init_client()


# Singleton instance
google_sheets_source = GoogleSheetsDataSource()
