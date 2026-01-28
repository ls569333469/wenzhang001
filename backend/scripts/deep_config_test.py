"""
Deep Configuration Flow Test
Tests EACH configuration option through the FULL creation flow
Monitors: UI interaction -> Backend request -> Response -> Strategy display

Test Items:
1. 创作模式 (4): 深度分析, 快速摘要, 改写润色, 专业翻译
2. 篇幅长度 (3): 短篇, 中篇, 长文
3. 开头吸引力 (3+): 温和开头, 悬念开头, 情绪开场, 强力Hook
4. 写作风格 (3): 咪蒙体, 半佛体, 新世相体
"""
from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime

class DeepConfigTest:
    def __init__(self):
        self.results = {
            "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "creation_modes": {},
            "article_lengths": {},
            "hook_styles": {},
            "writing_styles": {},
            "full_flow_tests": [],
            "issues_found": []
        }
        self.network_requests = []
        self.console_logs = []
        
    def run_all_tests(self):
        print("="*70)
        print("🔬 DEEP CONFIGURATION FLOW TEST")
        print(f"   Time: {self.results['test_time']}")
        print("="*70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=200)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            # Setup listeners
            self.setup_listeners(page)
            
            # Load page once
            page.goto("http://localhost:3000/studio")
            page.wait_for_load_state("networkidle")
            print("✅ Page loaded\n")
            
            # Test 1: Creation Modes
            self.test_creation_modes(page)
            
            # Test 2: Article Lengths
            self.test_article_lengths(page)
            
            # Test 3: Hook Styles
            self.test_hook_styles(page)
            
            # Test 4: Writing Styles
            self.test_writing_styles(page)
            
            # Test 5: Full Flow with specific config
            self.test_full_flow(page)
            
            # Save screenshot
            page.screenshot(path="deep_config_test.png")
            
            print("\n👀 Browser staying open for 15 seconds...")
            time.sleep(15)
            browser.close()
        
        # Save results
        self.save_results()
        self.print_summary()
        
    def setup_listeners(self, page):
        def on_request(req):
            if any(x in req.url for x in ['/analyze', '/generate']):
                try:
                    body = req.post_data
                    self.network_requests.append({
                        "url": req.url,
                        "method": req.method,
                        "body": json.loads(body) if body else None,
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                    print(f"[NET] {req.method} {req.url}")
                    if body:
                        data = json.loads(body)
                        print(f"      mode={data.get('mode')}, style={data.get('style')}, length={data.get('length')}")
                except:
                    pass
        
        def on_console(msg):
            if msg.type in ['error', 'warn'] or '[SSE]' in msg.text:
                self.console_logs.append({"type": msg.type, "text": msg.text[:200]})
                if msg.type == 'error':
                    print(f"[ERROR] {msg.text[:100]}")
        
        page.on("request", on_request)
        page.on("console", on_console)
    
    def test_creation_modes(self, page):
        print("\n" + "="*50)
        print("📁 TEST 1: 创作模式 (Creation Modes)")
        print("="*50)
        
        modes = [
            ("深度分析", "deep_analysis"),
            ("快速摘要", "quick_summary"),
            ("改写润色", "rewrite"),
            ("专业翻译", "translate")
        ]
        
        for display_name, mode_id in modes:
            result = {"name": display_name, "id": mode_id, "found": False, "clickable": False, "issues": []}
            
            try:
                # Try to find the mode button
                btn = page.locator(f"text={display_name}").first
                if btn.count() > 0:
                    result["found"] = True
                    
                    # Check if visible
                    if btn.is_visible():
                        result["visible"] = True
                        
                        # Try to click (but not start flow)
                        btn.click()
                        time.sleep(0.3)
                        result["clickable"] = True
                        
                        # Check if URL updated
                        url = page.url
                        if f"mode={mode_id}" in url:
                            result["url_updated"] = True
                        else:
                            result["url_updated"] = False
                            result["issues"].append(f"URL not updated with mode={mode_id}")
                        
                        print(f"  ✅ {display_name}: 可点击, URL更新={result.get('url_updated')}")
                    else:
                        result["visible"] = False
                        result["issues"].append("Button not visible")
                        print(f"  ⚠️ {display_name}: 找到但不可见")
                else:
                    result["issues"].append("Button not found")
                    print(f"  ❌ {display_name}: 未找到")
            except Exception as e:
                result["issues"].append(str(e))
                print(f"  ❌ {display_name}: 错误 - {str(e)[:50]}")
            
            self.results["creation_modes"][display_name] = result
    
    def test_article_lengths(self, page):
        print("\n" + "="*50)
        print("📁 TEST 2: 篇幅长度 (Article Lengths)")
        print("="*50)
        
        lengths = [
            ("短篇", "short"),
            ("中篇", "medium"),
            ("长文", "long")
        ]
        
        for display_name, length_id in lengths:
            result = {"name": display_name, "id": length_id, "found": False, "issues": []}
            
            try:
                btn = page.locator(f"text={display_name}").first
                if btn.count() > 0:
                    result["found"] = True
                    
                    if btn.is_visible():
                        result["visible"] = True
                        btn.click()
                        time.sleep(0.3)
                        result["clickable"] = True
                        
                        # Check URL
                        url = page.url
                        if f"length={length_id}" in url:
                            result["url_updated"] = True
                        else:
                            result["url_updated"] = False
                            result["issues"].append(f"URL not updated with length={length_id}")
                        
                        print(f"  ✅ {display_name}: 可点击, URL更新={result.get('url_updated')}")
                    else:
                        result["visible"] = False
                        result["issues"].append("Button not visible")
                        print(f"  ⚠️ {display_name}: 找到但不可见")
                else:
                    result["issues"].append("Button not found")
                    print(f"  ❌ {display_name}: 未找到")
                    
            except Exception as e:
                result["issues"].append(str(e))
                print(f"  ❌ {display_name}: 错误 - {str(e)[:50]}")
            
            self.results["article_lengths"][display_name] = result
    
    def test_hook_styles(self, page):
        print("\n" + "="*50)
        print("📁 TEST 3: 开头吸引力 (Hook Styles)")
        print("="*50)
        
        hooks = [
            ("温和开头", "gentle"),
            ("悬念", "suspense"),
            ("情绪", "emotional"),
            ("强力Hook", "powerful")
        ]
        
        for display_name, hook_id in hooks:
            result = {"name": display_name, "id": hook_id, "found": False, "issues": []}
            
            try:
                # Hook buttons might be partial text match
                btn = page.locator(f"text={display_name}").first
                if btn.count() > 0:
                    result["found"] = True
                    
                    if btn.is_visible():
                        result["visible"] = True
                        btn.click()
                        time.sleep(0.3)
                        result["clickable"] = True
                        print(f"  ✅ {display_name}: 可点击")
                    else:
                        result["visible"] = False
                        result["issues"].append("Button not visible")
                        print(f"  ⚠️ {display_name}: 找到但不可见")
                else:
                    result["issues"].append("Button not found")
                    print(f"  ❌ {display_name}: 未找到")
                    
            except Exception as e:
                result["issues"].append(str(e))
                print(f"  ❌ {display_name}: 错误 - {str(e)[:50]}")
            
            self.results["hook_styles"][display_name] = result
    
    def test_writing_styles(self, page):
        print("\n" + "="*50)
        print("📁 TEST 4: 写作风格 (Writing Styles)")
        print("="*50)
        
        styles = [
            ("咪蒙体", "mimeng"),
            ("半佛体", "banfo"),
            ("新世相体", "xinshixiang")
        ]
        
        for display_name, style_id in styles:
            result = {"name": display_name, "id": style_id, "found": False, "issues": []}
            
            try:
                btn = page.locator(f"text={display_name}").first
                if btn.count() > 0:
                    result["found"] = True
                    
                    if btn.is_visible():
                        result["visible"] = True
                        btn.click()
                        time.sleep(0.3)
                        result["clickable"] = True
                        
                        # Check URL for style
                        url = page.url
                        if f"style={style_id}" in url:
                            result["url_updated"] = True
                        else:
                            result["url_updated"] = False
                            result["issues"].append(f"URL not updated with style={style_id}")
                        
                        print(f"  ✅ {display_name}: 可点击, URL更新={result.get('url_updated')}")
                    else:
                        result["visible"] = False
                        result["issues"].append("Button not visible")
                        print(f"  ⚠️ {display_name}: 找到但不可见")
                else:
                    result["issues"].append("Button not found in DOM")
                    print(f"  ❌ {display_name}: 未找到")
                    
            except Exception as e:
                result["issues"].append(str(e))
                print(f"  ❌ {display_name}: 错误 - {str(e)[:50]}")
            
            self.results["writing_styles"][display_name] = result
    
    def test_full_flow(self, page):
        print("\n" + "="*50)
        print("📁 TEST 5: 完整创作流程")
        print("="*50)
        
        # Test config: 深度分析 + 中篇 + 咪蒙体
        test_config = {
            "mode": "deep_analysis",
            "length": "medium",
            "style": "mimeng",
            "topic": "比特币ETF获批后对加密市场的影响"
        }
        
        flow_result = {
            "config": test_config,
            "steps": {},
            "issues": []
        }
        
        print(f"\n  配置: mode={test_config['mode']}, length={test_config['length']}, style={test_config['style']}")
        
        # Step 1: Set configuration via clicks
        print("\n  [Step 1] 设置配置...")
        try:
            # Click 深度分析
            page.locator("text=深度分析").first.click()
            time.sleep(0.2)
            # Click 中篇
            page.locator("text=中篇").first.click()
            time.sleep(0.2)
            # Click 咪蒙体
            page.locator("text=咪蒙体").first.click()
            time.sleep(0.2)
            flow_result["steps"]["config_set"] = True
            print("  ✅ 配置已设置")
        except Exception as e:
            flow_result["steps"]["config_set"] = False
            flow_result["issues"].append(f"Config set failed: {e}")
            print(f"  ❌ 配置设置失败: {e}")
        
        # Step 2: Enter topic
        print("\n  [Step 2] 输入话题...")
        try:
            textarea = page.locator("textarea").first
            textarea.fill(test_config["topic"])
            flow_result["steps"]["topic_entered"] = True
            print(f"  ✅ 话题已输入: {test_config['topic'][:30]}...")
        except Exception as e:
            flow_result["steps"]["topic_entered"] = False
            flow_result["issues"].append(f"Topic input failed: {e}")
            print(f"  ❌ 话题输入失败: {e}")
        
        # Step 3: Click generate button
        print("\n  [Step 3] 点击生成按钮...")
        self.network_requests = []  # Clear previous
        try:
            btn = page.get_by_role("button", name="开始深度创作")
            btn.click()
            flow_result["steps"]["button_clicked"] = True
            print("  ✅ 按钮已点击")
        except Exception as e:
            flow_result["steps"]["button_clicked"] = False
            flow_result["issues"].append(f"Button click failed: {e}")
            print(f"  ❌ 按钮点击失败: {e}")
            self.results["full_flow_tests"].append(flow_result)
            return
        
        # Step 4: Wait and verify backend request
        print("\n  [Step 4] 等待后端请求...")
        time.sleep(3)
        
        if len(self.network_requests) > 0:
            req = self.network_requests[-1]
            flow_result["steps"]["request_sent"] = True
            flow_result["request_data"] = req.get("body")
            
            # Verify request contains correct config
            body = req.get("body", {})
            print(f"  ✅ 请求已发送到 {req['url']}")
            print(f"     请求体: mode={body.get('mode')}")
            
            # Check what's missing
            if body.get("mode") != test_config["mode"]:
                issue = f"Mode mismatch: expected {test_config['mode']}, got {body.get('mode')}"
                flow_result["issues"].append(issue)
                print(f"  ⚠️ {issue}")
            
            # Check if style is passed
            if "style" not in body:
                issue = "Style NOT passed to backend"
                flow_result["issues"].append(issue)
                print(f"  ⚠️ {issue}")
            else:
                print(f"     请求体: style={body.get('style')}")
            
            # Check if length is passed
            if "length" not in body:
                issue = "Length NOT passed to backend"
                flow_result["issues"].append(issue)
                print(f"  ⚠️ {issue}")
            else:
                print(f"     请求体: length={body.get('length')}")
                
        else:
            flow_result["steps"]["request_sent"] = False
            flow_result["issues"].append("No network request captured")
            print("  ❌ 未捕获到网络请求")
        
        # Step 5: Wait for strategy options
        print("\n  [Step 5] 等待策略选项显示 (最多90秒)...")
        start = time.time()
        found = False
        
        while time.time() - start < 90:
            try:
                selector = page.locator("text=选择您的角度").first
                if selector.count() > 0 and selector.is_visible():
                    flow_result["steps"]["strategy_displayed"] = True
                    elapsed = int(time.time() - start)
                    print(f"  ✅ 策略选项在 {elapsed} 秒后显示")
                    found = True
                    break
            except:
                pass
            time.sleep(2)
            print(f"     等待中... {int(time.time() - start)}s", end="\r")
        
        if not found:
            flow_result["steps"]["strategy_displayed"] = False
            flow_result["issues"].append("Strategy options not displayed after 90s")
            print("\n  ❌ 策略选项未显示 (90秒超时)")
        
        self.results["full_flow_tests"].append(flow_result)
    
    def save_results(self):
        with open("deep_config_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Results saved to: deep_config_results.json")
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 SUMMARY REPORT")
        print("="*70)
        
        # Count issues
        all_issues = []
        
        for category in ["creation_modes", "article_lengths", "hook_styles", "writing_styles"]:
            for name, data in self.results[category].items():
                if data.get("issues"):
                    for issue in data["issues"]:
                        all_issues.append(f"[{category}] {name}: {issue}")
        
        for flow in self.results["full_flow_tests"]:
            for issue in flow.get("issues", []):
                all_issues.append(f"[full_flow] {issue}")
        
        print(f"\n⚠️ Issues Found: {len(all_issues)}")
        for issue in all_issues:
            print(f"   - {issue}")
        
        self.results["issues_found"] = all_issues
        
        # Re-save with issues
        with open("deep_config_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    test = DeepConfigTest()
    test.run_all_tests()
