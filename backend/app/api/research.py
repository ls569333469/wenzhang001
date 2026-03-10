"""
P31: 投研报告 API
提供投研数据给前端展示 + 日报生成 + 侦察官搜索
"""
import json
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])

# 报告存储目录
RESEARCH_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"


def _find_latest_date() -> Optional[str]:
    """找到最新的报告日期 (YYYYMMDD)，从多种文件类型中发现"""
    dates = set()
    # 从所有可能的文件类型中发现日期
    patterns = [
        ("data_*.json", "data_"),
        ("daily_research_*.md", "daily_research_"),
        ("card_*.html", "card_"),
        ("tweets_*.md", "tweets_"),
        ("scout_*.md", "scout_"),
    ]
    for glob_pattern, prefix in patterns:
        for f in RESEARCH_DIR.glob(glob_pattern):
            date_str = f.stem.replace(prefix, "")
            if len(date_str) == 8 and date_str.isdigit():
                dates.add(date_str)
    return max(dates) if dates else None


def _read_file(path: Path) -> Optional[str]:
    """安全读取文件"""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


@router.get("/latest")
async def get_latest_report(date: Optional[str] = None):
    """获取最新投研报告数据，支持 ?date=YYYYMMDD 指定日期"""
    if not date:
        date = _find_latest_date()
    if not date:
        raise HTTPException(status_code=404, detail="暂无投研报告")

    # 读取 JSON 数据（可选，不是所有日期都有）
    json_path = RESEARCH_DIR / f"data_{date}.json"
    json_data = _read_file(json_path)
    projects = json.loads(json_data) if json_data else {}

    # 读取配图 HTML
    card_html = _read_file(RESEARCH_DIR / f"card_{date}.html")
    card_png_exists = (RESEARCH_DIR / f"card_{date}.png").exists()

    # 读取推文
    tweets_md = _read_file(RESEARCH_DIR / f"tweets_{date}.md")

    # 读取完整报告
    report_md = _read_file(RESEARCH_DIR / f"daily_research_{date}.md")

    # 解析推文为结构化数据
    tweets = []
    if tweets_md:
        import re
        blocks = re.split(r"## (.+?)\n", tweets_md)
        for i in range(1, len(blocks), 2):
            name = blocks[i].strip()
            content = blocks[i + 1] if i + 1 < len(blocks) else ""
            # 移除所有 ``` 标记
            clean = re.sub(r"```\s*", "", content)
            # 移除元数据行（字数统计等）
            clean = re.sub(r"（字数.*?）", "", clean)
            # 移除纯分隔线
            clean = re.sub(r"^---\s*$", "", clean, flags=re.MULTILINE)
            # 清理多余空行
            clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
            if clean:
                tweets.append({
                    "name": name,
                    "text": clean,
                    "char_count": len(clean),
                })

    # 计算项目数量（优先用 JSON，否则从报告正文推断）
    project_count = projects.get("project_count", 0)
    if project_count == 0 and report_md:
        import re
        # 统计 "## 1." "## 2." 等项目标题
        project_count = len(re.findall(r"^## \d+\.", report_md, re.MULTILINE))

    return {
        "date": f"{date[:4]}-{date[4:6]}-{date[6:8]}",
        "date_raw": date,
        "project_count": project_count,
        "projects": projects.get("projects", []),
        "card_html": card_html,
        "card_image_url": f"/api/research/card-image/{date}" if card_png_exists else None,
        "tweets": tweets,
        "report_md": report_md,
    }


@router.get("/card-image/{date}")
async def get_card_image(date: str):
    """提供预渲染的配图 PNG"""
    from fastapi.responses import FileResponse
    png_path = RESEARCH_DIR / f"card_{date}.png"
    if not png_path.exists():
        raise HTTPException(status_code=404, detail="配图 PNG 未找到")
    return FileResponse(str(png_path), media_type="image/png")


@router.post("/regen-card-image/{date}")
async def regen_card_image(date: str):
    """按需重新生成配图 PNG（用 Playwright 截图）"""
    html_path = RESEARCH_DIR / f"card_{date}.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="配图 HTML 未找到")
    html = html_path.read_text(encoding="utf-8")
    png_path = RESEARCH_DIR / f"card_{date}.png"

    from app.services.card_generator import generate_card_image
    generate_card_image(html, str(png_path))
    return {"status": "ok", "path": str(png_path)}


@router.get("/history")
async def get_report_history():
    """列出历史报告"""
    dates = set()
    for f in RESEARCH_DIR.glob("data_*.json"):
        date_str = f.stem.replace("data_", "")
        if len(date_str) == 8 and date_str.isdigit():
            dates.add(date_str)

    history = []
    for d in sorted(dates, reverse=True):
        json_data = _read_file(RESEARCH_DIR / f"data_{d}.json")
        count = 0
        if json_data:
            try:
                count = json.loads(json_data).get("project_count", 0)
            except Exception:
                pass
        history.append({
            "date": f"{d[:4]}-{d[4:6]}-{d[6:8]}",
            "date_raw": d,
            "project_count": count,
            "has_card": (RESEARCH_DIR / f"card_{d}.html").exists(),
            "has_tweets": (RESEARCH_DIR / f"tweets_{d}.md").exists(),
        })

    return {"reports": history}


# ============================================
# P31 Phase 3: Prompt 管理 API
# ============================================
PROMPTS_DIR = Path(__file__).parent.parent.parent / "data" / "prompts" / "research"

# 投研智能体列表（P32-C: 全部注册，P15 可编辑）
RESEARCH_AGENTS = {
    "scout": {"file": "scout.jinja2", "label": "侦察官"},
    "analyst": {"file": "analyst.jinja2", "label": "策略官"},
    "summarizer": {"file": "summarizer.jinja2", "label": "总结官"},
    "reviewer": {"file": "reviewer.jinja2", "label": "质检官"},
    "tweet_digest": {"file": "copywriter/tweet_digest.jinja2", "label": "推文写手"},
    "report": {"file": "copywriter/report.jinja2", "label": "日报模板"},
}


@router.get("/prompts")
async def get_research_prompts():
    """获取所有投研智能体的 Prompt"""
    result = {}
    for key, info in RESEARCH_AGENTS.items():
        path = PROMPTS_DIR / info["file"]
        content = ""
        if path.exists():
            content = path.read_text(encoding="utf-8")
        result[key] = {
            "label": info["label"],
            "content": content,
        }
    return result


class PromptUpdateBody(BaseModel):
    content: str


@router.post("/prompts/{agent_name}")
async def update_research_prompt(agent_name: str, body: PromptUpdateBody):
    """更新指定投研智能体的 Prompt"""
    if agent_name not in RESEARCH_AGENTS:
        raise HTTPException(status_code=404, detail=f"未知智能体: {agent_name}")

    info = RESEARCH_AGENTS[agent_name]
    path = PROMPTS_DIR / info["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.content, encoding="utf-8")
    return {"status": "success", "agent": agent_name}


# ============================================
# P31 v4: 日报生成 + 侦察官独立 API
# ============================================

class DailyReportRequest(BaseModel):
    """日报生成请求"""
    provider: str = "volcengine"
    model_id: Optional[str] = None
    concurrency: int = 3
    selected_projects: Optional[list[str]] = None  # 用户勾选的项目名列表
    scout_projects: Optional[list[dict]] = None     # 前端侦察官结果（避免重复搜索）


@router.post("/daily-report")
async def generate_daily_report(
    request: DailyReportRequest,
    background_tasks: BackgroundTasks,
):
    """
    POST /api/research/daily-report
    生成每日投研快报（侦察官→策略官×N→审核官→写手→润色官）

    前端调用或定时任务调用均可。
    策略官使用 Surf API（固定），审核官/写手/润色官使用 request 中的 provider。
    """
    from ..services.daily_report_service import generate_daily_report as _generate

    api_config = {
        "provider": request.provider,
        "model_id": request.model_id,
    }

    try:
        result = await _generate(
            api_config=api_config,
            concurrency=request.concurrency,
            selected_projects=request.selected_projects,
            scout_projects=request.scout_projects,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== P35: 重新组装日报 =====

@router.get("/available-projects")
async def get_available_projects(date: str = None):
    """
    GET /api/research/available-projects?date=20260309
    返回指定日期已分析的项目列表（供重新组装选择用）
    """
    from ..services.daily_report_service import get_available_projects as _get_projects

    projects = _get_projects(date)
    return {"projects": projects, "count": len(projects)}


class ReassembleRequest(BaseModel):
    selected_twitters: list[str] = []   # 选中的 twitter handles
    selected_names: list[str] = []      # P35: 选中的项目名（twitter 为空时的 fallback）
    date: Optional[str] = None          # 日期, 默认今天
    provider: str = "volcengine"
    model_id: Optional[str] = None


@router.post("/reassemble")
async def reassemble_daily_report(request: ReassembleRequest):
    """
    POST /api/research/reassemble
    重新组装日报 — 跳过侦察+策略(省 Surf API)，从磁盘读已有报告后跑后半段管线
    """
    import time as _time
    from ..services.daily_report_service import (
        load_analysis_from_disk,
        _run_post_analysis_pipeline,
        cn_now,
    )

    start_time = _time.time()
    date_str = request.date or cn_now().strftime("%Y%m%d")

    # 从磁盘加载指定项目的报告（twitter + name 双途径匹配）
    twitters = request.selected_twitters if request.selected_twitters else None
    names = request.selected_names if request.selected_names else None
    projects, analysis_results = load_analysis_from_disk(date_str, twitters=twitters, names=names)

    if not projects:
        raise HTTPException(
            status_code=404,
            detail=f"未找到 {date_str} 的报告，或选中的项目无匹配文件"
        )

    api_config = {
        "provider": request.provider,
        "model_id": request.model_id,
    }

    def _progress(step, detail):
        logger.info(f"[reassemble][{step}] {detail}")

    try:
        result = await _run_post_analysis_pipeline(
            projects=projects,
            analysis_results=analysis_results,
            api_config=api_config,
            date_str=date_str,
            _progress=_progress,
            skip_sheets_writeback=True,  # 重新组装不覆盖 Sheets
        )

        elapsed = _time.time() - start_time
        return {
            "status": "success",
            "date": date_str,
            "projects_count": len(projects),
            "projects": [{"name": p["name"], "twitter": p["twitter"]} for p in projects],
            "report_path": result["report_path"],
            "card_path": result["card_path"],
            "tweets_path": result["tweets_path"],
            "report_content": result["report_content"],
            "tweets": result["tweets"],
            "elapsed": elapsed,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scout")
async def run_scout_search():
    """
    GET /api/research/scout
    单独跑侦察官，返回项目列表。
    供前端 DataPanel (ResearchPanel) 使用。
    注意: run_scout 内部用同步 httpx，需要 to_thread 避免阻塞 event loop。
    """
    from ..services.daily_report_service import run_scout

    result = await asyncio.to_thread(run_scout)

    if not result["projects"]:
        return {
            "status": "empty",
            "projects": [],
            "message": "未发现热门项目",
            "elapsed": result.get("elapsed", 0),
        }

    return {
        "status": "success",
        "projects": result["projects"],
        "count": len(result["projects"]),
        "elapsed": result.get("elapsed", 0),
    }


@router.get("/reports")
async def list_research_reports():
    """
    GET /api/research/reports
    列出所有日报和单项目报告。
    供前端素材中心「投研报告」标签页使用。
    """
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    projects_dir = RESEARCH_DIR / "projects"
    projects_dir.mkdir(exist_ok=True)

    # 收集日报
    daily_reports = []
    for f in sorted(RESEARCH_DIR.glob("daily_research_*.md"), reverse=True):
        date_str = f.stem.replace("daily_research_", "")
        content = f.read_text(encoding="utf-8")
        # 提取摘要（前 200 字）
        summary = content[:200].replace("\n", " ").strip()
        daily_reports.append({
            "type": "daily",
            "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}" if len(date_str) == 8 else date_str,
            "date_raw": date_str,
            "filename": f.name,
            "summary": summary,
            "size": f.stat().st_size,
        })

    # 收集单项目报告
    project_reports = []
    for f in sorted(projects_dir.glob("*.md"), reverse=True):
        parts = f.stem.rsplit("_", 1)
        name = parts[0] if len(parts) > 1 else f.stem
        date_str = parts[1] if len(parts) > 1 else ""
        project_reports.append({
            "type": "project",
            "name": name,
            "date_raw": date_str,
            "filename": f.name,
            "size": f.stat().st_size,
        })

    return {
        "daily_reports": daily_reports,
        "project_reports": project_reports,
        "daily_count": len(daily_reports),
        "project_count": len(project_reports),
    }


@router.get("/project-report/{filename}")
async def get_project_report(filename: str):
    """
    GET /api/research/project-report/{filename}
    读取单个项目深度报告的完整内容。
    """
    projects_dir = RESEARCH_DIR / "projects"
    file_path = projects_dir / filename
    # 安全检查：防止路径遍历
    if not file_path.resolve().is_relative_to(projects_dir.resolve()):
        raise HTTPException(status_code=400, detail="非法路径")
    content = _read_file(file_path)
    if not content:
        raise HTTPException(status_code=404, detail=f"报告不存在: {filename}")
    return {
        "filename": filename,
        "content": content,
        "size": file_path.stat().st_size,
    }


# P35 F2: 项目历史查询
@router.get("/project-history")
async def get_project_history(twitter: str = ""):
    """
    GET /api/research/project-history?twitter=xxx
    从 ChromaDB 查询指定项目的历史报告列表。
    """
    if not twitter:
        raise HTTPException(status_code=400, detail="请提供 twitter 参数")

    from app.services.chroma_service import get_chroma_service
    chroma = get_chroma_service()
    history = chroma.get_project_history(twitter)
    return {
        "twitter": twitter,
        "count": len(history),
        "reports": history,
    }

