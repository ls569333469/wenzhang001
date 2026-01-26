"""临时测试脚本 - 验证 Web2 分支逻辑"""
import sys
from pathlib import Path

# 模拟主脚本逻辑
def test_web2_branch():
    # 模拟 args
    class Args:
        path = "data/Web2风格/mimeng"
        target = "web2"
        author = "咪蒙"
        style = "mimeng"
    
    args = Args()
    custom_path = Path(args.path)
    
    print(f"args.target = {repr(args.target)}")
    print(f"args.target == 'web2': {args.target == 'web2'}")
    
    if args.target == "web2":
        print("✅ Web2 分支执行!")
        author = args.author if args.author else custom_path.name
        style = args.style if args.style else custom_path.name.lower()
        print(f"Author: {author}")
        print(f"Style: {style}")
        
        # 构建命令
        backend_dir = Path(__file__).parent
        cleaner_cmd = [
            sys.executable, "-m", "tools.cleaner_cli", "clean",
            "--input", str(custom_path),
            "--author", author,
            "--style", style,
            "--source-category", "Shell",
            "--provider", "deepseek",
            "--min-score", "3"
        ]
        print(f"Command: {' '.join(cleaner_cmd)}")
        return True
    else:
        print("❌ Web3 分支执行!")
        return False

if __name__ == "__main__":
    result = test_web2_branch()
    print(f"\n测试结果: {'通过' if result else '失败'}")
