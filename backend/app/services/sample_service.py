# Sample Service - A/B Test Wrapper for Multiple Data Sources
# Supports: Lark (local cache), Google Sheets, or A/B testing between both

import os
import random
from typing import List, Dict, Optional
from app.services.sync_service import sync_service
from app.core.config import get_logger

logger = get_logger("services.sample")


class SampleService:
    """
    Unified sample retrieval service with A/B testing support.
    
    Environment Variables:
        SAMPLE_SOURCE: 'lark', 'google_sheets', or 'ab_test'
        AB_TEST_GOOGLE_RATIO: 0.0-1.0 (default 0.5 for 50% Google Sheets)
    """
    
    def __init__(self):
        self._google_source = None
        self._source_mode = os.getenv("SAMPLE_SOURCE", "lark")  # Default to Lark
        self._ab_ratio = float(os.getenv("AB_TEST_GOOGLE_RATIO", "0.5"))
        
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
        Get samples based on configured data source mode.
        
        Returns:
            List of sample dictionaries with 'content', 'style', etc.
        """
        source_used = "unknown"
        samples = []
        
        if self._source_mode == "google_sheets":
            # Google Sheets only
            gs = self._get_google_source()
            if gs and gs.is_available():
                samples = gs.get_samples(style, emotion, count)
                source_used = "google_sheets"
            else:
                # Fallback to Lark
                samples = sync_service.get_samples(style, emotion, count)
                source_used = "lark (fallback)"
                
        elif self._source_mode == "ab_test":
            # A/B Test: randomly choose source
            use_google = random.random() < self._ab_ratio
            gs = self._get_google_source()
            
            if use_google and gs and gs.is_available():
                samples = gs.get_samples(style, emotion, count)
                source_used = "google_sheets (A/B)"
            else:
                samples = sync_service.get_samples(style, emotion, count)
                source_used = "lark (A/B)"
                
        else:
            # Default: Lark (local cache)
            samples = sync_service.get_samples(style, emotion, count)
            source_used = "lark"
        
        logger.info(f"[SampleService] Source: {source_used}, Style: {style}, Count: {len(samples)}")
        return samples
    
    def set_source_mode(self, mode: str):
        """Dynamically change source mode: 'lark', 'google_sheets', 'ab_test'"""
        if mode in ["lark", "google_sheets", "ab_test"]:
            self._source_mode = mode
            logger.info(f"[SampleService] Source mode changed to: {mode}")
        else:
            logger.warning(f"[SampleService] Invalid mode: {mode}")
    
    def get_source_mode(self) -> str:
        """Get current source mode"""
        return self._source_mode
    
    def set_ab_ratio(self, ratio: float):
        """Set A/B test ratio (0.0-1.0 for Google Sheets probability)"""
        self._ab_ratio = max(0.0, min(1.0, ratio))
        logger.info(f"[SampleService] A/B ratio set to: {self._ab_ratio}")


# Singleton instance
sample_service = SampleService()
