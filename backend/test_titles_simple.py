"""
简化版标题测试 - 保存完整输出到文件
"""
import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.strategist import strategist_agent

def main():
    raw_input = "现货黄金日内暴涨 100 美元，突破 5280 美元/盎司"
    
    all_titles = []
    
    for run_num in range(1, 4):
        print(f"\n=== 第{run_num}次运行 ===")
        
        state = {
            "raw_input": raw_input,
            "mode": "mimeng",
            "style": "mimeng", 
            "narrative_type": "market_news",
            "retention_level": 3,
            "api_config": {"provider": "volcengine"}
        }
        
        try:
            result = strategist_agent(state)
            plan_text = result.get("plan", "")
            
            try:
                plan = json.loads(plan_text)
                titles = plan.get("title_candidates", [])
                
                for i, t in enumerate(titles, 1):
                    title = t.get("title", str(t)) if isinstance(t, dict) else str(t)
                    formula = t.get("formula_tags", []) if isinstance(t, dict) else []
                    score = t.get("hook_score", "N/A") if isinstance(t, dict) else "N/A"
                    
                    print(f"{i}. {title}")
                    print(f"   公式: {formula}, 分数: {score}")
                    all_titles.append(title)
                    
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                
        except Exception as e:
            print(f"调用失败: {e}")
    
    print(f"\n\n=== 总计生成 {len(all_titles)} 个标题 ===")
    print(f"唯一标题: {len(set(all_titles))} 个")

if __name__ == "__main__":
    main()
