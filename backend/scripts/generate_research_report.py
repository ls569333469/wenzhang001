"""
P31: 投研报告生成器 v2

架构: Layer 1(选题) → Layer 2(分析) → Layer 3(清洗分级) → Layer 4(报告组装)
数据流: Surf API → 原始数据 → 本地清洗 → JSON → Gemini/豆包写报告
"""
import os
import re
import sys
import time
import json
import httpx
from pathlib import Path
from datetime import datetime

# ===== 环境 =====
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

SURF_API_KEY = os.getenv("SURF_API_KEY")
SURF_BASE_URL = "https://api.asksurf.ai/surf-ai/v1/chat/completions"

if not SURF_API_KEY:
    print("ERROR: SURF_API_KEY not found")
    sys.exit(1)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "reports" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y%m%d")
TODAY_DISPLAY = datetime.now().strftime("%Y-%m-%d %H:%M")


# ============================================================
#  Surf API 调用器
# ============================================================
def call_surf(model: str, system_prompt: str, user_prompt: str,
              abilities: list, reasoning: str = "medium",
              timeout: int = 300) -> dict:
    """调用 Surf API，返回结构化结果"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "reasoning_effort": reasoning,
        "ability": abilities,
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


# ============================================================
#  Layer 1: 选题发现（简洁 prompt + 后处理解析）
#  经验教训: prompt 越简洁，Surf 搜索质量越好
# ============================================================
def parse_projects_from_text(text: str) -> list[dict]:
    """从 Surf 自由输出的 Markdown 中解析项目列表"""
    projects = []
    seen = set()

    # 方法1: 解析 Markdown 表格行 (| 项目 | @handle | ... |)
    table_rows = re.findall(
        r"\|\s*(.+?)\s*\|\s*(@\w+)\s*\|(.+?)\|",
        text
    )
    for row in table_rows:
        name = row[0].strip().strip("**").strip("| ").strip()
        twitter = row[1].strip()
        rest = row[2].strip()
        if name.lower() in ("项目名称", "project", "项目", "姓名", "姓名/昵称",
                            "账号名称", "-", "（无）", "(无数据)"):
            continue
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name,
            "twitter": twitter,
            "category": "",
            "kol_24h": 0,
            "buzz": rest[:100].strip(" |"),
            "opportunity": "",
        })

    # 方法2: 解析列表项 (- **Name** (@handle): ...)
    list_items = re.findall(
        r"[-•]\s*\*{0,2}(.+?)\*{0,2}\s*\((@\w+)\)[：:]\s*(.+?)(?:\n|$)",
        text
    )
    for item in list_items:
        name = item[0].strip()
        twitter = item[1].strip()
        key = twitter.lower()
        if key in seen:
            continue
        seen.add(key)
        projects.append({
            "name": name,
            "twitter": twitter,
            "category": "",
            "kol_24h": 0,
            "buzz": item[2].strip()[:100],
            "opportunity": "",
        })

    # 提取 KOL 数字 (如 "20 KOL" or "+20" or "20位KOL")
    for p in projects:
        kol_match = re.search(r"(\d+)\s*(?:位?\s*)?KOL", p["buzz"], re.IGNORECASE)
        if kol_match:
            p["kol_24h"] = int(kol_match.group(1))

    return projects


def layer1_discover(target_account: str = "@leakmealpha") -> list[dict]:
    """Layer 1: 选题发现 — 简洁 prompt，不限输出格式"""
    # 搜 leak.me 网站 — 经多次测试验证，比搜推文更可靠
    user_prompt = (
        f"请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据。"
        f"leak.me 是一个 Crypto KOL Tracker，追踪加密货币 KOL 的新关注行为。"
        f"请整理出所有被 KOL 关注的 Web3 和 AI 项目，"
        f"用表格列出：项目名称、Twitter 账号、类别、24h KOL 新关注数、热度原因。"
        f"排除个人 KOL 账号、交易所和媒体。"
    )

    print("\n" + "=" * 60)
    print("📡 Layer 1: 选题发现")
    print(f"   数据源: leak.me 网站")
    print("=" * 60)

    result = call_surf(
        model="surf-1.5",
        system_prompt="",
        user_prompt=user_prompt,
        abilities=["search"],
        reasoning="high",
    )

    if result["status"] != 200:
        print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
        return []

    content = result["content"]
    print(f"   ✅ 完成: {result['elapsed']:.0f}s, "
          f"{result['usage'].get('total_tokens', '?')} tokens, "
          f"{len(content)} 字符")

    # 保存原始输出（调试用）
    raw_path = OUTPUT_DIR / f"layer1_raw_{TODAY}.md"
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(f"# Layer 1 原始输出\n\n> {user_prompt}\n\n---\n\n{content}")

    # 后处理: 从自由格式文本中解析项目
    projects = parse_projects_from_text(content)
    print(f"   📋 解析出 {len(projects)} 个项目")
    for i, p in enumerate(projects, 1):
        kol_str = f"KOL +{p['kol_24h']}" if p['kol_24h'] else ""
        print(f"      {i}. {p['name']} ({p['twitter']}) {kol_str}")

    return projects


# ============================================================
#  Layer 2: 深度分析
# ============================================================
LAYER2_SYSTEM = """# 角色
你是一位机构级加密货币投研分析师，专注于发现可操作的投资机会。

# 任务
对指定 Web3 项目进行全维度深度分析，输出结构化的投研数据。

# 分析重点
你的分析应聚焦于"这个项目有没有赚钱机会"，具体包括：
- 关键事件：TGE 时间、空投计划、主网上线、新融资轮、上所公告
- 筹码结构：融资方阵容、估值区间、代币分配
- 团队背书：核心成员背景、顾问阵容
- 市场位置：竞品对比、赛道热度

# 约束
- 用中文输出
- 只输出结论和数据，不要暴露你的搜索过程和推理步骤
- 不要输出任何数据来源引用、URL 链接或内部数据库标记
- 没有数据的维度直接跳过整个章节，不要写"待验证""暂无数据""未找到"
- 每个章节内容精炼，2-4 句话为宜
- 使用表格呈现融资历史、团队、风险等结构化数据

# 输出格式
按以下章节结构输出（没有数据的章节直接省略）：

## 📊 一句话定位
一句话概括项目是什么、做什么、目标市场。

## 🎯 关键事件与参与机会
近期有什么可操作的事件？TGE/空投/主网/融资？参与方式是什么？

## 💰 筹码结构
融资历史表格（轮次/金额/领投/日期）。当前估值/FDV。代币分配比例。

## 👥 团队与背书
核心成员表格（姓名/角色/背景）。顾问阵容。团队可信度（强/中/弱）。

## 📈 市场数据
价格/市值/交易量/TVL。社交数据：X 粉丝数。

## 🔥 近期催化剂
最近 2 周内的重要公告或事件，为什么引发关注。

## ⚠️ 风险清单
表格列出 3-5 个风险（风险描述/影响程度/发生概率）。

## 🎯 结论
一句话判断：看涨/中立/看跌。适合的参与策略。需要跟踪的 3 个关键指标。"""


def layer2_analyze(project: dict) -> dict:
    """Layer 2: 深度分析 — 逐项目调用 Surf，获取原始投研数据"""
    name = project["name"]
    twitter = project.get("twitter", "")
    category = project.get("category", "")
    buzz = project.get("buzz", "")
    opportunity = project.get("opportunity", "")
    kol_24h = project.get("kol_24h", "?")

    user_prompt = f"""请对 {name}（{twitter}）进行深度投研分析。

背景：
- 赛道：{category}
- 热度原因：{buzz}
- 参与机会类型：{opportunity}
- 24h KOL 新增关注：{kol_24h}"""

    print(f"\n  🔍 Layer 2: 分析 {name} ({twitter})...")

    result = call_surf(
        model="surf-1.5",
        system_prompt=LAYER2_SYSTEM,
        user_prompt=user_prompt,
        abilities=["search", "market_analysis"],
        reasoning="high",
        timeout=300,
    )

    if result["status"] != 200:
        print(f"     ❌ 失败: {result.get('error', 'Unknown')}")
        return {"name": name, "status": "failed", "error": result.get("error", "")}

    print(f"     ✅ 完成: {result['elapsed']:.0f}s, "
          f"{len(result.get('content', ''))} 字符, "
          f"{result['usage'].get('total_tokens', '?')} tokens")

    return {
        "name": name,
        "twitter": twitter,
        "category": category,
        "kol_24h": kol_24h,
        "buzz": buzz,
        "opportunity": opportunity,
        "status": "ok",
        "raw_analysis": result["content"],
        "tokens": result["usage"].get("total_tokens", 0),
        "elapsed": result["elapsed"],
    }


# ============================================================
#  Layer 3: 分级 + 清洗（纯本地 Python，0 API 调用）
# ============================================================
def clean_surf_response(text: str) -> str:
    """清洗 Surf API 返回的原始文本，删除内部标记"""
    # 1. 删除内部数据源 ID
    text = re.sub(r"[\(（]?来源[：:].*?[\)）]", "", text)
    text = re.sub(r"[\(（]?source[：:].*?[\)）]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"db_internal_\w+", "", text)
    text = re.sub(r"execute_code_\w+", "", text)

    # 2. 删除完整 URL
    text = re.sub(r"https?://\S+", "", text)

    # 3. 删除"待验证"类无效字段
    text = re.sub(r"[：:]\s*[⚠️]*\s*待验证.*?(?=\n|$)", "：暂无公开数据", text)
    text = re.sub(r"[：:]\s*[⚠️]*\s*暂无数据.*?(?=\n|$)", "", text)
    text = re.sub(r"[：:]\s*[⚠️]*\s*暂无.*?(?=\n|$)", "", text)

    # 4. 删除方法论描述
    text = re.sub(r"[\(（].*?搜索未发现.*?[\)）]", "", text)
    text = re.sub(r"[\(（].*?内部数据.*?[\)）]", "", text)
    text = re.sub(r"[\(（].*?查询结果为空.*?[\)）]", "", text)

    # 5. 清理多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def classify_stage(analysis_text: str) -> str:
    """根据分析内容自动判断项目阶段"""
    lower = analysis_text.lower()

    # 判断逻辑：从高到低
    if any(kw in lower for kw in ["tvl", "协议收入", "链上用户", "月活"]):
        return "mature"
    if any(kw in lower for kw in ["当前价格", "市值 $", "交易量", "上线交易所", "已上市"]):
        return "launched"
    if any(kw in lower for kw in ["pre-tge", "预售", "tge", "代币计划", "预分配", "whales market"]):
        return "pre_tge"
    if any(kw in lower for kw in ["融资", "种子轮", "天使轮", "pre-seed", "seed"]):
        return "funded"
    return "concept"


def layer3_clean_and_classify(raw_results: list[dict]) -> list[dict]:
    """Layer 3: 清洗原始数据 + 自动分级 → 结构化 JSON"""
    print("\n" + "=" * 60)
    print("🧹 Layer 3: 分级 + 清洗（本地处理，0 API 调用）")
    print("=" * 60)

    cleaned = []
    for r in raw_results:
        if r.get("status") != "ok":
            print(f"  ⏭️ 跳过失败项目: {r['name']}")
            continue

        raw_text = r["raw_analysis"]
        clean_text = clean_surf_response(raw_text)
        stage = classify_stage(clean_text)

        project_data = {
            "name": r["name"],
            "twitter": r.get("twitter", ""),
            "category": r.get("category", ""),
            "stage": stage,
            "kol_24h": r.get("kol_24h", 0),
            "buzz": r.get("buzz", ""),
            "opportunity": r.get("opportunity", ""),
            "analysis": clean_text,
            "tokens_used": r.get("tokens", 0),
            "analysis_time": r.get("elapsed", 0),
        }
        cleaned.append(project_data)
        print(f"  ✅ {r['name']}: stage={stage}, "
              f"原始 {len(raw_text)} 字 → 清洗后 {len(clean_text)} 字 "
              f"(删除 {len(raw_text) - len(clean_text)} 字)")

    return cleaned


def save_json(projects: list[dict]) -> Path:
    """保存结构化数据为 JSON 中间文件"""
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": TODAY_DISPLAY,
        "source": "KOL Tracker × Surf AI",
        "project_count": len(projects),
        "projects": projects,
    }
    json_path = OUTPUT_DIR / f"data_{TODAY}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 JSON 已保存: {json_path}")
    return json_path


# ============================================================
#  Layer 4: 报告组装（Phase 1: 本地 Python 模板拼装）
#  TODO: Phase 2 接入 Gemini/豆包 AI 润色
# ============================================================
def layer4_build_report(projects: list[dict]) -> Path:
    """Layer 4: 组装最终 Markdown 报告"""
    print("\n" + "=" * 60)
    print("📝 Layer 4: 报告组装")
    print("=" * 60)

    stage_labels = {
        "concept": "💡 概念期",
        "funded": "💰 已融资",
        "pre_tge": "🎯 Pre-TGE",
        "launched": "🚀 已上线",
        "mature": "🏛️ 成熟协议",
    }

    lines = [
        "# 🌊 每日投研快报\n",
        f"> **生成时间**: {TODAY_DISPLAY}  ",
        f"> **数据来源**: KOL Tracker + Surf AI 深度分析  ",
        f"> **分析模型**: surf-1.5 (reasoning: high)  ",
        f"> **架构版本**: v2（选题→分析→清洗→组装）\n",
        "---\n",
        "## 📋 今日热点项目总览\n",
        "| # | 项目 | 阶段 | 类别 | KOL | 参与机会 |",
        "|---|------|------|------|-----|---------|",
    ]

    for i, p in enumerate(projects, 1):
        stage = stage_labels.get(p["stage"], p["stage"])
        lines.append(
            f"| {i} | **{p['name']}** ({p.get('twitter', '')}) "
            f"| {stage} | {p.get('category', '')} "
            f"| +{p.get('kol_24h', '?')} | {p.get('opportunity', '')} |"
        )

    lines.append("\n---\n")

    for i, p in enumerate(projects, 1):
        stage = stage_labels.get(p["stage"], p["stage"])
        lines.append(f"## {i}. {p['name']}\n")
        lines.append(f"> 📍 {p.get('category', '')} | {stage} "
                     f"| 🐦 {p.get('twitter', '')} | 🔥 KOL +{p.get('kol_24h', '?')}\n")
        lines.append(p.get("analysis", "（分析数据获取失败）"))
        lines.append("\n---\n")

    # 免责声明
    lines.append("## 📝 报告说明\n")
    lines.append("- 本报告由 AI 自动生成，仅供参考，不构成投资建议")
    lines.append("- 数据来源于公开信息，可能存在滞后或不完整")
    lines.append("- 投资有风险，入市需谨慎\n")

    report_text = "\n".join(lines)
    report_path = OUTPUT_DIR / f"daily_research_{TODAY}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"  ✅ Markdown 报告已保存: {report_path}")
    print(f"  📊 共 {len(projects)} 个项目, {len(report_text)} 字符")

    return report_path


# ============================================================
#  主流程
# ============================================================
if __name__ == "__main__":
    total_start = time.time()

    # === Layer 1: 选题发现 ===
    projects = layer1_discover("@leakmealpha")
    if not projects:
        print("\n❌ Layer 1 未发现项目，退出")
        sys.exit(1)

    # 控制项目数量（3-8 个，默认取前 5）
    MAX_PROJECTS = 5
    selected = projects[:MAX_PROJECTS]
    print(f"\n📌 选取前 {len(selected)} 个项目进行深度分析")

    # === Layer 2: 深度分析 ===
    print("\n" + "=" * 60)
    print("🔬 Layer 2: 深度分析")
    print("=" * 60)

    raw_results = []
    for p in selected:
        result = layer2_analyze(p)
        raw_results.append(result)

    # === Layer 3: 分级 + 清洗 ===
    cleaned_projects = layer3_clean_and_classify(raw_results)

    if not cleaned_projects:
        print("\n❌ 所有项目分析失败，退出")
        sys.exit(1)

    # 保存 JSON 中间文件
    json_path = save_json(cleaned_projects)

    # === Layer 4: 报告组装 ===
    report_path = layer4_build_report(cleaned_projects)

    # === 统计 ===
    total_time = time.time() - total_start
    total_tokens = sum(p.get("tokens_used", 0) for p in cleaned_projects)
    print("\n" + "=" * 60)
    print("📊 执行统计")
    print("=" * 60)
    print(f"  总耗时: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"  总 tokens: {total_tokens:,}")
    print(f"  项目数: {len(cleaned_projects)}")
    print(f"  JSON: {json_path}")
    print(f"  报告: {report_path}")
    print("\n✅ Done!")
