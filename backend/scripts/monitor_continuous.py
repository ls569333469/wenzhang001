"""
持续监控前端创作过程 (每 5 秒刷新一次)
"""

from playwright.sync_api import sync_playwright
import time

def continuous_monitor():
    print("="*60)
    print("  持续前端监控 (Ctrl+C 停止)")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("http://localhost:3000", timeout=30000)
            
            for i in range(60):  # 监控 5 分钟
                page.reload()
                time.sleep(1)
                
                timestamp = time.strftime("%H:%M:%S")
                
                # 检查错误
                error_el = page.query_selector('[class*="error"], [class*="Error"], .toast-error, [role="alert"]')
                if error_el:
                    error_text = error_el.inner_text()[:100]
                    print(f"[{timestamp}] ❌ 错误: {error_text}")
                
                # 检查进度状态
                progress_el = page.query_selector('[class*="progress"], [class*="agent"], [class*="thinking"]')
                if progress_el:
                    progress_text = progress_el.inner_text()[:80]
                    print(f"[{timestamp}] 🧠 进度: {progress_text}")
                
                # 检查主要内容变化
                content_el = page.query_selector('textarea, [class*="editor"], [class*="content"]')
                if content_el:
                    content = content_el.inner_text()
                    if len(content) > 50:
                        print(f"[{timestamp}] 📝 内容长度: {len(content)} 字")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
        except Exception as e:
            print(f"❌ 错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    continuous_monitor()
