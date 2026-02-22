"""A/B Test - minimal version"""
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from app.core.llm import generate_text
from app.core.prompts import render_prompt
from app.core.forbidden_patterns import load_forbidden_patterns
from app.services.sample_service import sample_service
from datetime import datetime

TEST_MATERIAL = """Monad Labs 完成 2.25 亿美元融资，Paradigm 领投。Monad 是一个与 EVM 兼容的高性能 Layer 1 区块链，声称可以达到 10,000 TPS。该轮融资估值未披露，但据知情人士透露预计在 30 亿美元左右。此前 Monad 于 2023 年完成 1900 万美元种子轮。Paradigm 上一次在 L1 大额投资是 2021 年领投 Solana 的 3.14 亿美元融资。Monad 团队来自 Jump Trading，核心成员有高频交易系统开发经验。"""

# A: current samples (content only)
raw_samples = sample_service.get_samples(style='mimeng', count=3)
rag_a = "\n\n".join([f"--- sample {i+1} ---\n{s.get('content', '')[:2000]}" for i, s in enumerate(raw_samples)])

# B: enriched (content + emotion + logic from style_library.json)
lib_path = os.path.join(os.path.dirname(__file__), "..", "data", "style_library.json")
with open(lib_path, "r", encoding="utf-8") as f:
    lib = json.load(f)
rich = [x for x in lib if x.get("author") in ("mimeng", "咪蒙") and x.get("logic_pattern")]
import random; random.seed(42)
rich3 = random.sample(rich, min(3, len(rich)))

rag_b = "\n\n".join([
    f"--- sample {i+1} ---\ncontent: {s['content'][:500]}\nemotional_valence: {s.get('emotional_valence','N/A')}\nlogic_pattern: {s.get('logic_pattern','N/A')}"
    for i, s in enumerate(rich3)
])

# Save rag contexts for inspection
out = {"rag_a": rag_a, "rag_b": rag_b, "results": {}}

for label, rag in [("A_only_content", rag_a), ("B_enriched", rag_b)]:
    ctx = {
        "current_time_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_input": TEST_MATERIAL,
        "rag_context": rag,
        "forbidden_patterns": load_forbidden_patterns(),
    }
    sys_prompt = render_prompt("strategist/short_article", ctx)
    usr_prompt = f"[Test-{label}] please analyze and output 3 plans in JSON."
    
    t0 = time.time()
    try:
        resp = generate_text(
            prompt=usr_prompt, system_prompt=sys_prompt,
            provider="volcengine", temperature=0.85,
        )
        dt = time.time() - t0
        text = resp
        if "```json" in text: text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text: text = text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(text)
        out["results"][label] = {"time": round(dt, 1), "plans": data.get("plans", [])}
        print(f"[{label}] OK {dt:.1f}s - {len(data.get('plans',[]))} plans")
    except Exception as e:
        dt = time.time() - t0
        out["results"][label] = {"time": round(dt,1), "error": str(e)}
        print(f"[{label}] FAIL {dt:.1f}s - {e}")

# Save
with open(os.path.join(os.path.dirname(__file__), "ab_results.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("DONE - saved ab_results.json")
