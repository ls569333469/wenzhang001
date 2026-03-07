"""Quick Surf API connectivity test"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.services.surf_service import SurfService

print("🔍 Testing Surf API connectivity...")
s = SurfService()
r = s.call(
    model="deepseek-v3",
    user_prompt="What is Bitcoin? Reply in one sentence.",
    abilities=["search"],
)
print(f"Status: {r['status']}")
print(f"Elapsed: {r.get('elapsed', 0):.1f}s")
if r["status"] == 200:
    print(f"✅ API OK! Content: {r.get('content', '')[:200]}")
else:
    print(f"❌ API Error: {r.get('error', 'Unknown')[:300]}")
