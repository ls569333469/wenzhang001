"""
P11 数据清洗管理 API
====================
提供数据清洗前端管理接口。
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import os
import json
import asyncio
from datetime import datetime

router = APIRouter(prefix="/cleaner", tags=["cleaner"])

# ==========================================
# 数据模型
# ==========================================

class CleanerStats(BaseModel):
    """数据库统计"""
    style_count: int
    knowledge_count: int
    pending_files: int

class SourceDirectory(BaseModel):
    """源目录"""
    name: str
    path: str
    file_count: int
    children: List['SourceDirectory'] = []

class CleanerJobRequest(BaseModel):
    """清洗任务请求"""
    input_path: str
    target: str = "knowledge"  # knowledge / style
    mode: str = "auto"  # auto / json / txt
    provider: str = "deepseek"

class CleanerJob(BaseModel):
    """清洗任务"""
    id: str
    status: str  # pending / running / completed / failed
    input_path: str
    target: str
    progress: float
    processed: int
    uploaded: int
    created_at: str
    error: Optional[str] = None

# 全局任务存储
_jobs: Dict[str, CleanerJob] = {}

# ==========================================
# API 端点
# ==========================================

@router.get("/stats", response_model=CleanerStats)
async def get_stats():
    """获取数据库统计"""
    try:
        from app.core.lark_client import lark_client
        
        app_token = os.getenv("LARK_BASE_TOKEN")
        style_id = os.getenv("LARK_TABLE_ID")
        knowledge_id = os.getenv("LARK_KNOWLEDGE_TABLE_ID")
        
        style_resp = lark_client.list_records(app_token, style_id, page_size=1)
        knowledge_resp = lark_client.list_records(app_token, knowledge_id, page_size=1)
        
        style_count = style_resp.get('data', {}).get('total', 0)
        knowledge_count = knowledge_resp.get('data', {}).get('total', 0)
        
        # 统计待处理文件
        data_dir = Path(__file__).parent.parent / "data"
        pending = sum(1 for _ in data_dir.glob("**/*.json")) + sum(1 for _ in data_dir.glob("**/*.txt"))
        
        return CleanerStats(
            style_count=style_count,
            knowledge_count=knowledge_count,
            pending_files=pending
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def get_sources():
    """获取源目录树"""
    data_dir = Path(__file__).parent.parent / "data"
    
    def scan_directory(path: Path, max_depth: int = 2, current_depth: int = 0) -> Dict:
        if current_depth >= max_depth:
            return None
        
        children = []
        file_count = 0
        
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    child = scan_directory(item, max_depth, current_depth + 1)
                    if child:
                        children.append(child)
                elif item.suffix.lower() in ['.json', '.txt', '.md']:
                    file_count += 1
        except PermissionError:
            pass
        
        return {
            "name": path.name,
            "path": str(path.relative_to(data_dir.parent)),
            "file_count": file_count,
            "children": children
        }
    
    result = scan_directory(data_dir)
    return {"sources": result.get("children", []) if result else []}

@router.get("/jobs")
async def list_jobs():
    """获取任务列表"""
    return {"jobs": list(_jobs.values())}

@router.post("/jobs")
async def create_job(request: CleanerJobRequest, background_tasks: BackgroundTasks):
    """创建清洗任务"""
    job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    job = CleanerJob(
        id=job_id,
        status="pending",
        input_path=request.input_path,
        target=request.target,
        progress=0,
        processed=0,
        uploaded=0,
        created_at=datetime.now().isoformat()
    )
    
    _jobs[job_id] = job
    
    # 后台运行任务
    background_tasks.add_task(run_cleaner_job, job_id, request)
    
    return {"job_id": job_id, "status": "created"}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """获取任务详情"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]

@router.get("/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """SSE 流式进度"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def generate():
        while True:
            job = _jobs.get(job_id)
            if not job:
                break
            
            data = job.dict()
            yield f"data: {json.dumps(data)}\n\n"
            
            if job.status in ["completed", "failed"]:
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """取消任务"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    _jobs[job_id].status = "cancelled"
    return {"status": "cancelled"}

# ==========================================
# 后台任务
# ==========================================

async def run_cleaner_job(job_id: str, request: CleanerJobRequest):
    """运行清洗任务"""
    job = _jobs.get(job_id)
    if not job:
        return
    
    try:
        job.status = "running"
        
        # 调用 unified_importer
        from tools.unified_importer import _import_async
        
        # 这里简化处理，实际应该集成进度回调
        await _import_async(
            input_path=request.input_path,
            target=request.target,
            provider=request.provider,
            dry_run=False
        )
        
        job.status = "completed"
        job.progress = 100
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
