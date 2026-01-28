"""
E2E Workflow Test - Deep Creation Flow Testing
Simulates real user behavior to identify broken features.

Usage: python backend/scripts/e2e_workflow_test.py
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import json

# Test Configuration
BASE_URL = "http://localhost:3000"
TEST_TOPIC = "比特币ETF获批后对加密市场的影响分析"
TIMEOUT_MS = 60000  # 60 seconds for LLM operations

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def log_pass(self, feature: str, detail: str = ""):
        print(f"✅ PASS: {feature}" + (f" - {detail}" if detail else ""))
        self.passed.append({"feature": feature, "detail": detail})
    
    def log_fail(self, feature: str, error: str):
        print(f"❌ FAIL: {feature} - {error}")
        self.failed.append({"feature": feature, "error": error})
    
    def log_warn(self, feature: str, message: str):
        print(f"⚠️ WARN: {feature} - {message}")
        self.warnings.append({"feature": feature, "message": message})
    
    def summary(self):
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\n--- Failed Features ---")
            for f in self.failed:
                print(f"  • {f['feature']}: {f['error']}")
        
        if self.warnings:
            print("\n--- Warnings ---")
            for w in self.warnings:
                print(f"  • {w['feature']}: {w['message']}")
        
        return len(self.failed) == 0


def run_e2e_test():
    result = TestResult()
    
    print("="*60)
    print("🚀 Starting E2E Workflow Test")
    print(f"   Target: {BASE_URL}")
    print(f"   Topic: {TEST_TOPIC}")
    print("="*60 + "\n")
    
    with sync_playwright() as p:
        # Launch browser (visible mode for debugging)
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        try:
            # ==========================================
            # Phase 1: Page Load & Basic UI
            # ==========================================
            print("\n[Phase 1: Page Load & Basic UI]")
            
            # Test: Homepage loads
            try:
                page.goto(f"{BASE_URL}/studio", timeout=10000)
                page.wait_for_load_state("networkidle")
                result.log_pass("Page Load", "/studio loaded successfully")
            except Exception as e:
                result.log_fail("Page Load", str(e))
                return result
            
            # Test: Main input area exists
            try:
                input_area = page.locator("textarea, [contenteditable='true'], input[type='text']").first
                if input_area.is_visible():
                    result.log_pass("Input Area", "Text input field visible")
                else:
                    result.log_fail("Input Area", "Input field not visible")
            except Exception as e:
                result.log_fail("Input Area", str(e))
            
            # Test: Word Count Selector
            try:
                short_btn = page.locator("text=短篇")
                medium_btn = page.locator("text=中篇")
                if short_btn.count() > 0 and medium_btn.count() > 0:
                    result.log_pass("Word Count Selector", "短篇/中篇 buttons found")
                else:
                    result.log_warn("Word Count Selector", "Buttons not found in initial view")
            except Exception as e:
                result.log_warn("Word Count Selector", str(e))
            
            # Test: Mode Selector
            try:
                mode_buttons = page.locator("[data-mode], button:has-text('深度分析'), button:has-text('快速摘要')")
                if mode_buttons.count() > 0:
                    result.log_pass("Mode Selector", f"Found {mode_buttons.count()} mode options")
                else:
                    result.log_warn("Mode Selector", "Mode selector not found")
            except Exception as e:
                result.log_warn("Mode Selector", str(e))
            
            # ==========================================
            # Phase 2: Input & Analysis Trigger
            # ==========================================
            print("\n[Phase 2: Input & Analysis]")
            
            # Enter topic
            try:
                # Find the main textarea
                textarea = page.locator("textarea").first
                textarea.click()
                textarea.fill(TEST_TOPIC)
                result.log_pass("Topic Input", f"Entered: {TEST_TOPIC[:30]}...")
                time.sleep(0.5)
            except Exception as e:
                result.log_fail("Topic Input", str(e))
                browser.close()
                return result
            
            # Find and click the generate/analyze button
            try:
                # Try various button selectors
                generate_btn = page.locator("button:has-text('开始'), button:has-text('生成'), button:has-text('分析'), button[type='submit']").first
                if generate_btn.is_visible():
                    generate_btn.click()
                    result.log_pass("Generate Button", "Clicked generate/analyze button")
                else:
                    result.log_fail("Generate Button", "Button not visible")
                    browser.close()
                    return result
            except Exception as e:
                result.log_fail("Generate Button", str(e))
                browser.close()
                return result
            
            # ==========================================
            # Phase 3: Wait for Strategy Options
            # ==========================================
            print("\n[Phase 3: Strategy Generation]")
            
            try:
                # Wait for strategy options to appear
                # Look for "选择您的角度" or strategy cards
                page.wait_for_selector("text=选择您的角度, text=方案 1, .strategy-card", timeout=TIMEOUT_MS)
                result.log_pass("Strategy Generation", "Strategy options received")
                
                # Check for multiple options
                options = page.locator("[class*='strategy'], [class*='option'], div:has-text('方案 1')")
                if options.count() >= 1:
                    result.log_pass("Multiple Options", f"Found {options.count()} strategy option(s)")
                else:
                    result.log_warn("Multiple Options", "Could not count strategy options")
                    
            except PlaywrightTimeout:
                result.log_fail("Strategy Generation", "Timeout waiting for strategy options (60s)")
                # Take screenshot for debugging
                page.screenshot(path="debug_strategy_timeout.png")
                result.log_warn("Debug", "Screenshot saved: debug_strategy_timeout.png")
                browser.close()
                return result
            except Exception as e:
                result.log_fail("Strategy Generation", str(e))
                browser.close()
                return result
            
            # Test: Title Candidates Display
            try:
                title_section = page.locator("text=标题, [class*='title']")
                if title_section.count() > 0:
                    result.log_pass("Title Candidates", "Title section visible")
                else:
                    result.log_warn("Title Candidates", "Title section not clearly visible")
            except Exception as e:
                result.log_warn("Title Candidates", str(e))
            
            # ==========================================
            # Phase 4: Select Strategy & Generate Content
            # ==========================================
            print("\n[Phase 4: Content Generation]")
            
            try:
                # Click first strategy option
                first_option = page.locator("div:has-text('方案 1'), [class*='strategy']:first-child, [class*='option']:first-child").first
                first_option.click()
                result.log_pass("Strategy Selection", "Clicked first strategy option")
            except Exception as e:
                result.log_fail("Strategy Selection", str(e))
                browser.close()
                return result
            
            # Wait for content generation
            try:
                # Wait for final content or writing canvas to have content
                page.wait_for_selector("[class*='canvas'] p, [class*='content'] p, .prose p, article p", timeout=TIMEOUT_MS * 2)
                result.log_pass("Content Generation", "Content appeared in canvas")
            except PlaywrightTimeout:
                result.log_fail("Content Generation", "Timeout waiting for content (120s)")
                page.screenshot(path="debug_content_timeout.png")
                browser.close()
                return result
            except Exception as e:
                result.log_fail("Content Generation", str(e))
                browser.close()
                return result
            
            # ==========================================
            # Phase 5: Timeline & Thinking Chain
            # ==========================================
            print("\n[Phase 5: Timeline Verification]")
            
            try:
                # Check if timeline shows completed steps
                completed_steps = page.locator("[class*='completed'], svg[class*='check'], text=Completed")
                if completed_steps.count() > 0:
                    result.log_pass("Timeline Steps", f"Found {completed_steps.count()} completed indicators")
                else:
                    result.log_warn("Timeline Steps", "No completed step indicators found")
                
                # Check for sub-steps (P1 fix verification)
                substeps = page.locator("[class*='substep'], [class*='sub-step'], .pl-2.border-l")
                if substeps.count() > 0:
                    result.log_pass("Timeline SubSteps (P1)", f"Found {substeps.count()} sub-step elements")
                else:
                    result.log_warn("Timeline SubSteps (P1)", "Sub-steps may not be visible (check expand)")
                    
            except Exception as e:
                result.log_warn("Timeline", str(e))
            
            # ==========================================
            # Phase 6: Export Functionality
            # ==========================================
            print("\n[Phase 6: Export Features]")
            
            try:
                # Look for export buttons
                export_md = page.locator("button:has-text('MD'), button:has-text('Markdown'), button:has-text('导出')")
                export_html = page.locator("button:has-text('HTML')")
                
                if export_md.count() > 0:
                    result.log_pass("Export MD Button", "Markdown export button found")
                else:
                    result.log_warn("Export MD Button", "MD export button not found")
                
                if export_html.count() > 0:
                    result.log_pass("Export HTML Button", "HTML export button found")
                else:
                    result.log_warn("Export HTML Button", "HTML export button not found")
                    
            except Exception as e:
                result.log_warn("Export Features", str(e))
            
            # ==========================================
            # Phase 7: Copy & Regenerate
            # ==========================================
            print("\n[Phase 7: Action Buttons]")
            
            try:
                copy_btn = page.locator("button:has-text('复制'), button:has-text('Copy')")
                regen_btn = page.locator("button:has-text('重新生成'), button:has-text('Regenerate')")
                
                if copy_btn.count() > 0:
                    result.log_pass("Copy Button", "Copy button available")
                else:
                    result.log_warn("Copy Button", "Copy button not found")
                
                if regen_btn.count() > 0:
                    result.log_pass("Regenerate Button", "Regenerate button available")
                else:
                    result.log_warn("Regenerate Button", "Regenerate button not found")
                    
            except Exception as e:
                result.log_warn("Action Buttons", str(e))
            
            # Final screenshot
            page.screenshot(path="e2e_final_state.png")
            print("\n📸 Final state screenshot saved: e2e_final_state.png")
            
        except Exception as e:
            result.log_fail("Unexpected Error", str(e))
            page.screenshot(path="debug_error.png")
        
        finally:
            # Keep browser open for 5 seconds so user can see final state
            print("\n⏳ Keeping browser open for 5 seconds...")
            time.sleep(5)
            browser.close()
    
    # Print summary
    success = result.summary()
    
    # Save results to JSON
    with open("e2e_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings,
            "success": success
        }, f, ensure_ascii=False, indent=2)
    print("\n📄 Results saved to: e2e_test_results.json")
    
    return result


if __name__ == "__main__":
    run_e2e_test()
