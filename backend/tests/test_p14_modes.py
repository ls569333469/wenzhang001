"""
P14 模式测试脚本
测试所有创作模式的后端 API 端点
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# 测试素材
TEST_INPUT = """
标题：以太坊 Dencun 升级完成，Layer2 Gas 费暴跌 90%

以太坊主网于今日完成 Dencun 升级，引入 EIP-4844（Proto-Danksharding）。
升级后，Arbitrum、Optimism、Base 等主要 L2 的 Gas 费从平均 0.5 美元降至 0.05 美元以下。
Vitalik 表示这是以太坊扩容路线图的重要里程碑。
目前 ETH 价格 3,500 美元，24h 涨幅 5%。
"""

def test_health():
    """测试健康检查"""
    print("\n" + "="*50)
    print("🏥 测试: Health Check")
    print("="*50)
    
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        result = resp.json()
        print(f"状态: {resp.status_code}")
        print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_hot_take():
    """测试锐评模式 (独立 API)"""
    print("\n" + "="*50)
    print("🔥 测试: Hot Take (锐评)")
    print("="*50)
    
    try:
        resp = requests.post(
            f"{BASE_URL}/hot_take",
            json={"input": TEST_INPUT},
            timeout=60
        )
        result = resp.json()
        print(f"状态: {resp.status_code}")
        print(f"模式: {result.get('mode')}")
        print(f"配置: {result.get('config')}")
        
        if "result" in result:
            candidates = result["result"].get("candidates", [])
            print(f"生成候选: {len(candidates)} 条")
            for c in candidates[:2]:  # 只显示前2条
                content = c.get("content", "")[:100]
                print(f"  - {content}...")
        
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_generate_mode(mode: str, length: str = "thread"):
    """测试标准创作模式 (通过 /generate/narrative)"""
    print("\n" + "="*50)
    print(f"📝 测试: {mode} (篇幅: {length})")
    print("="*50)
    
    payload = {
        "raw_input": TEST_INPUT,
        "mode": mode,
        "style": "mimeng",
        "length": length,
        "api_config": {
            "provider": "volcengine"
        }
    }
    
    try:
        # SSE 流式响应
        print("发起请求 (SSE 流)...")
        resp = requests.post(
            f"{BASE_URL}/generate/narrative",
            json=payload,
            stream=True,
            timeout=180  # 增加超时时间
        )
        
        event_types = set()
        final_content = ""
        critique_score = None
        total_events = 0
        
        for line in resp.iter_lines(decode_unicode=True):
            if line and line.startswith("data:"):
                total_events += 1
                try:
                    data = json.loads(line[5:].strip())
                    event_type = data.get("type", "unknown")
                    event_types.add(event_type)
                    
                    if event_type == "final":
                        final_content = data.get("content", "")[:200]
                    elif event_type == "critique":
                        critique_score = data.get("score")
                    elif event_type == "thinking_step":
                        agent = data.get("agent", "?")
                        step = data.get("step", "?")
                        print(f"  → [{agent}] {step}")
                        
                except json.JSONDecodeError:
                    continue
        
        print(f"总事件数: {total_events}")
        print(f"事件类型: {', '.join(event_types) if event_types else '无'}")
        print(f"评分: {critique_score}")
        if final_content:
            print(f"最终内容: {final_content[:100]}...")
        
        # 成功标准: 收到任何事件都算通过 (表示流程启动)
        success = total_events > 0
        return success
        
    except requests.exceptions.Timeout:
        print("⏰ 请求超时 (180s)")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# P14 模式完整测试")
    print("#"*60)
    
    results = {}
    
    # 1. Health Check
    results["health"] = test_health()
    
    # 2. Hot Take (独立 API)
    results["hot_take"] = test_hot_take()
    
    # 3. Mid Take / Quick Summary
    results["mid_take"] = test_generate_mode("quick_summary", "tweet")
    
    # 4. Deep Analysis
    results["deep_analysis"] = test_generate_mode("deep_analysis", "post")
    
    # 5. Tutorial
    results["tutorial"] = test_generate_mode("tutorial", "thread")
    
    # 汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n总计: {passed}/{total} 通过")
    
    return results

if __name__ == "__main__":
    run_all_tests()
