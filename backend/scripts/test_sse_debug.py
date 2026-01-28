"""
Test with console capture after frontend debug logging added
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    sse_events = []
    
    # Capture console
    def on_console(msg):
        text = msg.text
        if '[SSE]' in text:
            sse_events.append(text)
            print(f'[CONSOLE] {text[:300]}')
        elif msg.type == 'error':
            print(f'[ERROR] {text[:200]}')
    page.on('console', on_console)
    
    page.goto('http://localhost:3000/studio')
    page.wait_for_load_state('networkidle')
    print('Page loaded')
    
    # Fill and click
    textarea = page.locator('textarea').first
    textarea.fill('比特币ETF获批后对加密市场的影响')
    time.sleep(0.5)
    
    btn = page.get_by_role("button", name="开始深度创作")
    btn.click()
    print('Button clicked - watching for SSE events...')
    
    # Wait and monitor
    start = time.time()
    while time.time() - start < 90:
        elapsed = int(time.time() - start)
        
        # Check for strategy selector
        try:
            sel = page.locator('text=选择您的角度').first
            if sel.count() > 0 and sel.is_visible():
                print(f'\n✅ Strategy selector visible at {elapsed}s!')
                break
        except:
            pass
        
        print(f'  {elapsed}s...', end='\r')
        time.sleep(2)
    
    # Summary
    print(f'\n\nSSE events received: {len(sse_events)}')
    for e in sse_events:
        if 'analysis_result' in e:
            print(f'  ✅ {e[:150]}')
        else:
            print(f'  - {e[:100]}')
    
    page.screenshot(path='debug_sse.png')
    print('Screenshot: debug_sse.png')
    
    print('\nStaying open 15s...')
    time.sleep(15)
    browser.close()
