"""
方案 C 模拟测试：短篇深度分析
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

def test_plan_c():
    """测试方案 C 效果"""
    print("="*70)
    print("  方案 C 模拟测试：短篇深度分析")
    print(f"  话题: {TOPIC[:40]}...")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    payload = {
        "input": TOPIC,
        "mode": "deep_analysis",
        "style": "banfo",
        "length": "short"  # 测试短篇
    }
    
    print(f"\n📋 请求参数:")
    print(f"   mode: {payload['mode']}")
    print(f"   style: {payload['style']}")
    print(f"   length: {payload['length']}")
    print(f"   预期策略: 【短篇策略】聚焦单一核心观点")
    
    critic_scores = []
    content = ""
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            stream=True,
            timeout=600
        )
        
        print(f"\n🧠 执行过程:")
        print("-"*50)
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        event_type = data.get("type", "")
                        
                        timestamp = time.time() - start_time
                        
                        if event_type == "thinking_step":
                            agent = data.get("agent", "")
                            step = data.get("step", "")
                            detail = data.get("detail", "")[:50]
                            
                            # 只显示关键步骤
                            if step in ["generated", "scored", "feedback", "decision", "completed"]:
                                print(f"   [{timestamp:5.1f}s] {agent:12} | {step:15} | {detail}")
                                
                            # 记录 Critic 评分
                            if step == "scored":
                                try:
                                    score = int(detail.split(":")[1].split("/")[0].strip())
                                    critic_scores.append(score)
                                except:
                                    pass
                        
                        elif event_type == "agent_update":
                            agent = data.get("step", "")
                            status = data.get("status", "")
                            print(f"   [{timestamp:5.1f}s] ✅ {agent} - {status}")
                        
                        elif event_type == "final_result":
                            content = data.get("payload", "")
                            
                    except json.JSONDecodeError:
                        continue
        
        elapsed = time.time() - start_time
        word_count = len(content)
        
        # 结果汇总
        print(f"\n" + "="*70)
        print("  📊 测试结果")
        print("="*70)
        
        print(f"\n⏱️ 总耗时: {elapsed:.1f} 秒")
        print(f"📝 字数: {word_count} 字")
        
        # P10 验证
        if 300 <= word_count <= 600:
            print(f"✅ 字数符合 P10 短篇标准 (300-600)")
        else:
            print(f"⚠️ 字数偏差 (预期 300-600)")
        
        # Critic 评分分析
        if critic_scores:
            print(f"\n📈 Critic 评分历程: {' → '.join(map(str, critic_scores))}")
            final_score = critic_scores[-1]
            
            if final_score >= 70:
                print(f"✅ 方案 C 成功！最终评分 {final_score}/100 ≥ 70")
            else:
                print(f"⚠️ 评分仍低于 70，需进一步调优")
            
            # 与之前对比
            print(f"\n📊 对比（之前测试评分: 62→75→62）")
            if critic_scores[0] > 62:
                print(f"   ✅ 首轮评分提升: 62 → {critic_scores[0]} (+{critic_scores[0]-62})")
            else:
                print(f"   ⚠️ 首轮评分: {critic_scores[0]}")
        
        # 内容预览
        if content:
            print(f"\n📄 生成内容:")
            print("-"*50)
            print(content[:600])
            if len(content) > 600:
                print("...")
        
        return {
            "word_count": word_count,
            "elapsed": elapsed,
            "critic_scores": critic_scores,
            "content": content
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_plan_c()
