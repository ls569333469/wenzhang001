"""P32-C: 完整管道测试（直接运行，不经过 uvicorn）"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

async def main():
    from app.services.daily_report_service import generate_daily_report

    print("=" * 60)
    print("  P32-C: 完整管道测试")
    print("  侦察 → 策略 → 审核 → 写手 → 配图 → 推文")
    print("=" * 60)

    result = await generate_daily_report(
        api_config={"provider": "volcengine"},
        concurrency=2,
    )

    print("\n" + "=" * 60)
    print("  管道执行完毕")
    print("=" * 60)
    print(f"Status: {result.get('status')}")
    print(f"Projects: {result.get('projects_count', 0)}")
    print(f"Elapsed: {result.get('elapsed', 0):.0f}s")

    if result.get("error"):
        print(f"Error: {result['error']}")

    if result.get("report_path"):
        print(f"Report: {result['report_path']}")

    paths = result.get("project_paths", [])
    if paths:
        print(f"Project reports: {len(paths)}")
        for p in paths:
            print(f"  {p}")

    if result.get("report_content"):
        print(f"\n--- 日报预览（前 500 字）---")
        print(result["report_content"][:500])

if __name__ == "__main__":
    asyncio.run(main())
