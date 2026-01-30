"""
完整捕获12个标题 - 保存到JSON文件
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
    
    results = {"runs": [], "all_titles": []}
    
    for run_num in range(1, 4):
        run_data = {"run": run_num, "titles": []}
        
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
            
            plan = json.loads(plan_text)
            titles = plan.get("title_candidates", [])
            
            for t in titles:
                title_info = {
                    "title": t.get("title", str(t)) if isinstance(t, dict) else str(t),
                    "formula": t.get("formula_tags", []) if isinstance(t, dict) else [],
                    "score": t.get("hook_score", "N/A") if isinstance(t, dict) else "N/A"
                }
                run_data["titles"].append(title_info)
                results["all_titles"].append(title_info["title"])
                
        except Exception as e:
            run_data["error"] = str(e)
        
        results["runs"].append(run_data)
    
    # 保存到JSON文件
    with open("title_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("结果已保存到 title_results.json")
    print(f"总标题数: {len(results['all_titles'])}")
    print(f"唯一标题数: {len(set(results['all_titles']))}")

if __name__ == "__main__":
    main()
