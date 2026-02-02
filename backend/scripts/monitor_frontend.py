"""
监控前端运行状态 (本地 Playwright 脚本)
"""

from playwright.sync_api import sync_playwright
import time

def monitor_frontend():
    print("="*60)
    print("  前端状态监控")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n📡 访问 http://localhost:3000...")
            page.goto("http://localhost:3000", timeout=30000)
            time.sleep(2)
            
            # 检查页面标题
            title = page.title()
            print(f"📄 页面标题: {title}")
            
            # 检查是否有错误弹窗
            error_elements = page.query_selector_all('[class*="error"], [class*="Error"], .toast-error')
            if error_elements:
                print(f"\n❌ 发现 {len(error_elements)} 个错误元素:")
                for i, el in enumerate(error_elements):
                    text = el.inner_text()[:200] if el.inner_text() else "(空)"
                    print(f"   {i+1}. {text}")
            else:
                print("✅ 未发现明显错误元素")
            
            # 检查智能体进度
            progress_elements = page.query_selector_all('[class*="progress"], [class*="agent"], [class*="status"]')
            if progress_elements:
                print(f"\n🧠 发现 {len(progress_elements)} 个进度/状态元素")
            
            # 检查主要内容区域
            main_content = page.query_selector('main, [class*="content"], [class*="editor"]')
            if main_content:
                content_text = main_content.inner_text()[:500]
                print(f"\n📝 主内容预览:\n{content_text[:300]}...")
            
            # 截图保存
            screenshot_path = "frontend_status.png"
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"\n📸 截图已保存: {screenshot_path}")
            
        except Exception as e:
            print(f"\n❌ 监控失败: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    monitor_frontend()
