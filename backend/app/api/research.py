"""
P31: 投研报告 API
提供投研数据给前端展示
"""
import json
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException

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
