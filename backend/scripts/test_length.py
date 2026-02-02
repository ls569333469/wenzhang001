"""
短篇/中篇/长篇内容生成测试
话题: 现货黄金日内暴涨 100 美元，突破 5280 美元/盎司
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_length_generation(length: str, topic: str):
    """测试指定长度的内容生成"""
    print(f"\n{'='*60}")
    print(f"测试: {length} 篇幅")
    print(f"{'='*60}")
    
    payload = {
        "input": topic,
        "mode": "deep_analysis",
        "style": "banfo",
        "length": length
    }
    
    print(f"请求参数: mode={payload['mode']}, style={payload['style']}, length={length}")
    
    try:
        start_time = time.time()
        
        # 使用 SSE 流式接收
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            stream=True,
            timeout=180
        )
        
        content = ""
        title = ""
        word_count = 0
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        
                        # 提取最终内容
                        if data.get("type") == "final_result":
                            content = data.get("payload", "")
                            word_count = len(content)
                            
                        # 记录进度
                        if data.get("type") == "agent_update":
                            agent = data.get("step", "")
                            status = data.get("status", "")
                            print(f"   Agent: {agent} - {status}")
                            
                    except json.JSONDecodeError:
                        continue
        
        elapsed = time.time() - start_time
        
        # 输出结果
        print(f"\n📝 结果:")
        print(f"   标题: {title[:50]}..." if len(title) > 50 else f"   标题: {title}")
        print(f"   字数: {word_count} 字")
        print(f"   耗时: {elapsed:.1f} 秒")
        
        # 预期字数范围
        expected = {
            "short": (300, 700),
            "medium": (1200, 2000),
            "long": (2500, 4000)
        }
        
        min_words, max_words = expected.get(length, (0, 10000))
        if min_words <= word_count <= max_words:
            print(f"   ✅ 字数符合预期 ({min_words}-{max_words})")
        else:
            print(f"   ⚠️ 字数偏差 (预期 {min_words}-{max_words})")
        
        # 返回内容摘要
        if content:
            print(f"\n   内容预览 (前200字):")
            print(f"   {content[:200]}...")
            
        return {
            "length": length,
            "title": title,
            "word_count": word_count,
            "elapsed": elapsed,
            "content": content
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    topic = "现货黄金日内暴涨 100 美元，突破 5280 美元/盎司"
    
    print("="*60)
    print("    短篇/中篇/长篇 内容生成测试")
    print(f"    话题: {topic}")
    print("="*60)
    
    results = []
    
    for length in ["short", "medium", "long"]:
        result = test_length_generation(length, topic)
        if result:
            results.append(result)
        time.sleep(2)  # 间隔避免频繁请求
    
    # 汇总
    print("\n" + "="*60)
    print("    测试结果汇总")
    print("="*60)
    
    print(f"\n{'篇幅':<10} {'字数':<10} {'耗时':<10} {'状态':<10}")
    print("-"*40)
    
    for r in results:
        length_cn = {"short": "短篇", "medium": "中篇", "long": "长篇"}.get(r["length"], r["length"])
        status = "✅" if r["word_count"] > 0 else "❌"
        print(f"{length_cn:<10} {r['word_count']:<10} {r['elapsed']:.1f}秒{'':<5} {status}")
    
    # 保存结果到文件
    with open("length_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 length_test_results.json")
    
    return len(results) == 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
