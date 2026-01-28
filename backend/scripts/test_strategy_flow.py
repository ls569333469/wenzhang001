"""
Focused Strategy Flow Test - With Extended Timeout and Debug
"""
from playwright.sync_api import sync_playwright
import time

def test_strategy_flow():
    print("="*60)
    print("🔬 FOCUSED STRATEGY FLOW TEST")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Console log capture
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text[:100]}") if msg.type in ["error", "warn"] else None)
        
        print("\n[1] Loading page...")
        page.goto("http://localhost:3000/studio", timeout=15000)
        page.wait_for_load_state("networkidle")
        print("✅ Page loaded")
        
        print("\n[2] Entering topic...")
        textarea = page.locator("textarea").first
        textarea.fill("比特币ETF获批后对加密市场的影响")
        time.sleep(0.5)
        print("✅ Topic entered")
        
        print("\n[3] Clicking generate button...")
        gen_btn = page.locator("button:has-text('开始'), button:has-text('生成'), button:has-text('创作')").first
        gen_btn.click()
        print("✅ Button clicked")
        
        print("\n[4] Waiting for strategy options (up to 90 seconds)...")
        print("    Watching for UI changes...")
        
        # Extended wait with multiple selector options
        selectors = [
            "text=方案",
            "text=选择",
            "text=角度",
            "[class*='strategy']",
            "[class*='option']",
            "text=标题"
        ]
        
        start_time = time.time()
        found = False
        
        while time.time() - start_time < 90:
            for sel in selectors:
                try:
                    elements = page.locator(sel).all()
                    if len(elements) > 0:
                        for el in elements:
                            if el.is_visible():
                                print(f"\n✅ FOUND strategy element: {sel}")
                                print(f"   Text: {el.text_content()[:100]}")
                                found = True
                                break
                except:
                    pass
                if found:
                    break
            
            if found:
                break
            
            # Check for timeline updates
            timeline = page.locator("[class*='timeline'], [class*='step'], [class*='agent']").all()
            for t in timeline:
                try:
                    text = t.text_content()
                    if text and ("思考" in text or "分析" in text or "完成" in text):
                        print(f"   Timeline: {text[:50]}...")
                except:
                    pass
            
            time.sleep(2)
            elapsed = int(time.time() - start_time)
            print(f"   Waiting... {elapsed}s", end="\r")
        
        if not found:
            print("\n❌ No strategy options found after 90 seconds")
            page.screenshot(path="strategy_test_timeout.png")
            print("📸 Screenshot saved: strategy_test_timeout.png")
        
        print("\n\n[5] Final state check...")
        page.screenshot(path="strategy_test_final.png")
        print("📸 Screenshot saved: strategy_test_final.png")
        
        print("\n👀 Browser staying open for 10 seconds...")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    test_strategy_flow()
