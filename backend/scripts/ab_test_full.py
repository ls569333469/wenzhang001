"""
完整四阶段 A/B 测试：策略师 → 写手 → 审核 → 润色 + AI词汇检测
素材: Tether CNHT 停止发行
A 组: 样本仅传 content
B 组: 样本传 content + emotional_valence + logic_pattern
"""
import os, sys, json, time, random, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from app.core.llm import generate_text
from app.core.prompts import render_prompt, render_modular_prompt
from app.core.forbidden_patterns import load_forbidden_patterns, get_all_forbidden_words
from app.services.sample_service import sample_service
from app.agents.critic.standard import standard_critic
from app.agents.polisher.short_article import short_article_polisher, _scan_forbidden_words

# ============================================================
TEST_MATERIAL = """官方消息，Tether 宣布将从即日起停止离岸人民币稳定币 CNHT 的发行，并在公告发布的一年后停止对 CNHT 赎回的支持。

Tether 表示，消费者对该产品兴趣不高，CNHT 的社区需求有限，其使用水平不足以支撑 Tether 旗下所有产品所采用的标准所需的运营支持。"""

# AI 高频词 / 刻板词汇检测列表（除 forbidden_patterns 之外的补充）
AI_MARKERS = [
    "值得注意的是", "不可忽视", "毋庸置疑", "不言而喻",
    "总而言之", "综上所述", "诚然", "显而易见",
    "在此背景下", "以此为鉴", "与此同时", "由此可见",
    "这一举措", "这一决定", "这一事件",
    "进一步", "深入探讨", "深入分析",
    "核心", "关键", "重要的是",
    "不仅...而且", "首先...其次...最后",
    "生态", "赋能", "赛道", "范式", "闭环", "底层逻辑",
    "战略布局", "重磅", "引发广泛关注", "引发热议",
]

def detect_ai_markers(text):
    """检测 AI 高频词和刻板表达"""
    hits = []
    for marker in AI_MARKERS:
        if marker in text:
            hits.append(marker)
    # 也跑 forbidden_patterns 扫描
    fp_hits = _scan_forbidden_words(text)
    return hits, fp_hits

# ============================================================
# 拉取两组样本
# ============================================================
raw_samples = sample_service.get_samples(style='mimeng', count=3)
rag_a = "\n\n".join([f"--- 样本 {i+1} ---\n{s.get('content', '')[:2000]}" for i, s in enumerate(raw_samples)])

lib_path = os.path.join(os.path.dirname(__file__), "..", "data", "style_library.json")
with open(lib_path, "r", encoding="utf-8") as f:
    lib = json.load(f)
rich = [x for x in lib if x.get("author") in ("mimeng", "咪蒙") and x.get("logic_pattern")]
random.seed(42)
rich3 = random.sample(rich, min(3, len(rich)))
rag_b = "\n\n".join([
    f"--- 样本 {i+1} ---\n内容: {s['content'][:500]}\n情绪: {s.get('emotional_valence','N/A')}\n逻辑公式: {s.get('logic_pattern','N/A')}"
    for i, s in enumerate(rich3)
])

# ============================================================
# 辅助函数
# ============================================================
def run_strategist(rag_context, label):
    ctx = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_input": TEST_MATERIAL, "rag_context": rag_context,
        "forbidden_patterns": load_forbidden_patterns(),
    }
    sys_prompt = render_prompt("strategist/short_article", ctx)
    usr_prompt = f"[Test-{label}] 请分析以上素材，输出3个版本方案的JSON。"
    t0 = time.time()
    resp = generate_text(prompt=usr_prompt, system_prompt=sys_prompt, provider="volcengine", temperature=0.85)
    dt = time.time() - t0
    text = resp
    if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
    data = json.loads(text)
    print(f"  [1.策略师] {dt:.0f}s - {len(data.get('plans',[]))} plans")
    return data

def run_writer_single(raw_input, plan, rag_context, label):
    ctx = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "style": "mimeng", "length": {"min": 50, "max": 300, "target": 200},
        "retention_level": 3, "raw_input": raw_input,
        "strategy_plan": json.dumps(plan, ensure_ascii=False),
        "rag_context": rag_context, "context_card": "",
        "forbidden_patterns": load_forbidden_patterns(),
    }
    system_prompt = render_modular_prompt("writer/short_article.jinja2", ctx)
    user_prompt = f"""素材：
{raw_input}

你要写的版本：{plan.get('label','')}
角度：{plan.get('angle','')}
第一句的方向：{plan.get('hook','')}
语气：{plan.get('tone','')}
情感走向：{plan.get('emotion_arc','')}
收尾方式：{plan.get('ending_style','')}

⚠️ 严禁编造素材中没有的事实、场景、对话、数据。只能基于素材内容进行观点重构和表达重构。
⚠️ 记住节奏要求：必须有长短句交替，禁止全篇碎片短句。
直接写。200字左右。第一句就亮出判断。"""

    t0 = time.time()
    resp = generate_text(prompt=user_prompt, system_prompt=system_prompt, provider="volcengine", temperature=0.88, max_tokens=450)
    dt = time.time() - t0
    text = re.sub(r'<think>.*?</think>', '', resp, flags=re.DOTALL)
    text = re.sub(r'——', '，', text); text = text.replace('；', '。')
    text = re.sub(r'^#+\s*.*\n', '', text, flags=re.MULTILINE); text = text.strip()
    print(f"    [2.写手] {plan.get('label','')} {dt:.0f}s {len(text)}字")
    return text

def run_critic(draft, strategy_json):
    t0 = time.time()
    result = standard_critic(draft=draft, mode="short_article", strategy_json=json.dumps(strategy_json, ensure_ascii=False))
    dt = time.time() - t0
    print(f"  [3.审核] {dt:.0f}s - 分数:{result['score']} 判定:{result['verdict']}")
    return result

def run_polisher(draft):
    t0 = time.time()
    result = short_article_polisher(draft=draft, critique_feedback="", mode="short_article")
    dt = time.time() - t0
    print(f"  [4.润色] {dt:.0f}s - {len(result)}字")
    return result

# ============================================================
# 运行全流程
# ============================================================
report_lines = []
report_lines.append("# 完整四阶段 A/B 测试报告\n")
report_lines.append(f"> 测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 模型：volcengine 默认\n")
report_lines.append("---\n\n## 测试素材\n")
report_lines.append(f"```\n{TEST_MATERIAL.strip()}\n```\n")

for group_label, rag in [("A_仅content", rag_a), ("B_增强版", rag_b)]:
    print(f"\n{'='*50}\n  {group_label}\n{'='*50}")
    report_lines.append(f"\n---\n\n## {group_label}\n")
    
    # 1. 策略师
    plans_data = run_strategist(rag, group_label)
    plans = plans_data.get("plans", [])
    
    # 2. 写手 (逐版本)
    all_articles = []
    draft_combined = ""
    for i, plan in enumerate(plans):
        article = run_writer_single(TEST_MATERIAL, plan, rag, group_label)
        all_articles.append({"plan": plan, "writer_output": article})
        if draft_combined: draft_combined += "\n\n---\n\n"
        draft_combined += f"## 版本{i+1}：{plan.get('label','')}\n\n{article}"
    
    # 3. 审核
    critic_result = run_critic(draft_combined, plans_data)
    
    # 4. 润色
    polished = run_polisher(draft_combined)
    
    # 5. AI 词汇检测（对润色后的最终文本）
    ai_hits, fp_hits = detect_ai_markers(polished)
    print(f"  [5.AI检测] AI高频词: {ai_hits if ai_hits else '无'}")
    print(f"             禁用词: {[h['word'] for h in fp_hits] if fp_hits else '无'}")
    
    # 拆分润色后的各版本
    polished_versions = re.split(r'\n\s*---\s*\n', polished)
    polished_versions = [v.strip() for v in polished_versions if v.strip()]
    
    # 写报告
    for i, item in enumerate(all_articles):
        plan = item["plan"]
        writer_text = item["writer_output"]
        final_text = polished_versions[i] if i < len(polished_versions) else writer_text
        
        # 去掉版本标题头
        final_body = re.sub(r'^##\s*版本\d+[：:].*\n\s*', '', final_text).strip()
        writer_body = writer_text.strip()
        
        report_lines.append(f"\n### 版本 {i+1}：{plan.get('label','')}\n")
        report_lines.append(f"| 项目 | 内容 |")
        report_lines.append(f"|------|------|")
        report_lines.append(f"| 角度 | {plan.get('angle','')} |")
        report_lines.append(f"| 开篇方向 | {plan.get('hook','')} |")
        report_lines.append(f"| 语气 | {plan.get('tone','')} |")
        report_lines.append(f"| 情感弧线 | {plan.get('emotion_arc','')} |")
        report_lines.append(f"| 收尾方式 | {plan.get('ending_style','')} |\n")
        report_lines.append(f"**写手原稿（{len(writer_body)}字）：**\n")
        report_lines.append(f"> {writer_body}\n")
        
        if final_body != writer_body:
            report_lines.append(f"**润色后（{len(final_body)}字）：**\n")
            report_lines.append(f"> {final_body}\n")
        else:
            report_lines.append(f"*润色后无变化*\n")
    
    # 审核结果
    report_lines.append(f"\n### 审核结果\n")
    report_lines.append(f"| 项目 | 值 |")
    report_lines.append(f"|------|-----|")
    report_lines.append(f"| 分数 | **{critic_result['score']}** |")
    report_lines.append(f"| 判定 | {critic_result['verdict']} |")
    if critic_result.get('suggestions'):
        report_lines.append(f"| 建议 | {'; '.join(critic_result['suggestions'][:3])} |")
    
    # AI 词汇检测
    report_lines.append(f"\n### AI 词汇检测（润色后）\n")
    if ai_hits:
        report_lines.append(f"**命中 AI 高频词（{len(ai_hits)}个）：** {', '.join(ai_hits)}\n")
    else:
        report_lines.append(f"✅ 未检测到 AI 高频词\n")
    if fp_hits:
        report_lines.append(f"**命中禁用词（{len(fp_hits)}个）：** {', '.join([h['word'] for h in fp_hits])}\n")
    else:
        report_lines.append(f"✅ 未检测到禁用词\n")

# 保存
report_path = os.path.join(os.path.dirname(__file__), "..", "reports", "AB测试_四阶段完整对比.md")
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"\n报告: {report_path}")
print("DONE")
