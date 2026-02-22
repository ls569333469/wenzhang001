"""
P29 AB测试：当前prompt vs 优化prompt
测试素材：Vitalik以太坊扩展层计划

用法：python scripts/run_ab_test_p29.py
"""
import sys, os, json, time, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.agents.strategist import strategist_agent
from app.agents.writer.short_article import short_article_writer

# ========== 测试素材 ==========
TEST_INPUT = """Vitalik Buterin 发布以太坊 L1 扩展路线图，计划将 L1 Gas Limit 提升 10 倍。
核心变化：
1. 将区块 gas limit 从当前 3600万提升到 3.6亿
2. 采用 EIP-4444 对历史数据进行过期处理，降低节点存储要求
3. 无状态客户端 + Verkle Trees 让验证节点不需要存储完整状态
4. 目标：L1 本身成为高性能链，而非仅作为 DA 层
5. 预计分多阶段实施，首阶段在 Pectra 升级中完成

社区反应两极化：
- 支持者认为这是 ETH 重新夺回 DeFi 主权的关键
- 反对者担心节点中心化风险加剧
- Solana 社区调侃"欢迎来到 2021 年"

当前 ETH 价格 $2,780，过去30天下跌 12%。"""

def run_group(group_name: str, state: dict):
    """运行一组测试"""
    print(f"\n{'='*60}")
    print(f"  {group_name}")
    print(f"{'='*60}\n")
    
    # Step 1: 策略师
    print(">>> Step 1: 策略师分析...")
    strategist_result = strategist_agent(state)
    strategy_json = strategist_result.get("plan", "{}")
    print(f">>> 策略师输出长度: {len(strategy_json)} chars")
    
    # 解析策略师输出
    strategy_obj = {}
    try:
        strategy_obj = json.loads(strategy_json) if isinstance(strategy_json, str) else strategy_json
        plans = strategy_obj.get("plans", [])
        print(f">>> 提取到 {len(plans)} 个版本方案:")
        for i, p in enumerate(plans):
            print(f"    版本{i+1}: {p.get('label','')} | tone:{p.get('tone','')} | ending:{p.get('ending_style','')}")
    except:
        plans = []
    
    # Step 2: 写手生成
    print("\n>>> Step 2: 写手生成...")
    writer_state = {**state, "strategy_json": strategy_json}
    result = short_article_writer(writer_state)
    
    variants = result.get("variants", [])
    print(f">>> 写手输出 {len(variants)} 个版本")
    
    return {
        "strategy_json": strategy_json,
        "strategy_obj": strategy_obj if plans else {},
        "variants": variants,
    }

def main():
    base_state = {
        "raw_input": TEST_INPUT,
        "mode": "short_article",
        "style": "banfo",
        "narrative_type": "project_review",
        "retention_level": 3,
        "api_config": {
            "provider": "google",
            "model_id": "gemini-2.0-flash",
        },
    }
    
    results = {}
    
    # ========== A组：当前prompt ==========
    print("\n" + "🅰️ "*20)
    state_a = copy.deepcopy(base_state)
    results["A"] = run_group("🅰️  A组：当前 Prompt（基线）", state_a)
    
    time.sleep(3)  # 避免API限流
    
    # ========== B组：修改prompt ==========
    # 直接用 custom_prompts 注入优化后的策略师和写手 prompt
    print("\n" + "🅱️ "*20)
    state_b = copy.deepcopy(base_state)
    
    # B组写手用 custom_prompts 覆盖
    state_b["custom_prompts"] = {
        "writer": """Current Time: {{ current_time_str }}

{% if context_card %}
---
## 事件脉络卡片
{% if context_card.has_event %}📍 爆发性事件{% else %}📍 快讯速评{% endif %}
- 摘要: {{ context_card.summary }}
- 时效: {{ context_card.time_context }}
{% if context_card.forward_look %}- 展望: {{ context_card.forward_look }}{% endif %}
{% endif %}

---

## 角色设定

你是一个在X上日更的 Web3 KOL，你的粉丝因为你的毒舌和犀利而关注你。
你擅长把复杂信息用一两句话重新表达，让读者觉得"哦原来是这么回事"。
你有明确的立场，偶尔调侃，但判断基于事实。你不是在写分析报告，你是在发推。
你的读者都是圈内人，他们想看的是你怎么想，不需要你从头科普。

---

## 任务描述

核心能力是重构：用自己的视角、结构、语言，写出一篇全新的原创短文。
你写的东西和原文放在一起，读者不会觉得是同一篇的改写版。

按策略官推荐的方案写作，约{{ length.target }}字（{{ length.min }}-{{ length.max }}）。

输出结构：
1. 第一句亮出你的判断或反应（像刷到新闻后的第一句话）
2. 中间用3-5个短段落展开，每段1-2句话，段间空行，像发Thread
3. 收尾按策略官指定的 ending_style，一句话打完收工

---

## 风格要求

### 节奏（重要！）
- 大部分句子8-22字，但**每篇必须包含1-2个30-50字的复合长句**作为段落支撑
- 长句和短句交替出现，像人在思考，想到哪说到哪，偶尔绕一下再拉回来
- 段落以1-2句为主，段间必须空行。允许1处3-4句的密集段作为信息炸弹
- **绝对禁止全篇都是整齐划一的碎片短句**，这是最明显的AI指纹

### 人味
- 偶尔承认不确定
- 允许一处自己修正自己的说法
- 不需要每句话都斩钉截铁，允许一处观点灰度
- 信息密度不均匀：可以有1处只是顺嘴感慨，不必每段都有干货

### 口语感（重要！）
- 善用过渡词拉近距离：说实话 / 你品品 / 话说回来 / 换句话说 / 最狠的是
- 允许1处语气词开头：啊这 / 好家伙 / 离谱 / 有意思
- 不要写"值得注意的是"、"综上所述"，写"但最关键的一点是"、"所以呢"
- 语感目标：像你一个聪明朋友在微信上给你发语音转的文字

---

## 禁止事项

标点：破折号「——」、分号「；」
AI词（出现即不合格）：赛道、生态、布局、底层逻辑、核心竞争力、破局、赋能、差异化
AI比喻词（出现即不合格）：筹码、牌桌、战场、猎杀、阵地
屏蔽词：庄哥、庄家、币圈、韭菜、割韭菜

事实：
- 虚构原文中不存在的场景、对话、动作、时间、地点
- 编造数据、案例、项目、事件
- 给人物加戏（编造心理活动、肢体动作、表情描写）
- 所有内容必须能从素材原文中找到依据

---

## 素材
{{ raw_input }}

{% if rag_context %}
## 样本参考
{{ rag_context }}
{% endif %}

---

直接输出中文短文正文。约**{{ length.target }}字**。第一句就亮出你的判断。"""
    }
    
    results["B"] = run_group("🅱️  B组：优化 Prompt（P29）", state_b)
    
    # ========== 生成对比报告 ==========
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "reports", "P29_AB测试_提示词优化.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# P29 AB测试：提示词优化对比\n\n")
        f.write(f"测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试素材：Vitalik 以太坊 L1 扩展路线图\n")
        f.write(f"风格：banfo | 模式：short_article\n\n")
        
        for group_key in ["A", "B"]:
            group_label = "A组（当前Prompt）" if group_key == "A" else "B组（优化Prompt）"
            f.write(f"---\n\n## {group_label}\n\n")
            
            # 策略师输出
            try:
                sobj = results[group_key].get("strategy_obj", {})
                plans = sobj.get("plans", [])
                f.write("### 策略师方案\n\n")
                for i, p in enumerate(plans):
                    f.write(f"**版本{i+1}: {p.get('label','')}**\n")
                    f.write(f"- angle: {p.get('angle','')}\n")
                    f.write(f"- hook: {p.get('hook','')}\n")
                    f.write(f"- tone: {p.get('tone','')}\n")
                    if p.get('emotion_arc'):
                        f.write(f"- emotion_arc: {p.get('emotion_arc','')}\n")
                    if p.get('logic_pattern'):
                        f.write(f"- logic_pattern: {p.get('logic_pattern','')}\n")
                    f.write(f"- ending_style: {p.get('ending_style','')}\n\n")
            except:
                f.write("策略师输出解析失败\n\n")
            
            # 写手输出
            variants = results[group_key].get("variants", [])
            f.write("### 写手输出\n\n")
            for v in variants:
                f.write(f"#### {v.get('label', v.get('key',''))} ({v.get('char_count',0)}字)\n\n")
                f.write(f"{v.get('content','')}\n\n")
        
        f.write("---\n\n## 对比维度\n\n")
        f.write("| 维度 | A组（当前） | B组（优化） |\n")
        f.write("|------|-----------|------------|\n")
        f.write("| 开头风格 | | |\n")
        f.write("| 段落结构 | | |\n")
        f.write("| 收尾方式 | | |\n")
        f.write("| 口语感 | | |\n")
        f.write("| 像真人KOL程度 | | |\n")
    
    print(f"\n\n{'='*60}")
    print(f"  报告已保存: {report_path}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
