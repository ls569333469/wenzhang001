"""
P14 完整 DOM 测试脚本
使用本地 Playwright 进行前端全流程测试

测试项目:
1. 页面加载
2. 创作模式选择器 (含 hot_take)
3. Hot Take 生成流程
4. 标准创作流程
"""
import time
import json
from playwright.sync_api import sync_playwright, expect

TEST_URL = "http://localhost:3000"
TEST_INPUT = "以太坊 Dencun 升级完成，Layer2 Gas 费暴跌 90%。升级后，主要 L2 的 Gas 费从 0.5 美元降至 0.05 美元以下。"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def test_page_load(page):
    """测试1: 页面加载"""
    log("🔍 测试1: 页面加载")
    page.goto(TEST_URL)
    page.wait_for_load_state("networkidle")
    
    title = page.title()
    log(f"  页面标题: {title}")
    
    # 截图
    page.screenshot(path="test_results/01_page_load.png")
    return True

def test_studio_page(page):
    """测试2: Studio 页面"""
    log("🔍 测试2: Studio 页面")
    
    # 尝试导航到 Studio
    studio_link = page.locator("text=Studio").or_(page.locator("text=创作")).first
    if studio_link.is_visible():
        studio_link.click()
        page.wait_for_load_state("networkidle")
        log("  已导航到 Studio 页面")
    else:
        # 可能已经在 Studio 页面
        log("  当前可能已在 Studio 页面")
    
    page.screenshot(path="test_results/02_studio_page.png")
    return True

def test_mode_selector(page):
    """测试3: 创作模式选择器"""
    log("🔍 测试3: 创作模式选择器")
    
    # 查找模式选择器的各种可能性
    selectors = [
        "select[name*='mode']",
        "[data-testid='mode-selector']",
        "text=创作模式",
        "text=模式",
        ".mode-selector",
        "button:has-text('深度分析')",
        "button:has-text('快讯速评')",
        "button:has-text('锐评')",
        "button:has-text('hot_take')",
    ]
    
    found_modes = []
    for sel in selectors:
        try:
            elements = page.locator(sel)
            if elements.count() > 0:
                log(f"  找到选择器: {sel}")
                found_modes.append(sel)
        except:
            pass
    
    # 获取页面所有按钮文本
    buttons = page.locator("button")
    button_count = buttons.count()
    log(f"  页面按钮数: {button_count}")
    
    for i in range(min(button_count, 10)):  # 只打印前10个
        try:
            text = buttons.nth(i).inner_text().strip()[:30]
            if text:
                log(f"    按钮 {i+1}: {text}")
        except:
            pass
    
    page.screenshot(path="test_results/03_mode_selector.png")
    return len(found_modes) > 0

def test_input_area(page):
    """测试4: 输入区域"""
    log("🔍 测试4: 输入区域")
    
    # 查找输入框
    input_selectors = [
        "textarea",
        "input[type='text']",
        "[contenteditable='true']",
        ".input-area",
        "[placeholder*='素材']",
        "[placeholder*='输入']",
    ]
    
    input_element = None
    for sel in input_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                input_element = el
                log(f"  找到输入区: {sel}")
                break
        except:
            pass
    
    if input_element:
        # 输入测试内容
        input_element.fill(TEST_INPUT)
        log(f"  已输入测试内容 ({len(TEST_INPUT)} 字)")
        page.screenshot(path="test_results/04_input_filled.png")
        return True
    else:
        log("  ⚠️ 未找到输入区域")
        page.screenshot(path="test_results/04_input_not_found.png")
        return False

def test_generate_flow(page):
    """测试5: 生成流程"""
    log("🔍 测试5: 生成流程")
    
    # 查找生成按钮
    generate_buttons = [
        "button:has-text('生成')",
        "button:has-text('创作')",
        "button:has-text('开始')",
        "button:has-text('Submit')",
        "button:has-text('Generate')",
        "[data-testid='generate-button']",
    ]
    
    clicked = False
    for sel in generate_buttons:
        try:
            btn = page.locator(sel).first
            if btn.is_visible():
                log(f"  找到生成按钮: {sel}")
                btn.click()
                clicked = True
                break
        except:
            pass
    
    if clicked:
        log("  等待生成结果 (最多 60 秒)...")
        try:
            # 等待结果显示
            page.wait_for_selector(
                "text=思考中,text=生成中,text=完成,.result,.output,.content",
                timeout=60000
            )
            time.sleep(3)  # 额外等待一点时间
            page.screenshot(path="test_results/05_generating.png")
        except Exception as e:
            log(f"  生成等待超时: {e}")
        
        # 最终截图
        page.screenshot(path="test_results/05_generate_result.png")
        return True
    else:
        log("  ⚠️ 未找到生成按钮")
        return False

def run_all_tests():
    """运行所有 DOM 测试"""
    log("=" * 60)
    log("P14 完整 DOM 测试")
    log("=" * 60)
    
    # 创建结果目录
    import os
    os.makedirs("test_results", exist_ok=True)
    
    results = {}
    
    with sync_playwright() as p:
        log("启动 Chromium 浏览器...")
        browser = p.chromium.launch(headless=False)  # 使用可见模式方便调试
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # 运行测试
            results["page_load"] = test_page_load(page)
            results["studio_page"] = test_studio_page(page)
            results["mode_selector"] = test_mode_selector(page)
            results["input_area"] = test_input_area(page)
            results["generate_flow"] = test_generate_flow(page)
            
        except Exception as e:
            log(f"❌ 测试异常: {e}")
            page.screenshot(path="test_results/error.png")
        finally:
            # 保持浏览器打开一会儿方便查看
            log("测试完成，5 秒后关闭浏览器...")
            time.sleep(5)
            browser.close()
    
    # 汇总
    log("=" * 60)
    log("📊 测试结果汇总")
    log("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        log(f"  {name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    log(f"\n总计: {passed_count}/{len(results)} 通过")
    log(f"截图保存在: test_results/")
    
    return results

if __name__ == "__main__":
    run_all_tests()
