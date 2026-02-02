"""
P11 烟雾测试脚本
验证新篇幅体系 (tweet/thread/post) 是否在 UI 中正确显示
"""
from playwright.sync_api import sync_playwright
import sys

def main():
    print("🧪 P11 烟雾测试开始...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("📍 访问 http://localhost:3000/studio")
        page.goto("http://localhost:3000/studio", wait_until="networkidle")
        
        # 等待页面加载
        page.wait_for_timeout(2000)
        
        # 获取页面内容
        html_content = page.content()
        
        # 检查新的篇幅选项
        new_options = ["推文", "推文串", "帖子"]
        old_options = ["短篇", "中篇", "长文"]
        
        print("\n📋 检查篇幅选项:")
        
        found_new = []
        found_old = []
        
        for opt in new_options:
            if opt in html_content:
                found_new.append(opt)
                print(f"  ✅ 找到新选项: {opt}")
            else:
                print(f"  ❌ 未找到新选项: {opt}")
        
        for opt in old_options:
            if opt in html_content:
                found_old.append(opt)
                print(f"  ⚠️ 发现旧选项: {opt}")
        
        # 截图保存
        screenshot_path = "d:/AI_Projects/2026001/reports/测试审计/p11_smoke_test.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 截图已保存: {screenshot_path}")
        
        browser.close()
        
        # 结果判断
        print("\n" + "="*50)
        if len(found_new) == 3 and len(found_old) == 0:
            print("🎉 P11 烟雾测试通过！新篇幅体系已正确显示。")
            return 0
        elif len(found_new) > 0:
            print(f"⚠️ 部分通过: 找到 {len(found_new)}/3 个新选项")
            return 1
        else:
            print("❌ 测试失败: 未找到新的篇幅选项")
            return 1

if __name__ == "__main__":
    sys.exit(main())
