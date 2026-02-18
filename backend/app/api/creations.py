"""
P27 创作保存 API
================
提供创作的保存、列表、详情、删除接口。
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/creations", tags=["creations"])


# ==========================================
# 数据模型
# ==========================================

class SaveCreationRequest(BaseModel):
    """保存创作请求"""
    title: str = "无标题"
    content: str
    mode: str = "unknown"
    input_topic: str = ""
    source_material: Optional[str] = None
    critic_score: int = 0
    critic_verdict: str = ""
    word_count: int = 0


# ==========================================
# API 端点
# ==========================================

@router.post("/save")
async def save_creation(request: SaveCreationRequest):
    """保存创作到本地文件"""
    try:
        from app.services.creation_store import creation_store
        result = creation_store.save(request.model_dump())
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_creations(
    month: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """列出所有创作（带分页）"""
    try:
        from app.services.creation_store import creation_store
        return creation_store.list_all(month=month, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{creation_id}")
async def get_creation(creation_id: str):
    """获取单条创作详情"""
    try:
        from app.services.creation_store import creation_store
        result = creation_store.get(creation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Creation not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{creation_id}")
async def delete_creation(creation_id: str):
    """删除创作"""
    try:
        from app.services.creation_store import creation_store
        ok = creation_store.delete(creation_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Creation not found")
        return {"status": "ok", "deleted": creation_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
