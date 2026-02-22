"""
P29 诊断：追踪策略师完整调用链路
输出每一步的输入/输出数据
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.sample_service import sample_service
from app.agents.strategist import build_strategist_context, build_strategist_prompt

TEST_INPUT = """Vitalik Buterin 发布以太坊 L1 扩展路线图，计划将 L1 Gas Limit 提升 10 倍。
核心变化：将区块 gas limit 从当前 3600万提升到 3.6亿。
社区反应两极化。Solana 社区调侃"欢迎来到 2021 年"。
当前 ETH 价格 2780美元，过去30天下跌 12%。"""

state = {
    "raw_input": TEST_INPUT,
    "mode": "short_article",
    "style": "banfo",
    "narrative_type": "project_review",
    "retention_level": 3,
    "api_config": {"provider": "google", "model_id": "gemini-2.0-flash"},
}

out = []
out.append("# P29 策略师调用链路诊断\n")

# ========== Step 1: 公式菜单 ==========
out.append("## Step 1: 获取公式菜单 (get_pattern_menu)\n")
out.append("**调用**: `sample_service.get_pattern_menu(style='banfo')`")
out.append("**数据源**: Google Sheets → 风格_半佛 Tab\n")

menu = sample_service.get_pattern_menu("banfo")
out.append(f"**返回** {len(menu)} 个公式:\n")
for i, p in enumerate(menu):
    out.append(f"  {i+1}. {p}")
out.append("")

# ========== Step 2: 获取随机样本 ==========
out.append("## Step 2: 获取随机样本 (get_samples)\n")
out.append("**调用**: `sample_service.get_samples(style='banfo', count=3)`")
out.append("**逻辑**: 从风格_半佛 Tab 中 random.sample() 随机抽 3 条\n")

samples = sample_service.get_samples(style="banfo", count=3)
for i, s in enumerate(samples):
    out.append(f"### 样本{i+1}")
    out.append(f"- content: {s.get('content', '')[:150]}")
    out.append(f"- logic_pattern: {s.get('logic_pattern', '(空)')}")
    out.append(f"- emotional_valence: {s.get('emotional_valence', '(空)')}")
    out.append(f"- snippet_type: {s.get('snippet_type', '(空)')}")
    out.append("")

# ========== Step 3: build_strategist_context ==========
out.append("## Step 3: 构建策略师上下文 (build_strategist_context)\n")
context = build_strategist_context(state)

out.append("**context 包含的 key**:\n")
for k in context.keys():
    if k == "rag_context":
        out.append(f"- `{k}`: ({len(context[k])}字) 3条样本的格式化文本")
    elif k == "pattern_menu":
        out.append(f"- `{k}`: {context[k]}")
    elif k == "forbidden_patterns":
        out.append(f"- `{k}`: (词库已加载)")
    else:
        out.append(f"- `{k}`: {context[k]}")
out.append("")

# ========== Step 4: build_strategist_prompt ==========
out.append("## Step 4: 构建 Prompt (build_strategist_prompt)\n")
system_prompt, user_prompt = build_strategist_prompt(context, state)

out.append(f"**system_prompt 长度**: {len(system_prompt)} 字符")
out.append(f"**user_prompt 长度**: {len(user_prompt)} 字符\n")

# 检查是哪个模板
if "公式菜单" in system_prompt or "pattern_menu" in system_prompt or "写作公式" in system_prompt:
    out.append("✅ 使用了 `strategist/short_article.jinja2`（P29 新模板）\n")
else:
    out.append("⚠️ 使用了通用 `strategist.jinja2`（旧模板）\n")

out.append("### system_prompt 全文\n")
out.append("```")
out.append(system_prompt)
out.append("```\n")

out.append("### user_prompt 全文\n")
out.append("```")
out.append(user_prompt)
out.append("```\n")

# ========== Step 5: rag_context 详情 ==========
out.append("## Step 5: 传给策略师的 rag_context（样本原文）\n")
out.append("```")
out.append(context.get("rag_context", ""))
out.append("```\n")

# ========== 写入文件 ==========
report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "reports", "P29_策略师调用链路.md")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(f"Done: {report_path}")
