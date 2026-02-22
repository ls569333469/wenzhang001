# P28: Google Sheets Data Source for Quantum Studio
# 唯一数据源 — 所有风格样本和知识库数据

import os
import random
from typing import List, Dict, Optional
from pathlib import Path

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
    
    # Only Sheets scope - Drive API is not enabled in the project
    # IMPORTANT: Always use open_by_key() with spreadsheet ID, not open() with name
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
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
                print(f"[GoogleSheets] Credentials file not found: {creds_path}")
                return False
            
            print(f"[GoogleSheets] Loading credentials from {creds_path}")
            print(f"[GoogleSheets] Using scopes: {self.SCOPES}")
            
            creds = Credentials.from_service_account_file(creds_path, scopes=self.SCOPES)
            gc = gspread.authorize(creds)
            print(f"[GoogleSheets] Spreadsheet ID: '{spreadsheet_name}', Length: {len(spreadsheet_name)}")
            
            # Use open_by_key to avoid Drive API requirement
            # If spreadsheet_name looks like an ID (44 chars), use it directly
            if len(spreadsheet_name) > 40 and '/' not in spreadsheet_name:
                print("[GoogleSheets] Opening by key...")
                self._spreadsheet = gc.open_by_key(spreadsheet_name)
            else:
                print("[GoogleSheets] Opening by name (Requires Drive API)...")
                self._spreadsheet = gc.open(spreadsheet_name)
            self._initialized = True
            print(f"[GoogleSheets] Connected to spreadsheet")
            return True
            
        except Exception as e:
            print(f"[GoogleSheets] Init failed: {e}")
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
            print(f"[GoogleSheets] Loaded {len(mapped_records)} records from sheet: {sheet_name}")
            return mapped_records
        except Exception as e:
            print(f"[GoogleSheets] Failed to load sheet {sheet_name}: {e}")
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
            print(f"[GoogleSheets] No records found in sheet: {sheet_name}")
            return []
        
        # Filter by style (case-insensitive) - 兼容表内有 style 列的情况
        # Fallback: if style field is empty, verify if sheet name matches the requested style
        # Filter by style - 工作表本身已按风格划分
        # 如果表内有 style 列则过滤，否则直接使用所有记录
        style_matches = []
        for item in all_records:
            item_style = item.get("style", "")
            if item_style and item_style.lower() == style.lower():
                style_matches.append(item)
            elif not item_style:
                # 工作表名称即风格，直接添加
                style_matches.append(item)
        
        # Filter out PS content (same as SyncService)
        def is_not_ps_content(item):
            content = item.get("content", "")
            if content.strip().startswith("PS") or content.strip().startswith("再PS"):
                return False
            return True
        
        style_matches = [item for item in style_matches if is_not_ps_content(item)]
        
        if not style_matches:
            print(f"[GoogleSheets] No samples found for style: {style}")
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
    
    def refresh_cache(self, sheet_name: str = None):
        """Clear cache to force reload"""
        if sheet_name:
            self._cache.pop(sheet_name, None)
        else:
            self._cache.clear()
        print("[GoogleSheets] Cache cleared")
    
    def is_available(self) -> bool:
        """Check if Google Sheets is configured and accessible"""
        return self._init_client()


# Singleton instance
google_sheets_source = GoogleSheetsDataSource()
