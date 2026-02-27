"""
P31: 投研模块共享工具
提供 Surf API 调用、输出解析等共享函数
"""
import os
import re
import time
import httpx

SURF_API_KEY = os.getenv("SURF_API_KEY", "")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"


def call_surf(model: str, system_prompt: str, user_prompt: str,
              abilities: list = None, reasoning: str = "medium",
              timeout: int = 300) -> dict:
    """调用 Surf API，返回 {status, content, usage, elapsed}"""
    if not SURF_API_KEY:
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
        "Authorization": f"Bearer {SURF_API_KEY}",
        "Content-Type": "application/json",
    }

    start = time.time()
    try:
        with httpx.Client(timeout=timeout, verify=False) as client:
            resp = client.post(SURF_BASE_URL, headers=headers, json=payload)
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": 200,
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "elapsed": elapsed,
            }
        return {"status": resp.status_code, "error": resp.text[:500], "elapsed": elapsed}
    except Exception as e:
        return {"status": "error", "error": str(e), "elapsed": time.time() - start}


def parse_projects_from_text(text: str) -> list[dict]:
    """从 Surf 返回的 Markdown 中解析项目列表"""
    projects = []
    seen = set()

    # 解析 Markdown 表格行
    table_rows = re.findall(r"\|\s*(.+?)\s*\|\s*(@\w+)\s*\|(.+?)\|", text)
    for row in table_rows:
        name = row[0].strip().strip("**").strip("| ").strip()
        twitter = row[1].strip()
        rest = row[2].strip()
        if name.lower() in ("项目名称", "project", "项目", "姓名", "-", "（无）"):
            continue
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name, "twitter": twitter,
            "category": "", "kol_24h": 0,
            "buzz": rest[:100].strip(" |"),
        })

    # 解析列表项
    list_items = re.findall(
        r"[-•]\s*\*{0,2}(.+?)\*{0,2}\s*\((@\w+)\)[：:]\s*(.+?)(?:\n|$)", text
    )
    for item in list_items:
        name = item[0].strip()
        twitter = item[1].strip()
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name, "twitter": twitter,
            "category": "", "kol_24h": 0,
            "buzz": item[2].strip()[:100],
        })

    # 提取 KOL 数字
    for p in projects:
        kol_match = re.search(r"(\d+)\s*(?:位?\s*)?KOL", p["buzz"], re.IGNORECASE)
        if kol_match:
            p["kol_24h"] = int(kol_match.group(1))

    return projects
