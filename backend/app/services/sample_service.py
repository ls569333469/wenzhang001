# P28: Sample Service — Google Sheets Only
# 数据源统一为 Google Sheets，移除 Lark/A/B 测试逻辑

from typing import List, Dict
from app.core.config import get_logger

logger = get_logger("services.sample")


class SampleService:
    """
    统一样本检索服务 — 直接从 Google Sheets 获取样本。
    """
    
    def __init__(self):
        self._google_source = None
        
    def _get_google_source(self):
        """Lazy load Google Sheets source"""
        if self._google_source is None:
            try:
                from app.services.google_sheets_source import google_sheets_source
                self._google_source = google_sheets_source
            except Exception as e:
                logger.warning(f"[SampleService] Failed to load Google Sheets source: {e}")
                self._google_source = False  # Mark as unavailable
        return self._google_source if self._google_source else None
    
    def get_samples(self, style: str, emotion: str = None, count: int = 3) -> List[Dict]:
        """
        从 Google Sheets 获取样本。
        """
        gs = self._get_google_source()
        if gs and gs.is_available():
            samples = gs.get_samples(style, emotion, count)
            logger.info(f"[SampleService] Source: google_sheets, Style: {style}, Count: {len(samples)}")
            return samples
        
        logger.warning(f"[SampleService] Google Sheets unavailable, no samples for {style}")
        return []


# Singleton instance
sample_service = SampleService()
