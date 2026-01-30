"""
Local Playwright test for P10 creation workflow
Per 20260128_浏览器子系统故障报告.md - use local Playwright, not cloud browser_subagent
"""
from playwright.sync_api import sync_playwright
import time

def test_creation_workflow():
    print("=" * 60)
    print("Local Playwright Test: P10 Creation Workflow")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False to see the browser
        page = browser.new_page()
        
        # Navigate directly to studio page
        print("\n1. Navigating to http://localhost:3000/studio...")
        page.goto("http://localhost:3000/studio", timeout=30000)
        time.sleep(3)
        
        print("2. Page loaded. Title:", page.title())
        print("   URL:", page.url)
        
        # Take screenshot of initial state
        page.screenshot(path="test_screenshot_1_studio.png")
        print("   Screenshot saved: test_screenshot_1_studio.png")
        
        # Look for input area - could be textarea, contenteditable div, or specific component
        print("\n3. Looking for input elements...")
        
        # Try multiple selectors
        textarea = page.query_selector("textarea")
        contenteditable = page.query_selector("[contenteditable='true']")
        prompt_input = page.query_selector("[data-testid='prompt-input'], .prompt-input, #prompt-input")
        
        input_element = textarea or contenteditable or prompt_input
        
        if input_element:
            print("   Found input element!")
            input_element.fill("比特币突破10万美元，创历史新高")
            print("   Filled input with text")
            page.screenshot(path="test_screenshot_2_input.png")
        else:
            print("   No direct input found, listing page structure...")
            # Debug: print all interactive elements
            all_inputs = page.query_selector_all("textarea, input[type='text'], [contenteditable]")
            print(f"   Found {len(all_inputs)} text input elements")
            all_buttons = page.query_selector_all("button")
            print(f"   Found {len(all_buttons)} buttons")
        
        # Look for generate button
        print("\n4. Looking for generate button...")
        buttons = page.query_selector_all("button")
        print(f"   Found {len(buttons)} buttons. Listing all:")
        
        generate_button = None
        for i, btn in enumerate(buttons):
            text = btn.inner_text().strip().replace('\n', ' ')[:40]  # Truncate long text
            print(f"      {i+1}. '{text}'")
            # Look for the specific orange button
            if "探索" in text or "开始探索" in text or ("开始" in text and "创作" in text):
                generate_button = btn
                print(f"         ^^^ This is the generate button!")
        
        if generate_button:
            print("\n   Clicking generate button...")
            generate_button.click()
            page.screenshot(path="test_screenshot_3_clicked.png")
            print("   Screenshot saved: test_screenshot_3_clicked.png")
        else:
            print("\n   ❌ Generate button not found!")
        
        # Wait for response
        print("\n5. Waiting for LLM response (90s)...")
        
        try:
            # Wait for loading to complete or timeout
            page.wait_for_timeout(90000)  # Wait 90s for LLM response
            page.screenshot(path="test_screenshot_4_result.png")
            print("   Screenshot saved: test_screenshot_4_result.png")
        except Exception as e:
            print(f"   Error during wait: {e}")
        
        print("\n6. Current URL:", page.url)
        
        # Keep browser open for manual inspection
        print("\n✅ Test complete. Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    test_creation_workflow()
