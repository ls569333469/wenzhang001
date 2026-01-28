"""
Comprehensive Feature Matrix Test
Tests all sidebar configuration options with visible browser

Tests:
1. 创作模式 (4 options): 深度分析, 快速摘要, 改写润色, 专业翻译
2. 篇幅长度 (3 options): 短文, 中文, 长文
3. 开头吸引力 (3+ options): 温和开头, 悬念开头, 情绪开场, 强力Hook
4. 写作风格: 咪蒙体, 半佛体, 新世相体, etc.

Usage: python backend/scripts/feature_matrix_test.py
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:3000"
TEST_TOPIC = "Web3 行业趋势分析"
SLOW_MO = 500  # Milliseconds between actions (for visibility)

class FeatureTestResult:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def log(self, category: str, feature: str, status: str, detail: str = ""):
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} [{category}] {feature}: {detail}")
        self.results.append({
            "category": category,
            "feature": feature,
            "status": status,
            "detail": detail,
            "timestamp": timestamp
        })
    
    def summary(self):
        print("\n" + "="*70)
        print("📊 FEATURE MATRIX TEST SUMMARY")
        print("="*70)
        
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"pass": 0, "fail": 0, "warn": 0}
            if r["status"] == "PASS":
                categories[cat]["pass"] += 1
            elif r["status"] == "FAIL":
                categories[cat]["fail"] += 1
            else:
                categories[cat]["warn"] += 1
        
        for cat, counts in categories.items():
            total = counts["pass"] + counts["fail"] + counts["warn"]
            print(f"\n📁 {cat}")
            print(f"   ✅ Passed: {counts['pass']}/{total}")
            if counts["fail"] > 0:
                print(f"   ❌ Failed: {counts['fail']}/{total}")
            if counts["warn"] > 0:
                print(f"   ⚠️ Warnings: {counts['warn']}/{total}")
        
        # Save to file
        with open("feature_matrix_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "test_time": self.start_time.isoformat(),
                "results": self.results,
                "summary": categories
            }, f, ensure_ascii=False, indent=2)
        print("\n📄 Results saved to: feature_matrix_results.json")


def run_feature_matrix_test():
    result = FeatureTestResult()
    
    print("="*70)
    print("🧪 COMPREHENSIVE FEATURE MATRIX TEST")
    print(f"   Target: {BASE_URL}/studio")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n⚠️ Browser will open in VISIBLE mode - watch the screen!\n")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=SLOW_MO,
            args=['--start-maximized']
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        page = context.new_page()
        
        try:
            # ==========================================
            # PHASE 0: Load Page
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 0] Loading Studio Page")
            print("="*50)
            
            page.goto(f"{BASE_URL}/studio", timeout=15000)
            page.wait_for_load_state("networkidle")
            result.log("页面加载", "Studio 页面", "PASS", "页面加载成功")
            time.sleep(1)
            
            # Take initial screenshot
            page.screenshot(path="feature_test_initial.png")
            
            # ==========================================
            # PHASE 1: 创作模式 (Creation Mode) - 4 Options
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 1] Testing 创作模式 (Creation Modes)")
            print("="*50)
            
            creation_modes = [
                ("深度分析", "深度分析"),
                ("快速摘要", "快速摘要"),
                ("改写润色", "改写润色"),
                ("专业翻译", "专业翻译")
            ]
            
            for mode_name, mode_text in creation_modes:
                try:
                    # Find the mode button/option
                    mode_btn = page.locator(f"text={mode_text}").first
                    if mode_btn.count() > 0:
                        is_visible = mode_btn.is_visible()
                        if is_visible:
                            mode_btn.click()
                            time.sleep(0.3)
                            result.log("创作模式", mode_name, "PASS", "按钮可见且可点击")
                        else:
                            result.log("创作模式", mode_name, "WARN", "按钮存在但不可见")
                    else:
                        result.log("创作模式", mode_name, "FAIL", "未找到按钮")
                except Exception as e:
                    result.log("创作模式", mode_name, "FAIL", str(e)[:50])
            
            # Reset to default (深度分析)
            try:
                page.locator("text=深度分析").first.click()
                time.sleep(0.3)
            except:
                pass
            
            # ==========================================
            # PHASE 2: 篇幅长度 (Article Length) - 3 Options
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 2] Testing 篇幅长度 (Article Length)")
            print("="*50)
            
            # Based on screenshot: 短文(~500字), 中文(~1.5k), 长文(~3k字)
            length_options = [
                ("短文", ["短文", "短篇", "~500"]),
                ("中文", ["中文", "中篇", "~1.5k", "1.5k"]),
                ("长文", ["长文", "长篇", "~3k", "3k"])
            ]
            
            for length_name, search_texts in length_options:
                found = False
                for search_text in search_texts:
                    try:
                        btn = page.locator(f"text={search_text}").first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click()
                            time.sleep(0.3)
                            result.log("篇幅长度", length_name, "PASS", f"找到并点击 '{search_text}'")
                            found = True
                            break
                    except:
                        continue
                
                if not found:
                    result.log("篇幅长度", length_name, "FAIL", "未找到匹配按钮")
            
            # ==========================================
            # PHASE 3: 开头吸引力 (Hook Style) - 3+ Options
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 3] Testing 开头吸引力 (Hook Styles)")
            print("="*50)
            
            hook_styles = [
                ("温和开头", ["温和开头", "温和"]),
                ("悬念开头", ["悬念开头", "悬念"]),
                ("情绪开场", ["情绪开场", "情绪"]),
                ("强力Hook", ["强力Hook", "强力", "Hook"])
            ]
            
            for hook_name, search_texts in hook_styles:
                found = False
                for search_text in search_texts:
                    try:
                        btn = page.locator(f"text={search_text}").first
                        if btn.count() > 0 and btn.is_visible():
                            btn.click()
                            time.sleep(0.3)
                            result.log("开头吸引力", hook_name, "PASS", f"找到并点击 '{search_text}'")
                            found = True
                            break
                    except:
                        continue
                
                if not found:
                    result.log("开头吸引力", hook_name, "WARN", "未找到按钮 (可能需滚动)")
            
            # ==========================================
            # PHASE 4: 写作风格 (Writing Styles)
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 4] Testing 写作风格 (Writing Styles)")
            print("="*50)
            
            writing_styles = [
                "咪蒙体",
                "半佛体",
                "新世相体",
                "智能媒体",
                "极客酷科",
                "硅谷华语",
                "陆公子体"
            ]
            
            for style_name in writing_styles:
                try:
                    # First scroll down sidebar if needed
                    sidebar = page.locator("aside, [class*='sidebar'], [class*='config']").first
                    if sidebar.count() > 0:
                        sidebar.evaluate("el => el.scrollTop += 100")
                    
                    btn = page.locator(f"text={style_name}").first
                    if btn.count() > 0:
                        is_visible = btn.is_visible()
                        if is_visible:
                            btn.click()
                            time.sleep(0.3)
                            result.log("写作风格", style_name, "PASS", "按钮可见且可点击")
                        else:
                            # Try scrolling to it
                            try:
                                btn.scroll_into_view_if_needed()
                                time.sleep(0.2)
                                btn.click()
                                result.log("写作风格", style_name, "PASS", "滚动后可点击")
                            except:
                                result.log("写作风格", style_name, "WARN", "存在但不可见")
                    else:
                        result.log("写作风格", style_name, "FAIL", "未找到按钮")
                except Exception as e:
                    result.log("写作风格", style_name, "FAIL", str(e)[:50])
            
            # ==========================================
            # PHASE 5: Test Generation Flow with Config
            # ==========================================
            print("\n" + "="*50)
            print("[PHASE 5] Testing Generation Flow")
            print("="*50)
            
            # Set specific config for test
            print("Setting test configuration: 中文 + 咪蒙体...")
            
            try:
                # Select 中文 length
                page.locator("text=中文").first.click()
                time.sleep(0.2)
                
                # Select 咪蒙体 style
                page.locator("text=咪蒙体").first.click()
                time.sleep(0.2)
                
                result.log("配置选择", "中文+咪蒙体", "PASS", "配置已选择")
            except Exception as e:
                result.log("配置选择", "组合测试", "FAIL", str(e)[:50])
            
            # Enter topic
            try:
                textarea = page.locator("textarea").first
                textarea.fill(TEST_TOPIC)
                result.log("话题输入", TEST_TOPIC[:20], "PASS", "话题已输入")
                time.sleep(0.5)
            except Exception as e:
                result.log("话题输入", "输入测试", "FAIL", str(e)[:50])
            
            # Click generate button
            try:
                gen_btn = page.locator("button:has-text('开始'), button:has-text('生成'), button:has-text('创作')").first
                if gen_btn.is_visible():
                    gen_btn.click()
                    result.log("生成按钮", "点击生成", "PASS", "已点击生成按钮")
                    
                    # Wait for response (with timeout)
                    print("\n⏳ Waiting for backend response (max 30s)...")
                    try:
                        # Wait for either strategy options or error
                        page.wait_for_selector(
                            "text=选择您的角度, text=方案 1, text=error, text=错误, [class*='strategy']",
                            timeout=30000
                        )
                        result.log("后端响应", "策略生成", "PASS", "收到后端响应")
                    except PlaywrightTimeout:
                        result.log("后端响应", "策略生成", "FAIL", "30秒超时 - 后端无响应")
                        page.screenshot(path="feature_test_timeout.png")
                else:
                    result.log("生成按钮", "按钮状态", "FAIL", "按钮不可见")
            except Exception as e:
                result.log("生成按钮", "生成流程", "FAIL", str(e)[:50])
            
            # Final screenshot
            page.screenshot(path="feature_test_final.png")
            print("\n📸 Screenshots saved: feature_test_initial.png, feature_test_final.png")
            
        except Exception as e:
            result.log("系统错误", "测试执行", "FAIL", str(e))
            page.screenshot(path="feature_test_error.png")
        
        finally:
            # Summary
            result.summary()
            
            # Keep browser open for user to see
            print("\n" + "="*50)
            print("👀 Browser will stay open for 10 seconds for review...")
            print("="*50)
            time.sleep(10)
            browser.close()
    
    return result


if __name__ == "__main__":
    run_feature_matrix_test()
