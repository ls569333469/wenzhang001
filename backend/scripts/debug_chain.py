"""
完整链路调试：追踪短篇/长篇生成过程
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import json
import requests
import time

BASE_URL = "http://localhost:8000"
TOPIC = "前 Coinbase CTO：实物黄金并非对冲美元危机的最佳品种，比特币更具抗审查优势"

def debug_single_request(length: str):
    """发起单个请求并详细记录"""
    print(f"\n{'='*70}")
    print(f"  详细链路调试: {length}")
    print(f"{'='*70}")
    
    payload = {
        "input": TOPIC,
        "mode": "deep_analysis",
        "style": "banfo",
        "length": length
    }
    
    print(f"\n📋 请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    # 收集所有 SSE 事件
    all_events = []
    content = ""
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json=payload,
            stream=True,
            timeout=300
        )
        
        start = time.time()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])
                        event_type = data.get("type", "")
                        
                        timestamp = time.time() - start
                        
                        # 记录事件
                        event = {
                            "time": f"{timestamp:.1f}s",
                            "type": event_type,
                            "data": data
                        }
                        all_events.append(event)
                        
                        # 打印关键事件
                        if event_type == "thinking_step":
                            agent = data.get("agent", "")
                            step = data.get("step", "")
                            detail = data.get("detail", "")[:60]
                            print(f"  [{timestamp:5.1f}s] {agent:12} | {step:15} | {detail}")
                            
                        elif event_type == "agent_update":
                            agent = data.get("step", "")
                            logs = data.get("logs", [])
                            print(f"  [{timestamp:5.1f}s] ✅ {agent} 完成")
                            # 显示日志
                            for log in logs[:2]:
                                print(f"           └─ {log[:70]}")
                                
                        elif event_type == "final_result":
                            content = data.get("payload", "")
                            print(f"  [{timestamp:5.1f}s] 📝 最终内容: {len(content)} 字")
                            
                        elif event_type == "samples_loaded":
                            samples = data.get("samples", [])
                            print(f"  [{timestamp:5.1f}s] 📊 素材加载: {len(samples)} 条")
                            for i, s in enumerate(samples, 1):
                                title = s.get("title", "")[:30]
                                logic = s.get("logic_pattern", "无")[:30]
                                print(f"           样本{i}: [{logic}] {title}")
                                
                    except json.JSONDecodeError:
                        continue
                        
        elapsed = time.time() - start
        print(f"\n⏱️ 总耗时: {elapsed:.1f}秒")
        
        # 保存详细事件
        output = {
            "length": length,
            "elapsed": elapsed,
            "word_count": len(content),
            "content_preview": content[:500] if content else "无内容",
            "events_count": len(all_events),
            "events": all_events
        }
        
        return output
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_samples_directly():
    """直接检查 Google Sheets 样本"""
    print("\n" + "="*70)
    print("  Google Sheets 素材数据详情")
    print("="*70)
    
    from app.services.google_sheets_source import GoogleSheetsDataSource
    from app.services.sample_service import sample_service
    
    # 强制使用 Google Sheets
    sample_service.set_source_mode("google_sheets")
    
    gs = GoogleSheetsDataSource()
    
    for style in ["banfo", "mimeng"]:
        print(f"\n--- {style} 工作表 ---")
        
        # 加载数据
        if style not in gs._cache:
            gs._cache[style] = gs._load_sheet_data(style)
        
        records = gs._cache.get(style, [])
        print(f"总行数: {len(records)}")
        
        if records:
            # 显示字段
            print(f"字段: {list(records[0].keys())}")
            
            # 显示前 3 条
            for i, r in enumerate(records[:3], 1):
                content = r.get("content", "")[:80]
                logic = r.get("logic_pattern", "无")
                print(f"\n  行 {i}:")
                print(f"    逻辑公式: {logic}")
                print(f"    内容: {content}...")

def main():
    # 先检查素材数据
    check_samples_directly()
    
    # 运行短篇调试 (不运行完整生成，只获取素材信息)
    print("\n\n" + "="*70)
    print("  注意: 完整生成测试已在之前完成")
    print("  上次测试结果:")
    print("  - 短篇: 492字, 3轮修订 (62→75→62分)")
    print("  - 中篇: 1313字, 1次通过 (94分)")
    print("  - 长篇: 失败 (Writer返回0字)")
    print("="*70)

if __name__ == "__main__":
    main()
