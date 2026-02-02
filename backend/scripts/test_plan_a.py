"""
测试方案 A: mode → length 强制约束
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

def test_mode_length_constraint():
    """测试 mode → length 强制约束"""
    print("="*70)
    print("  方案 A 测试: mode → length 强制约束")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 测试用例: 请求 deep_analysis + short
    # 预期: 系统自动强制使用 long
    payload = {
        "input": TOPIC,
        "mode": "deep_analysis",
        "style": "banfo",
        "length": "short"  # 故意请求 short，测试是否被强制为 long
    }
    
    print(f"\n📋 请求参数:")
    print(f"   mode: {payload['mode']}")
    print(f"   style: {payload['style']}")
    print(f"   length: {payload['length']} (请求)")
    print(f"   预期约束: deep_analysis → length=long")
    
    critic_scores = []
    content = ""
    actual_length_constraint = None
    
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
                            detail = data.get("detail", "")[:60]
                            
                            # 检查约束日志
                            if "强制约束" in detail or "length" in detail.lower():
                                print(f"   [{timestamp:5.1f}s] 🔒 {detail}")
                            
                            # 关键步骤
                            if step in ["generated", "scored", "completed"]:
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
        
        # 验证篇幅约束是否生效
        # deep_analysis 应该强制为 long (2000-4000字)
        if word_count >= 2000:
            print(f"✅ 约束生效! 字数 {word_count} 符合 long 篇幅 (2000-4000)")
        elif word_count >= 800:
            print(f"⚠️ 字数 {word_count}，接近 medium 篇幅")
        else:
            print(f"❌ 约束未生效，字数 {word_count} 仍为 short 范围")
        
        # Critic 评分分析
        if critic_scores:
            print(f"\n📈 Critic 评分历程: {' → '.join(map(str, critic_scores))}")
            final_score = critic_scores[-1]
            
            if final_score >= 70:
                print(f"✅ 评分合格！ {final_score}/100 ≥ 70")
            else:
                print(f"⚠️ 评分 {final_score}/100")
        
        # 内容预览
        if content:
            print(f"\n📄 生成内容预览:")
            print("-"*50)
            print(content[:800])
            if len(content) > 800:
                print(f"\n... (共 {word_count} 字)")
        
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
    test_mode_length_constraint()
