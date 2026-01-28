import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.writer import writer_agent

def test_writer_knowledge_integration():
    print("=== Testing Writer Knowledge Integration ===")
    
    # Mock specific knowledge that acts as a "secret key" to verify usage
    secret_knowledge = "The specific token identifier for the new project is 'BIO-X-2026'."
    
    mock_knowledge = f"""===== Web3 知识背景 (1 条相关记录) =====
--- [Web3背景 1] BioProtocol 深度分析 ---
主题: BioTech + DeSci
质量评分: 9.0
内容摘要:
BioProtocol 是一个革命性的 DeSci 项目，旨在将生物数据上链。
{secret_knowledge}
它的共识机制基于 Proof of Biology (PoB)。
"""
    
    state = {
        "raw_input": "Write a short introduction about BioProtocol.",
        "mode": "banfo",
        "narrative_type": "project_review",
        "strategy_json": '{"pain_point": "Bio data is centralized", "hook_angle": "DeSci is the future", "outline": ["Intro", "Problem", "Solution"]}',
        "web3_knowledge": mock_knowledge,
        "api_config": {
             "provider": "volcengine",
             # Assumes env vars are set for keys, otherwise will fail or need mock
        }
    }
    
    print("\n[Input State]")
    print(f"Mode: {state['mode']}")
    print(f"Knowledge Snippet: {secret_knowledge}")
    
    try:
        result = writer_agent(state)
        
        if "draft_content" in result:
            content = result["draft_content"]
            print("\n[Generated Content Preview]")
            print(content[:500] + "...")
            
            print("\n[Verification]")
            if "BIO-X-2026" in content :
                print("✅ SUCCESS: Found secret token 'BIO-X-2026' in content.")
            elif "BioProtocol" in content:
                print("⚠️ PARTIAL: Found 'BioProtocol' but maybe not the secret token. Check content manually.")
            else:
                print("❌ FAILURE: Did not find relevant keywords.")
        else:
            print(f"Error: {result.get('error')}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_writer_knowledge_integration()
