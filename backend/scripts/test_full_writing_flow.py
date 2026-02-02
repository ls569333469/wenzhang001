"""
P14 完整写作流程测试 v2
正确导航到 /studio 页面并测试写作流程
"""
import time
import json
import os
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
STUDIO_URL = f"{BASE_URL}/studio"
TEST_INPUT = """【快讯】以太坊 Dencun 升级完成

以太坊主网于今日完成 Dencun 升级，引入 EIP-4844（Proto-Danksharding）。
升级后，Arbitrum、Optimism、Base 等主要 L2 的 Gas 费从平均 0.5 美元降至 0.05 美元以下。
Vitalik 表示这是以太坊扩容路线图的重要里程碑。
目前 ETH 价格 3,500 美元，24h 涨幅 5%。
"""

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def run_full_writing_test():
    """运行完整写作流程测试 v2"""
    log("=" * 70)
    log("P14 完整写作流程测试 v2")
    log("=" * 70)
    
    # 创建结果目录
    os.makedirs("test_results", exist_ok=True)
    
    with sync_playwright() as p:
        log("启动 Chromium 浏览器 (可见模式)...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # ========== Step 1: 直接导航到 Studio 页面 ==========
            log("\n📍 Step 1: 直接导航到 Studio 页面")
            page.goto(STUDIO_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            page.screenshot(path="test_results/v2_01_studio.png")
            log(f"  ✅ 页面标题: {page.title()}")
            log(f"  ✅ 当前URL: {page.url}")
            
            # ========== Step 2: 分析页面结构 ==========
            log("\n📍 Step 2: 分析 Studio 页面结构")
            
            # 获取所有可见的按钮
            buttons = page.locator("button:visible")
            button_count = buttons.count()
            log(f"  可见按钮数: {button_count}")
            for i in range(min(button_count, 8)):
                try:
                    text = buttons.nth(i).inner_text().strip()[:40]
                    if text:
                        log(f"    按钮 {i+1}: '{text}'")
                except:
                    pass
            
            # 获取所有 textarea
            textareas = page.locator("textarea:visible")
            ta_count = textareas.count()
            log(f"  可见 textarea 数: {ta_count}")
            
            # 获取所有 input
            inputs = page.locator("input:visible")
            input_count = inputs.count()
            log(f"  可见 input 数: {input_count}")
            
            page.screenshot(path="test_results/v2_02_structure.png")
            
            # ========== Step 3: 输入素材 ==========
            log("\n📍 Step 3: 输入素材")
            
            input_success = False
            
            # 方法1: textarea
            if ta_count > 0:
                textarea = textareas.first
                textarea.click()
                textarea.fill(TEST_INPUT)
                log(f"  ✅ 通过 textarea 输入成功")
                input_success = True
            
            # 方法2: contenteditable
            if not input_success:
                editables = page.locator("[contenteditable='true']:visible")
                if editables.count() > 0:
                    editables.first.click()
                    editables.first.fill(TEST_INPUT)
                    log(f"  ✅ 通过 contenteditable 输入成功")
                    input_success = True
            
            # 方法3: 任何 placeholder 带"输入"的元素
            if not input_success:
                placeholder_el = page.locator("[placeholder*='输入']:visible, [placeholder*='素材']:visible").first
                if placeholder_el.count() > 0:
                    placeholder_el.click()
                    placeholder_el.fill(TEST_INPUT)
                    log(f"  ✅ 通过 placeholder 匹配输入成功")
                    input_success = True
            
            if not input_success:
                log("  ⚠️ 未找到输入区域!")
            
            time.sleep(0.5)
            page.screenshot(path="test_results/v2_03_input.png")
            
            # ========== Step 4: 寻找并点击生成按钮 ==========
            log("\n📍 Step 4: 寻找生成按钮")
            
            # 按钮选择器优先级
            btn_selectors = [
                "button:has-text('开始创作')",
                "button:has-text('生成')",
                "button:has-text('创作')",
                "button:has-text('Start')",
                "button:has-text('Generate')",
                "button[type='submit']",
            ]
            
            clicked = False
            for sel in btn_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible():
                        log(f"  找到按钮: {sel}")
                        btn.click()
                        clicked = True
                        log(f"  ✅ 已点击生成按钮")
                        break
                except Exception as e:
                    continue
            
            if not clicked:
                log("  ⚠️ 未找到匹配的生成按钮，尝试使用键盘快捷键")
                page.keyboard.press("Control+Enter")
            
            page.screenshot(path="test_results/v2_04_clicked.png")
            
            # ========== Step 5: 等待生成完成 ==========
            log("\n📍 Step 5: 等待生成完成 (最多 180 秒)...")
            
            MAX_WAIT = 180
            start_time = time.time()
            last_screenshot = start_time
            screenshot_count = 0
            generation_started = False
            
            while time.time() - start_time < MAX_WAIT:
                elapsed = int(time.time() - start_time)
                
                # 检查是否有加载/生成中的指示器
                loading_indicators = [
                    page.locator("text=思考中"),
                    page.locator("text=生成中"),
                    page.locator("text=Loading"),
                    page.locator(".loading"),
                    page.locator(".spinner"),
                    page.locator("[role='progressbar']"),
                ]
                
                for indicator in loading_indicators:
                    if indicator.count() > 0:
                        if not generation_started:
                            log(f"  [{elapsed}s] 检测到生成开始!")
                            generation_started = True
                        break
                
                # 检查是否完成
                done_indicators = [
                    page.locator("text=完成"),
                    page.locator("text=PASS"),
                    page.locator("text=REFINE"),
                    page.locator(".critique-panel"),
                    page.locator("[data-status='completed']"),
                ]
                
                completed = False
                for indicator in done_indicators:
                    if indicator.count() > 0 and indicator.first.is_visible():
                        log(f"  [{elapsed}s] ✅ 检测到生成完成!")
                        completed = True
                        break
                
                if completed:
                    break
                
                # 每 20 秒截一张图
                if time.time() - last_screenshot > 20:
                    screenshot_count += 1
                    page.screenshot(path=f"test_results/v2_05_progress_{screenshot_count}.png")
                    last_screenshot = time.time()
                    log(f"  [{elapsed}s] 进度截图 #{screenshot_count}")
                
                time.sleep(3)
            
            # 最终截图
            page.screenshot(path="test_results/v2_06_final.png", full_page=True)
            
            # ========== Step 6: 提取结果 ==========
            log("\n📍 Step 6: 提取生成结果")
            
            # 获取页面主要内容区域文本
            main_content = page.locator("main").first
            if main_content.count() > 0:
                content_text = main_content.inner_text()[:1000]
                log(f"  主内容区文本长度: {len(content_text)} 字")
                log(f"  内容预览: {content_text[:200]}...")
            
            # 保存 HTML
            html = page.content()
            with open("test_results/v2_final_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            log("  已保存页面 HTML")
            
            # ========== 总结 ==========
            log("\n" + "=" * 70)
            log("📊 测试完成总结")
            log("=" * 70)
            log(f"  总耗时: {int(time.time() - start_time)} 秒")
            log(f"  截图数: {6 + screenshot_count}")
            log(f"  生成是否启动: {'是' if generation_started else '否'}")
            log(f"  截图保存: test_results/")
            
            # 保持浏览器打开
            log("\n浏览器将保持打开 15 秒供检查...")
            time.sleep(15)
            
        except Exception as e:
            log(f"❌ 测试异常: {e}")
            page.screenshot(path="test_results/v2_error.png")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()
            log("浏览器已关闭")

if __name__ == "__main__":
    run_full_writing_test()
