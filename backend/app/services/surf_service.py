"""
P31: Surf AI API 服务
统一封装 Surf API 调用，供投研模块各节点使用

使用方式:
    from app.services.surf_service import SurfService
    surf = SurfService()
    result = surf.call("surf-1.5", system_prompt, user_prompt)
"""
import os
import time
import httpx
from ..core.config import get_logger

logger = get_logger("surf_service")

SURF_API_KEY = os.getenv("SURF_API_KEY", "")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"


class SurfService:
    """Surf AI API 服务封装"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or SURF_API_KEY
        self.base_url = SURF_BASE_URL

    def call(
        self,
        model: str = "surf-1.5",
        system_prompt: str = "",
        user_prompt: str = "",
        abilities: list = None,
        reasoning: str = "medium",
        timeout: int = 300,
    ) -> dict:
        """
        调用 Surf API

        Args:
            model: 模型名称 (surf-1.5 / surf-1.5-instant)
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            abilities: Surf 能力列表 (如 ["search"])
            reasoning: 推理深度 (low/medium/high)
            timeout: 请求超时（秒）

        Returns:
            {status: 200, content: str, usage: dict, elapsed: float}
            或 {status: int|str, error: str, elapsed: float}
        """
        if not self.api_key:
            logger.error("SURF_API_KEY not configured")
            return {"status": "error", "error": "SURF_API_KEY not set", "elapsed": 0}

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "reasoning_effort": reasoning,
            "ability": abilities or ["search"],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start = time.time()
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(self.base_url, headers=headers, json=payload)
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                logger.info(
                    f"Surf API OK: {model}, {elapsed:.1f}s, "
                    f"{usage.get('total_tokens', '?')} tokens"
                )
                return {
                    "status": 200,
                    "content": content,
                    "usage": usage,
                    "elapsed": elapsed,
                }

            logger.warning(f"Surf API {resp.status_code}: {resp.text[:200]}")
            return {
                "status": resp.status_code,
                "error": resp.text[:500],
                "elapsed": elapsed,
            }
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"Surf API error: {e} ({elapsed:.1f}s)")
            return {"status": "error", "error": str(e), "elapsed": elapsed}
