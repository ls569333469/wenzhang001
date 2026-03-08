"""
币安广场发布 API 服务
P34: 通过 X-Square-OpenAPI-Key 发布到币安广场

限制:
    - 纯文本，≤ 900 字
    - 每天 100 次发布
    - 与交易/提款隔离
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 币安广场 API 端点
BINANCE_SQUARE_API_URL = "https://www.binance.com/bapi/square/v1/openapi/square/post/create"


async def publish_to_square(
    content: str,
    api_key: Optional[str] = None,
) -> dict:
    """
    发布内容到币安广场

    Args:
        content: 帖子文本 (≤ 900 字)
        api_key: X-Square-OpenAPI-Key

    Returns:
        {"success": bool, "post_url": str, "error": str}
    """
    if not api_key:
        api_key = os.environ.get("BINANCE_SQUARE_API_KEY", "")

    if not api_key:
        return {"success": False, "error": "未配置币安广场 API Key"}

    if len(content) > 900:
        return {"success": False, "error": f"内容超过 900 字限制 (当前 {len(content)} 字)"}

    if not content.strip():
        return {"success": False, "error": "内容不能为空"}

    try:
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BINANCE_SQUARE_API_URL,
                headers={
                    "X-Square-OpenAPI-Key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "content": content,
                }
            )

            result = response.json()

            if response.status_code == 200 and result.get("success"):
                post_url = result.get("data", {}).get("postUrl", "")
                logger.info(f"[BinanceSquare] ✅ 发布成功: {post_url}")
                return {
                    "success": True,
                    "post_url": post_url,
                    "data": result.get("data", {}),
                }
            else:
                error_msg = result.get("message", f"HTTP {response.status_code}")
                logger.error(f"[BinanceSquare] ❌ 发布失败: {error_msg}")
                return {"success": False, "error": error_msg}

    except Exception as e:
        logger.error(f"[BinanceSquare] ❌ 网络错误: {e}")
        return {"success": False, "error": f"网络错误: {str(e)}"}
