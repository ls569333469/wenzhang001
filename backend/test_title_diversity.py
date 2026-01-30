"""
测试标题多样性 - 直接调用 Strategist Agent
运行3次相同输入，对比生成的标题
"""
import os
import sys
import json
import asyncio

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.strategist import strategist_agent

def run_test(test_num: int, raw_input: str):
    """运行单次测试"""
    print(f"\n{'='*60}")
    print(f"🧪 测试 #{test_num}")
    print(f"{'='*60}")
    
    state = {
        "raw_input": raw_input,
        "mode": "mimeng",  # 咪蒙体
        "style": "mimeng",
        "narrative_type": "market_news",
        "retention_level": 3,
        "api_config": {
            "provider": "volcengine"
        }
    }
    
    try:
        result = strategist_agent(state)
        plan_text = result.get("plan", "")
        
        # 解析 JSON
        try:
            plan = json.loads(plan_text)
            titles = plan.get("title_candidates", [])
            
            print(f"\n📌 生成了 {len(titles)} 个标题:")
            for i, t in enumerate(titles, 1):
                title = t.get("title", str(t)) if isinstance(t, dict) else str(t)
                formula = t.get("formula_tags", []) if isinstance(t, dict) else []
                score = t.get("hook_score", "N/A") if isinstance(t, dict) else "N/A"
                print(f"  {i}. {title}")
                print(f"     公式: {formula}, 分数: {score}")
            
            return titles
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"原始输出: {plan_text[:500]}...")
            return []
            
    except Exception as e:
        print(f"❌ 调用失败: {e}")
        return []

def main():
    raw_input = "现货黄金日内暴涨 100 美元，突破 5280 美元/盎司"
    
    print("=" * 60)
    print("标题多样性测试")
    print("=" * 60)
    print(f"输入: {raw_input}")
    print(f"测试次数: 3")
    
    all_titles = []
    
    for i in range(1, 4):
        titles = run_test(i, raw_input)
        all_titles.append(titles)
    
    # 对比分析
    print("\n" + "=" * 60)
    print("📊 多样性分析")
    print("=" * 60)
    
    # 收集所有标题文本
    all_title_texts = []
    for run_titles in all_titles:
        for t in run_titles:
            title = t.get("title", str(t)) if isinstance(t, dict) else str(t)
            all_title_texts.append(title)
    
    unique_titles = set(all_title_texts)
    
    print(f"\n总生成标题数: {len(all_title_texts)}")
    print(f"唯一标题数: {len(unique_titles)}")
    print(f"重复率: {100 - (len(unique_titles) / len(all_title_texts) * 100):.1f}%")
    
    if len(unique_titles) == len(all_title_texts):
        print("\n✅ 完美！所有标题都不重复！")
    elif len(unique_titles) >= len(all_title_texts) * 0.8:
        print("\n⚠️ 大部分标题不重复，但仍有少量重复")
    else:
        print("\n❌ 标题重复率过高，需要进一步优化")
    
    # 检查是否还有固定短语
    fixed_phrases = ["真相藏在这里", "上车", "泡沫还是起点", "还在观望", "还在等什么"]
    found_fixed = []
    for title in all_title_texts:
        for phrase in fixed_phrases:
            if phrase in title:
                found_fixed.append((title, phrase))
    
    if found_fixed:
        print(f"\n⚠️ 发现固定短语:")
        for title, phrase in found_fixed[:5]:
            print(f"  - '{phrase}' 在: {title[:30]}...")
    else:
        print("\n✅ 未发现固定短语模板!")

if __name__ == "__main__":
    main()
