"""
P12 前端验证脚本 - 使用 Playwright 验证 Agent 模型配置 UI
"""
from playwright.sync_api import sync_playwright
import time

def test_frontend_agent_config():
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("=" * 60)
        print("P12 前端验证: Agent 模型配置 UI")
        print("=" * 60)
        
        # 1. 访问前端 (Next.js 默认端口 3000)
        print("\n[1] 访问 http://localhost:3000...")
        page.goto("http://localhost:3000")
        page.wait_for_load_state("networkidle")
        print("    ✅ 页面加载完成")
        
        # 2. 截图保存当前状态
        page.screenshot(path="p12_frontend_step1.png")
        print("    📸 截图已保存: p12_frontend_step1.png")
        
        # 3. 查找模型配置相关元素
        print("\n[2] 查找 Agent 模型配置 UI...")
        
        # 尝试查找配置按钮
        config_selectors = [
            "text=模型配置",
            "text=Agent Config",
            "text=配置",
            "[data-testid='model-config']",
            "button:has-text('设置')",
            "button:has-text('Settings')"
        ]
        
        config_found = False
        for selector in config_selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    print(f"    ✅ 找到配置入口: {selector}")
                    config_found = True
                    element.click()
                    time.sleep(1)
                    page.screenshot(path="p12_frontend_config.png")
                    print("    📸 截图已保存: p12_frontend_config.png")
                    break
            except:
                continue
        
        if not config_found:
            print("    ⚠️ 未找到明显的配置入口，检查页面内容...")
            # 打印页面文本内容
            page_text = page.inner_text("body")[:500]
            print(f"    页面内容预览: {page_text[:200]}...")
        
        # 4. 查找模型选择器
        print("\n[3] 查找模型选择器...")
        model_selectors = [
            "select",
            "[role='combobox']",
            "text=Gemini",
            "text=DeepSeek",
            "text=Doubao",
            "text=volcengine"
        ]
        
        for selector in model_selectors:
            try:
                elements = page.locator(selector).all()
                if elements:
                    print(f"    ✅ 找到: {selector} ({len(elements)} 个)")
            except:
                continue
        
        # 5. 最终截图
        page.screenshot(path="p12_frontend_final.png")
        print("\n    📸 最终截图已保存: p12_frontend_final.png")
        
        print("\n" + "=" * 60)
        print("验证完成！请检查截图文件。")
        print("=" * 60)
        
        # 保持浏览器打开一会儿让用户查看
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    test_frontend_agent_config()
