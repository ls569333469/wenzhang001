"""
Web3 话题完整写作流程测试 - 增强监控版
话题: 前 Coinbase CTO：实物黄金并非对冲美元危机的最佳品种，比特币更具抗审查优势
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOPIC = "前 Coinbase CTO：实物黄金并非对冲美元危机的最佳品种，比特币更具抗审查优势"

def test_with_monitoring(length: str):
    """带完整监控的内容生成测试"""
    print(f"\n{'='*70}")
    print(f"  测试篇幅: {length.upper()}")
    print(f"  话题: {TOPIC[:40]}...")
    print(f"{'='*70}")
    
    payload = {
        "input": TOPIC,
        "mode": "deep_analysis",
        "style": "banfo",
        "length": length
    }
    
    print(f"\n📋 请求参数:")
    print(f"   mode: {payload['mode']}")
    print(f"   style: {payload['style']}")
    print(f"   length: {payload['length']}")
    
    # 思维链路记录
    thinking_steps = []
    agent_timeline = []
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            stream=True,
            timeout=600  # 10分钟超时
        )
        
        content = ""
        word_count = 0
        
        print(f"\n🧠 思维链路监控:")
        print("-"*50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        event_type = data.get("type", "")
                        
                        # 思考步骤
                        if event_type == "thinking_step":
                            agent = data.get("agent", "")
                            step = data.get("step", "")
                            detail = data.get("detail", "")
                            progress = data.get("progress", 0)
                            
                            timestamp = time.time() - start_time
                            thinking_steps.append({
                                "time": f"{timestamp:.1f}s",
                                "agent": agent,
                                "step": step,
                                "detail": detail
                            })
                            
                            print(f"   [{timestamp:5.1f}s] {agent:12} | {step:15} | {detail[:40]}...")
                        
                        # Agent 完成状态
                        elif event_type == "agent_update":
                            agent = data.get("step", "")
                            status = data.get("status", "")
                            logs = data.get("logs", [])
                            
                            timestamp = time.time() - start_time
                            agent_timeline.append({
                                "time": f"{timestamp:.1f}s",
                                "agent": agent,
                                "status": status
                            })
                            
                            status_icon = "✅" if status == "completed" else "🔄"
                            print(f"   [{timestamp:5.1f}s] {status_icon} {agent} - {status}")
                            
                            if logs:
                                for log in logs[:2]:
                                    print(f"            └─ {log[:50]}...")
                        
                        # 最终结果
                        elif event_type == "final_result":
                            content = data.get("payload", "")
                            word_count = len(content)
                            
                        # 错误
                        elif event_type == "error":
                            print(f"   ❌ 错误: {data.get('message', '')}")
                            
                    except json.JSONDecodeError:
                        continue
        
        elapsed = time.time() - start_time
        
        # 结果汇总
        print(f"\n📊 执行结果:")
        print("-"*50)
        print(f"   总耗时: {elapsed:.1f} 秒")
        print(f"   字数: {word_count} 字")
        
        # P10 字数验证
        length_map = {
            "short": {"min": 300, "max": 600},
            "medium": {"min": 800, "max": 1500},
            "long": {"min": 2000, "max": 4000}
        }
        expected = length_map.get(length, {"min": 0, "max": 10000})
        
        if expected["min"] <= word_count <= expected["max"]:
            print(f"   ✅ 字数符合 P10 标准 ({expected['min']}-{expected['max']})")
        else:
            print(f"   ⚠️ 字数偏差 (预期 {expected['min']}-{expected['max']})")
        
        # Agent 调用统计
        print(f"\n📈 Agent 调用统计:")
        agent_counts = {}
        for item in agent_timeline:
            agent = item["agent"]
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        for agent, count in agent_counts.items():
            print(f"   {agent}: {count}x")
        
        # 内容预览
        if content:
            print(f"\n📝 内容预览 (前300字):")
            print("-"*50)
            print(content[:300])
            print("...")
            
        return {
            "length": length,
            "word_count": word_count,
            "elapsed": elapsed,
            "content": content,
            "thinking_steps": thinking_steps,
            "agent_timeline": agent_timeline
        }
        
    except requests.exceptions.Timeout:
        print(f"   ⏰ 请求超时 (>600秒)")
        return None
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*70)
    print("  Web3 话题完整写作流程测试 - 增强监控版")
    print(f"  话题: {TOPIC}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = []
    
    for length in ["short", "medium", "long"]:
        result = test_with_monitoring(length)
        if result:
            results.append(result)
        else:
            print(f"\n⚠️ {length} 测试失败，跳过")
        
        if length != "long":
            print(f"\n⏳ 等待 5 秒后继续下一个测试...")
            time.sleep(5)
    
    # 最终汇总
    print("\n" + "="*70)
    print("  测试结果汇总")
    print("="*70)
    
    print(f"\n{'篇幅':<10} {'字数':<10} {'耗时':<12} {'P10验证':<10}")
    print("-"*45)
    
    for r in results:
        length_cn = {"short": "短篇", "medium": "中篇", "long": "长篇"}.get(r["length"], r["length"])
        length_map = {
            "short": {"min": 300, "max": 600},
            "medium": {"min": 800, "max": 1500},
            "long": {"min": 2000, "max": 4000}
        }
        expected = length_map.get(r["length"], {"min": 0, "max": 10000})
        status = "✅" if expected["min"] <= r["word_count"] <= expected["max"] else "⚠️"
        
        print(f"{length_cn:<10} {r['word_count']:<10} {r['elapsed']:.1f}s{'':<6} {status}")
    
    # 保存详细结果
    output_file = "web3_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        # 简化保存，避免内容太长
        save_results = []
        for r in results:
            save_results.append({
                "length": r["length"],
                "word_count": r["word_count"],
                "elapsed": r["elapsed"],
                "content": r["content"],
                "agent_timeline": r["agent_timeline"]
            })
        json.dump(save_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存到: {output_file}")
    
    return len(results) == 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
