"""
Full Flow Test - With Correct Button Selector
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    # Capture network
    requests = []
    def on_req(r):
        if 'analyze' in r.url or 'generate' in r.url:
            requests.append(r.url)
            print(f'[REQUEST] {r.method} {r.url}')
    page.on('request', on_req)
    
    def on_console(msg):
        if msg.type in ['error', 'warn'] or 'sse' in msg.text.lower() or 'analysis' in msg.text.lower():
            print(f'[CONSOLE] {msg.type}: {msg.text[:150]}')
    page.on('console', on_console)
    
    page.goto('http://localhost:3000/studio')
    page.wait_for_load_state('networkidle')
    print('✅ Page loaded')
    
    # Fill input
    textarea = page.locator('textarea').first
    textarea.fill('比特币ETF获批后对加密市场的影响分析')
    print('✅ Input filled')
    time.sleep(0.5)
    
    # Click button
    btn = page.get_by_role("button", name="开始深度创作")
    btn.click()
    print('✅ Button clicked')
    
    # Monitor for strategy options
    print('\n⏳ Waiting for strategy options (90s max)...')
    start = time.time()
    found = False
    
    while time.time() - start < 90:
        elapsed = int(time.time() - start)
        
        # Look for strategy option elements
        selectors = [
            'text=方案 1',
            'text=视角 1', 
            'text=选题方案',
            'text=请选择',
            '[data-testid*="option"]',
            '[class*="strategy-option"]',
            '[class*="option-card"]'
        ]
        
        for sel in selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0 and el.is_visible():
                    print(f'\n✅ FOUND: {sel}')
                    print(f'   Text: {el.text_content()[:100]}')
                    found = True
                    break
            except:
                pass
        
        if found:
            break
        
        # Check for timeline updates
        try:
            timeline = page.locator('[class*="timeline"], [class*="agent"]').first
            if timeline.count() > 0:
                text = timeline.text_content()
                if '完成' in text or 'completed' in text.lower():
                    print(f'\n[TIMELINE] {text[:100]}')
        except:
            pass
        
        print(f'   {elapsed}s...', end='\r')
        time.sleep(2)
    
    # Final result
    print('\n\n' + '='*50)
    if found:
        print('✅ TEST PASSED - Strategy options displayed')
    else:
        print('❌ TEST FAILED - No strategy options found')
    print(f'Network requests: {len(requests)}')
    
    page.screenshot(path='full_flow_result.png')
    print('📸 Screenshot: full_flow_result.png')
    
    print('\n👀 Browser staying open for 15s...')
    time.sleep(15)
    browser.close()
