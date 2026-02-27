"""
P31: 投研报告 API
提供投研数据给前端展示 + 日报生成 + 侦察官搜索
"""
import json
import os
import asyncio
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/research", tags=["research"])

# 报告存储目录
RESEARCH_DIR = Path(__file__).parent.parent.parent.parent / "reports" / "research"


def _find_latest_date() -> Optional[str]:
    """找到最新的报告日期 (YYYYMMDD)"""
    dates = set()
    for f in RESEARCH_DIR.glob("data_*.json"):
        date_str = f.stem.replace("data_", "")
        if len(date_str) == 8 and date_str.isdigit():
            dates.add(date_str)
    return max(dates) if dates else None


def _read_file(path: Path) -> Optional[str]:
    """安全读取文件"""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


@router.get("/latest")
async def get_latest_report():
    """获取最新投研报告数据"""
    date = _find_latest_date()
    if not date:
        raise HTTPException(status_code=404, detail="暂无投研报告")

    # 读取 JSON 数据
    json_path = RESEARCH_DIR / f"data_{date}.json"
    json_data = _read_file(json_path)
    if not json_data:
        raise HTTPException(status_code=404, detail="数据文件不存在")

    projects = json.loads(json_data)

    # 读取配图 HTML
    card_html = _read_file(RESEARCH_DIR / f"card_{date}.html")

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
            tweet_match = re.search(r"```\n(.*?)\n```", content, re.DOTALL)
            tweet_text = tweet_match.group(1) if tweet_match else ""
            tweets.append({
                "name": name,
                "text": tweet_text,
                "char_count": len(tweet_text),
            })

    return {
        "date": f"{date[:4]}-{date[4:6]}-{date[6:8]}",
        "date_raw": date,
        "project_count": projects.get("project_count", 0),
        "projects": projects.get("projects", []),
        "card_html": card_html,
        "tweets": tweets,
        "report_md": report_md,
    }


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

# 投研智能体列表
RESEARCH_AGENTS = {
    "scout": {"file": "scout.jinja2", "label": "🔭 侦察官"},
    "analyst": {"file": "analyst.jinja2", "label": "🔬 分析师"},
    "tweet_digest": {"file": "copywriter/tweet_digest.jinja2", "label": "✍️ 文案官(推文)"},
    "report": {"file": "copywriter/report.jinja2", "label": "✍️ 文案官(报告)"},
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


@router.post("/prompts/{agent_name}")
async def update_research_prompt(agent_name: str, content: str = ""):
    """更新指定投研智能体的 Prompt"""
    if agent_name not in RESEARCH_AGENTS:
        raise HTTPException(status_code=404, detail=f"未知智能体: {agent_name}")

    from pydantic import BaseModel

    class PromptBody(BaseModel):
        content: str

    info = RESEARCH_AGENTS[agent_name]
    path = PROMPTS_DIR / info["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"status": "success", "agent": agent_name}


# ============================================
# P31 v4: 日报生成 + 侦察官独立 API
# ============================================

class DailyReportRequest(BaseModel):
    """日报生成请求"""
    provider: str = "volcengine"
    model_id: Optional[str] = None
    concurrency: int = 3


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
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scout")
async def run_scout_search():
    """
    GET /api/research/scout
    单独跑侦察官，返回项目列表。
    供前端 DataPanel (ResearchPanel) 使用。
    """
    from ..services.daily_report_service import run_scout

    result = run_scout()

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
