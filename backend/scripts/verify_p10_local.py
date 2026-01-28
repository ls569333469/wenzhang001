from playwright.sync_api import sync_playwright
import time
import sys

def verify_issues():
    print("--- Starting Local Verification ---")
    
    with sync_playwright() as p:
        # Launch browser (headless for speed/reliability)
        try:
            print("Launching Chromium...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Verify P2: Word Count Selector
            print("\n[Verifying P2: Word Count Selector]")
            try:
                page.goto("http://localhost:3000/studio", timeout=10000)
                page.wait_for_load_state("networkidle")
                
                # Search for specific text seen in DOM report
                short_btn = page.locator("text=短篇")
                medium_btn = page.locator("text=中篇")
                
                if short_btn.count() > 0 or medium_btn.count() > 0:
                    print("✅ P2: Word Count UI FOUND.")
                    print(f"   - '短篇' button count: {short_btn.count()}")
                    print(f"   - '中篇' button count: {medium_btn.count()}")
                    # Check visibility
                    if short_btn.first.is_visible():
                        print("   - Element is VISIBLE to user.")
                    else:
                        print("   - Element is PRESENT but NOT VISIBLE (Hidden).")
                else:
                    print("❌ P2: Word Count UI NOT FOUND in DOM.")
                    # Dump page text to debug
                    print(f"   - Page Title: {page.title()}")
                    # print(f"   - Page Text (First 200 chars): {page.inner_text('body')[:200]}")
                    
            except Exception as e:
                print(f"❌ P2 Verification Error: {e}")

            # 2. Verify P1: Timeline Details (Code Check)
            print("\n[Verifying P1: Timeline Logic]")
            try:
                with open("frontend/src/features/agent/stores/useAgentStore.ts", "r", encoding="utf-8") as f:
                    content = f.read()
                    if "steps[stepIndex].subSteps =" in content or "steps[stepIndex].subSteps = [" in content:
                        print("✅ P1: useAgentStore.ts logic confirmed (Appends to subSteps).")
                    else:
                        print("❌ P1 Check Failed: Sub-step logic missing in useAgentStore.ts")
            except Exception as e:
                print(f"❌ P1 Read Error: {e}")
            
            # 3. Verify P0: Title Diversity (Code Check)
            print("\n[Verifying P0: Title Diversity]")
            try:
                with open("backend/app/agents/strategist.py", "r", encoding="utf-8") as f:
                    content = f.read()
                    if "temperature=0.7" in content:
                        print("✅ P0: Strategist Temperature is 0.7 (FIXED).")
                    elif "temperature=0.2" in content:
                        print("❌ P0: Temperature is still 0.2 (Failed).")
                    else:
                        print("⚠️ P0: Temperature value unclear.")
                        
                    if "3 DISTINCT and CREATIVE options" in content:
                         print("✅ P0: Prompt instructions updated for diversity.")
                    else:
                         print("❌ P0: Prompt missing diversity instructions.")
            except Exception as e:
                print(f"❌ P0 Read Error: {e}")

        except Exception as e:
            print(f"Fatal Error: {e}")
        finally:
            browser.close()
            print("\n--- Verification Finished ---")

if __name__ == "__main__":
    verify_issues()
