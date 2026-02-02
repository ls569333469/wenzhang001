"""
详细前端状态检查
"""

from playwright.sync_api import sync_playwright
import time

def detailed_check():
    print("="*60)
    print("  详细前端状态检查")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("\n📡 访问 http://localhost:3000/studio...")
            page.goto("http://localhost:3000/studio", timeout=30000)
            time.sleep(3)
            
            # 页面标题
            print(f"📄 页面标题: {page.title()}")
            print(f"📍 当前 URL: {page.url}")
            
            # 获取页面所有文本
            body_text = page.query_selector('body').inner_text()
            
            # 检查是否有明显错误关键词
            error_keywords = ['error', 'Error', '错误', '失败', 'failed', 'timeout', '超时']
            found_errors = []
            for kw in error_keywords:
                if kw.lower() in body_text.lower():
                    # 找到包含该关键词的行
                    for line in body_text.split('\n'):
                        if kw.lower() in line.lower() and len(line.strip()) > 0:
                            found_errors.append(line.strip()[:100])
            
            if found_errors:
                print(f"\n⚠️ 发现可能的错误信息:")
                for err in set(found_errors[:10]):
                    print(f"   - {err}")
            else:
                print("\n✅ 未发现明显错误关键词")
            
            # 检查智能体状态
            print("\n🧠 页面内容摘要:")
            lines = [l.strip() for l in body_text.split('\n') if l.strip()]
            for line in lines[:30]:
                print(f"   {line[:80]}")
            
            # 截图
            page.screenshot(path="frontend_detail.png", full_page=True)
            print(f"\n📸 完整截图: frontend_detail.png")
            
        except Exception as e:
            print(f"\n❌ 检查失败: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    detailed_check()
