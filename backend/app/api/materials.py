"""
P23 素材中心 API
================
提供素材的列表、抓取、分析接口。
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

router = APIRouter(prefix="/materials", tags=["materials"])


# ==========================================
# 数据模型
# ==========================================

class MaterialItem(BaseModel):
    """素材项"""
    fetch_date: str = ""
    published_at: str = ""
    timeliness: str = ""
    source: str = ""
    content_type: str = ""
    title: str = ""
    url: str = ""
    content: str = ""
    summary: str = ""
    quality_score: int = 0
    score_reason: str = ""
    fact_type: str = ""
    keywords: List[str] = []
    entities: List[str] = []
    suggested_modes: List[str] = []
    fingerprint: str = ""
    status: str = ""


class FetchRequest(BaseModel):
    """抓取请求"""
    source: str = "chaincatcher"
    count: int = 10
    analyze: bool = True
    analyze_count: int = 5


class FetchJob(BaseModel):
    """抓取任务"""
    id: str
    status: str  # pending / running / completed / failed
    source: str
    total_fetched: int = 0
    total_analyzed: int = 0
    total_written: int = 0
    error: Optional[str] = None


# 全局任务存储
_fetch_jobs: Dict[str, FetchJob] = {}


# ==========================================
# API 端点
# ==========================================

@router.get("/list")
async def list_materials(
    date: Optional[str] = None,
    source: Optional[str] = None,
    min_score: int = 0,
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    timeliness: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """获取素材列表（带筛选 + 分页）"""
    try:
        from app.services.material_sheet import material_sheet
        all_items = material_sheet.list_materials(
            date=date,
            source=source,
            min_score=min_score,
            content_type=content_type,
            status=status,
            timeliness=timeliness,
        )

        # Pagination
        total = len(all_items)
        start = (page - 1) * page_size
        end = start + page_size
        items = all_items[start:end]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_material_stats():
    """获取素材统计"""
    try:
        from app.services.material_sheet import material_sheet
        items = material_sheet.list_materials()

        total = len(items)
        if total == 0:
            return {
                "total": 0,
                "by_source": {},
                "by_type": {},
                "by_status": {},
                "score_avg": 0,
                "fresh_count": 0,
            }

        by_source = {}
        by_type = {}
        by_status = {}
        scores = []
        fresh = 0

        for item in items:
            src = item.get("source", "未知")
            by_source[src] = by_source.get(src, 0) + 1

            ct = item.get("content_type", "未知")
            by_type[ct] = by_type.get(ct, 0) + 1

            st = item.get("status", "未知")
            by_status[st] = by_status.get(st, 0) + 1

            score = item.get("quality_score", 0)
            if score:
                scores.append(score)

            if item.get("timeliness") == "fresh":
                fresh += 1

        return {
            "total": total,
            "by_source": by_source,
            "by_type": by_type,
            "by_status": by_status,
            "score_avg": round(sum(scores) / len(scores), 1) if scores else 0,
            "fresh_count": fresh,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch")
async def start_fetch(request: FetchRequest, background_tasks: BackgroundTasks):
    """启动素材抓取任务"""
    job_id = f"fetch_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    job = FetchJob(
        id=job_id,
        status="pending",
        source=request.source,
    )
    _fetch_jobs[job_id] = job

    background_tasks.add_task(
        _run_fetch_job, job_id, request
    )

    return {"job_id": job_id, "status": "created"}


@router.get("/fetch/{job_id}")
async def get_fetch_status(job_id: str):
    """获取抓取任务状态"""
    if job_id not in _fetch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _fetch_jobs[job_id]


@router.post("/mark-used")
async def mark_material_used(url: str):
    """标记素材已使用"""
    try:
        from app.services.material_sheet import material_sheet
        ok = material_sheet.mark_used(url)
        if ok:
            return {"status": "ok"}
        return {"status": "not_found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 后台任务
# ==========================================

async def _run_fetch_job(job_id: str, request: FetchRequest):
    """后台运行抓取任务"""
    job = _fetch_jobs.get(job_id)
    if not job:
        return

    try:
        job.status = "running"

        # Run in thread to avoid blocking
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await asyncio.get_event_loop().run_in_executor(
                pool, _sync_fetch_pipeline, request
            )

        job.total_fetched = result.get("fetched", 0)
        job.total_analyzed = result.get("analyzed", 0)
        job.total_written = result.get("written", 0)
        job.status = "completed"

    except Exception as e:
        job.status = "failed"
        job.error = str(e)


def _sync_fetch_pipeline(request: FetchRequest) -> dict:
    """同步执行抓取管线"""
    from app.services.material_fetcher import get_fetcher
    from app.services.material_analyzer import analyze_batch
    from app.services.material_sheet import material_sheet

    # 1. Fetch
    fetcher = get_fetcher(request.source)
    materials = fetcher.fetch_latest(count=request.count)

    # Enrich with details
    materials = fetcher.enrich_with_details(materials, max_items=request.count)

    result = {"fetched": len(materials)}

    if not materials:
        return result

    # 2. Analyze (if enabled)
    if request.analyze:
        analyzed = analyze_batch(materials[:request.analyze_count])
        # Append un-analyzed items
        if request.analyze_count < len(materials):
            analyzed.extend(materials[request.analyze_count:])
        materials = analyzed
        result["analyzed"] = len(analyzed)

    # 3. Dedup + Write
    existing = material_sheet.get_existing_urls()
    new_materials = [m for m in materials if m.get("url") not in existing]

    if new_materials:
        written = material_sheet.write_materials(new_materials)
        result["written"] = written
    else:
        result["written"] = 0

    return result
