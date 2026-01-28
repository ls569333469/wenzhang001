"""
Simple button click test
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    # Capture network
    requests = []
    def on_req(r):
        if 'analyze' in r.url or 'generate' in r.url:
            requests.append(r.url)
            print(f'[REQUEST] {r.url}')
    page.on('request', on_req)
    
    page.goto('http://localhost:3000/studio')
    page.wait_for_load_state('networkidle')
    print('Page loaded')
    
    # Find and fill textarea
    textarea = page.locator('textarea').first
    textarea.fill('比特币ETF获批后对加密市场的影响')
    print('Input filled')
    time.sleep(0.5)
    
    # Find button by text
    btn = page.get_by_role("button", name="开始深度创作")
    print(f'Button count: {btn.count()}')
    
    if btn.count() > 0:
        print(f'Button visible: {btn.is_visible()}')
        print(f'Button enabled: {btn.is_enabled()}')
        
        # Click
        btn.click()
        print('Button clicked!')
    else:
        # Try alternative selector
        print('Button not found with exact text, trying alternatives...')
        all_buttons = page.locator('button').all()
        print(f'Total buttons: {len(all_buttons)}')
        for i, b in enumerate(all_buttons[:10]):
            try:
                txt = b.text_content()
                print(f'  Button {i}: {txt[:50]}')
            except:
                pass
    
    # Wait for network request
    time.sleep(5)
    print(f'Network requests captured: {len(requests)}')
    for r in requests:
        print(f'  - {r}')
    
    # Keep open
    print('Staying open 10s...')
    time.sleep(10)
    browser.close()
