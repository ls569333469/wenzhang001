
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from app.core.lark_client import lark_client
from app.core.config import get_logger
import os

logger = get_logger("services.sync")

# Mapping from Lark Chinese field names to Internal keys
# P12.3 更新: 添加实际 Lark 表格字段名映射 (博主、片段类型、风格标签、质量评分)
FIELD_MAPPING = {
    "内容": "content",
    "Content": "content",
    # 博主 (Lark 实际字段名) 和 作者 (兼容)
    "博主": "author",
    "作者": "author",
    "Author": "author",
    # 风格标签 (Lark 实际字段名) 和 风格 (兼容)
    "风格标签": "style",
    "风格": "style",
    "Style": "style",
    # 片段类型 (Lark 实际字段名) 和 类型 (兼容)
    "片段类型": "snippet_type",
    "类型": "snippet_type",
    "Type": "snippet_type",
    # 情绪
    "情绪": "emotional_valence",
    "Emotion": "emotional_valence",
    # 逻辑公式
    "逻辑公式": "logic_pattern",
    "Logic Pattern": "logic_pattern",
    # 质量评分 (Lark 实际字段名) 和 质量分 (兼容)
    "质量评分": "quality_score",
    "质量分": "quality_score",
    "Quality Score": "quality_score",
    # 状态
    "状态": "status",
    "Status": "status"
}

# The target file for material storage
DATA_DIR = Path(__file__).parent.parent.parent / "data"
STYLE_LIBRARY_FILE = DATA_DIR / "style_library.json"

class SyncService:
    def __init__(self):
        self.base_token = os.getenv("LARK_BASE_TOKEN")
        self.table_id = os.getenv("LARK_TABLE_ID")
        self.lark = lark_client
        
    def _ensure_data_dir(self):
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            
    def load_library(self) -> List[Dict]:
        self._ensure_data_dir()
        if not STYLE_LIBRARY_FILE.exists():
            return []
        try:
            with open(STYLE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def save_library(self, items: List[Dict]):
        self._ensure_data_dir()
        with open(STYLE_LIBRARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    def sync_from_lark(self) -> Dict[str, Any]:
        """
        Main Sync Logic:
        1. Fetch records from Lark with Status='Pending' (or '待处理')
        2. Clean and Map fields
        3. Append to local JSON
        4. Update Lark record status to 'Synced' ('已同步')
        """
        logger.info("Starting Lark Sync...")
        
        if not self.base_token or not self.table_id:
            return {"status": "error", "message": "Missing Lark Base Config"}

        # 1. Fetch pending records
        # Note: Bitable API filtering syntax is complex. 
        # For simplicity, we fetch page by page and filter in memory, 
        # or we could use filter string if we are confident about the syntax.
        # Let's try listing all (assuming pending queue isn't huge) and filtering in memory first for robustness.
        
        try:
            resp = self.lark.list_records(self.base_token, self.table_id, page_size=100)
            if resp.get("code") != 0:
                raise Exception(f"Lark API Error: {resp}")
                
            all_records = resp.get("data", {}).get("items", [])
            logger.info(f"Fetched {len(all_records)} records total from Lark.")
            
        except Exception as e:
            logger.error(f"Sync failed during fetch: {e}")
            return {"status": "error", "message": str(e)}

        synced_count = 0
        new_items = []
        
        # Load existing library to avoid duplicates (optional, based on content hash?)
        # For now, we trust the 'Status' field.
        current_library = self.load_library()
        
        records_to_update = []

        for record in all_records:
            fields = record.get("fields", {})
            record_id = record.get("record_id")
            
            # Detect Status Key (could be "状态" or "Status")
            status_val = fields.get("状态") or fields.get("Status")
            
            # Check if pending
            if status_val in ["待处理", "Pending", "待同步"]:
                # Map fields
                clean_item = {}
                for ch_key, val in fields.items():
                    if ch_key in FIELD_MAPPING:
                        clean_item[FIELD_MAPPING[ch_key]] = val
                
                # Default ID
                clean_item["id"] = record_id
                
                # Check completeness
                if "content" in clean_item and "style" in clean_item:
                    new_items.append(clean_item)
                    records_to_update.append(record_id)
                else:
                    logger.warning(f"Skipping incomplete record {record_id}: {fields}")

        # 2. Update Local Library
        if new_items:
            logger.info(f"Found {len(new_items)} new items to sync.")
            current_library.extend(new_items)
            self.save_library(current_library)
            
            # 3. Update Lark Status
            for rid in records_to_update:
                try:
                    # Update status to '已同步' (Synced)
                    # We try both keys to be safe, or just the one that existed? 
                    # Let's just update '状态' if exists, 'Status' if exists.
                    # Simplest: Update '状态' to '已同步'
                    self.lark.update_record(self.base_token, self.table_id, rid, {"状态": "已同步"})
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Failed to update status for {rid}: {e}")
        
        return {
            "status": "success", 
            "synced_count": synced_count, 
            "total_library_size": len(current_library),
            "new_items": new_items  # Return the actual new items for workflow processing
        }

    def get_samples(self, style: str, emotion: str = None, count: int = 3) -> List[Dict]:
        """
        Retrieve 'count' samples matching the style (and optional emotion/emotional_valence).
        If matching emotion not found, falls back to style only.
        
        P12 Update: Now uses 'emotional_valence' field internally, but accepts 'emotion' param for backward compatibility.
        Returns samples with logic_pattern for enhanced Few-Shot prompting.
        """
        library = self.load_library()
        if not library:
            return []
            
        import random
        
        # Filter by style (case-insensitive)
        style_matches = [
            item for item in library 
            if item.get("style", "").lower() == style.lower()
        ]
        
        # P12.1 优化: 过滤 PS 内容 (通常是广告/闲聊)
        # 排除内容中包含 "PS:" 或以 "PS" 开头的素材
        def is_not_ps_content(item):
            content = item.get("content", "")
            if content.strip().startswith("PS") or content.strip().startswith("再PS"):
                return False
            return True
        
        style_matches = [item for item in style_matches if is_not_ps_content(item)]
        
        if not style_matches:
            logger.warning(f"No samples found for style: {style}")
            return []
            
        # Filter by emotion/emotional_valence if provided
        # P12: Support both old 'emotion' and new 'emotional_valence' field names
        if emotion:
            emotion_matches = [
                item for item in style_matches 
                if (item.get("emotional_valence", "") or item.get("emotion", "")).lower() == emotion.lower()
            ]
            if len(emotion_matches) >= count:
                return random.sample(emotion_matches, count)
            elif emotion_matches:
                # If not enough emotion matches, mix with style matches
                remaining = count - len(emotion_matches)
                others = [x for x in style_matches if x not in emotion_matches]
                return emotion_matches + random.sample(others, min(len(others), remaining))
        
        # If no emotion filter or not enough matches, return random style matches
        return random.sample(style_matches, min(len(style_matches), count))

sync_service = SyncService()
