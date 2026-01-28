"""
Deep Frontend Debug - Captures all console logs, network requests, and DOM changes
"""
from playwright.sync_api import sync_playwright
import time
import json

def debug_frontend_flow():
    print("="*70)
    print("🔬 DEEP FRONTEND DEBUG")
    print("="*70)
    
    console_logs = []
    network_requests = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        # Capture ALL console messages
        def on_console(msg):
            log_entry = {
                "type": msg.type,
                "text": msg.text[:500] if msg.text else "",
                "time": time.strftime("%H:%M:%S")
            }
            console_logs.append(log_entry)
            # Print important ones
            if msg.type in ["error", "warn"] or "SSE" in msg.text or "analysis" in msg.text.lower():
                print(f"[CONSOLE {msg.type.upper()}] {msg.text[:200]}")
        
        page.on("console", on_console)
        
        # Capture network requests
        def on_request(request):
            if "analyze" in request.url or "generate" in request.url:
                network_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "time": time.strftime("%H:%M:%S")
                })
                print(f"[NETWORK] {request.method} {request.url}")
        
        def on_response(response):
            if "analyze" in response.url or "generate" in response.url:
                print(f"[RESPONSE] {response.status} {response.url}")
        
        page.on("request", on_request)
        page.on("response", on_response)
        
        # Load page
        print("\n[1] Loading page...")
        page.goto("http://localhost:3000/studio", timeout=15000)
        page.wait_for_load_state("networkidle")
        print("✅ Page loaded")
        time.sleep(1)
        
        # Enter topic
        print("\n[2] Entering topic...")
        textarea = page.locator("textarea").first
        textarea.fill("比特币ETF获批后对加密市场的影响分析")
        time.sleep(0.5)
        print("✅ Topic entered")
        
        # Click generate
        print("\n[3] Clicking generate button...")
        gen_btn = page.locator("button:has-text('开始'), button:has-text('创作')").first
        gen_btn.click()
        print("✅ Button clicked - watching for responses...")
        
        # Extended monitoring
        print("\n[4] Monitoring for 60 seconds...")
        start = time.time()
        last_html = ""
        
        while time.time() - start < 60:
            elapsed = int(time.time() - start)
            
            # Check for DOM changes in main content area
            try:
                main_content = page.locator("main, [class*='content'], [class*='studio']").first
                current_html = main_content.inner_html()[:500] if main_content.count() > 0 else ""
                
                if current_html != last_html:
                    print(f"\n[DOM CHANGE at {elapsed}s]")
                    # Look for strategy-related content
                    if "方案" in current_html or "option" in current_html.lower():
                        print("   🎯 Strategy options detected in DOM!")
                    if "error" in current_html.lower():
                        print("   ⚠️ Error detected in DOM!")
                    last_html = current_html
            except:
                pass
            
            # Check for specific UI elements
            for selector in ["[class*='strategy']", "[class*='option']", "text=方案 1", "text=选题"]:
                try:
                    el = page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        print(f"\n✅ Found element: {selector}")
                        print(f"   Text: {el.text_content()[:100]}")
                except:
                    pass
            
            time.sleep(2)
            print(f"   {elapsed}s elapsed...", end="\r")
        
        # Final screenshot
        print("\n\n[5] Capturing final state...")
        page.screenshot(path="debug_final.png")
        print("📸 Screenshot: debug_final.png")
        
        # Dump console logs
        print("\n" + "="*50)
        print("📋 Console Log Summary")
        print("="*50)
        errors = [l for l in console_logs if l["type"] == "error"]
        warnings = [l for l in console_logs if l["type"] == "warn"]
        print(f"Total logs: {len(console_logs)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        
        if errors:
            print("\n🔴 Errors:")
            for e in errors[:5]:
                print(f"  [{e['time']}] {e['text'][:150]}")
        
        # Save full logs
        with open("debug_console_logs.json", "w", encoding="utf-8") as f:
            json.dump({"console": console_logs, "network": network_requests}, f, ensure_ascii=False, indent=2)
        print("\n📄 Full logs saved to: debug_console_logs.json")
        
        print("\n👀 Browser staying open for 10 seconds...")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    debug_frontend_flow()
