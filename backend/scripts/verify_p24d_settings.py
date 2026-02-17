"""
P24-D 一致性验证脚本 — 使用本地 Playwright 检查设置页 UI
运行：python backend/scripts/verify_p24d_settings.py
"""

import sys
import time
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "reports" / "测试审计" / "p24d_screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []

def log(check_id, desc, passed, detail=""):
    status = PASS if passed else FAIL
    results.append((check_id, desc, passed))
    print(f"  {status}  [{check_id}] {desc}" + (f" — {detail}" if detail else ""))

def close_modal(page):
    """Close the modal by clicking ✕ button, then fallback to overlay click"""
    try:
        # Try clicking the ✕ SVG close button
        close_btn = page.locator('button:has(svg.lucide-x)').first
        if close_btn.is_visible(timeout=1000):
            close_btn.click()
            time.sleep(0.8)
            return
    except:
        pass
    try:
        # Fallback: click the overlay backdrop
        page.locator('.fixed.inset-0').first.click(position={"x": 10, "y": 10})
        time.sleep(0.8)
    except:
        pass

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("\n🔧 P24-D Settings UI Verification\n" + "=" * 50)

        # ===== Step 0: Navigate directly to settings =====
        print("\n--- Step 0: 直接导航到设置页 ---")
        page.goto(f"{BASE_URL}/settings", timeout=15000)
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        time.sleep(3)
        print(f"  当前 URL: {page.url}")
        page.screenshot(path=str(SCREENSHOT_DIR / "01_settings_page.png"))

        # ===== CHECK 1: Find 4 agent cards =====
        print("\n--- 检查 1: 智能体卡片 ---")
        body_text = page.inner_text("body")

        checks = {
            "策略师": "按 6 种模式独立配置",
            "写手": "按 6 种模式独立配置",
            "评论家": "1 种跳过",
            "润色师": "2 种跳过",
        }
        for agent, expected in checks.items():
            found = agent in body_text and expected in body_text
            log(f"1-{agent}", f"卡片 '{agent}' 含 '{expected}'", found)

        # ===== CHECK 2: Click strategist card =====
        print("\n--- 检查 2: 策略师 Modal ---")
        try:
            # Navigate fresh to avoid stale state
            page.goto(f"{BASE_URL}/settings", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)

            card = page.locator('h3:has-text("策略师 (strategist)")').first
            card.click()
            time.sleep(2)

            modal_text = page.inner_text("body")
            mode_labels = ["锐评", "短篇", "中篇", "长篇", "教程指南", "改写润色"]
            modes_found = sum(1 for m in mode_labels if m in modal_text)
            log("2a", f"策略师 modal 含 {modes_found}/6 模式", modes_found >= 6)

            # Strategist should NOT have skip rows
            skip_count = modal_text.count("该模式不使用")
            log("2b", f"策略师无跳过行 (found {skip_count})", skip_count == 0)

            page.screenshot(path=str(SCREENSHOT_DIR / "02_strategist_modal.png"))
            close_modal(page)
        except Exception as e:
            log("2a", f"策略师 modal 测试异常: {e}", False)
            traceback.print_exc()

        # ===== CHECK 3: Click critic card =====
        print("\n--- 检查 3: 评论家 Modal ---")
        try:
            # Navigate fresh
            page.goto(f"{BASE_URL}/settings", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)

            card = page.locator('h3:has-text("评论家 (critic)")').first
            card.click()
            time.sleep(2)

            page.screenshot(path=str(SCREENSHOT_DIR / "03_critic_modal.png"))

            modal_text = page.inner_text("body")
            mode_labels = ["锐评", "短篇", "中篇", "长篇", "教程指南", "改写润色"]
            modes_found = sum(1 for m in mode_labels if m in modal_text)
            log("3a", f"评论家 modal 含 {modes_found}/6 模式行", modes_found >= 6)

            # 1 skip for critic (锐评) — 检查「该模式不使用」文本
            skip_count = modal_text.count("该模式不使用")
            log("3b", f"评论家有 {skip_count} 个跳过行 (期望 1)", skip_count == 1)

            close_modal(page)
        except Exception as e:
            log("3a", f"评论家 modal 测试异常: {e}", False)
            traceback.print_exc()

        # ===== CHECK 4: Click polisher card =====
        print("\n--- 检查 4: 润色师 Modal ---")
        try:
            # Navigate fresh
            page.goto(f"{BASE_URL}/settings", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)

            card = page.locator('h3:has-text("润色师 (polisher)")').first
            card.click()
            time.sleep(2)

            page.screenshot(path=str(SCREENSHOT_DIR / "04_polisher_modal.png"))

            modal_text = page.inner_text("body")

            # 2 skips for polisher (锐评 + 短篇) — 检查「该模式不使用」文本
            skip_count = modal_text.count("该模式不使用")
            log("4a", f"润色师有 {skip_count} 个跳过行 (期望 2)", skip_count == 2)

            close_modal(page)
        except Exception as e:
            log("4a", f"润色师 modal 测试异常: {e}", False)
            traceback.print_exc()

        # ===== CHECK 5: Scroll to Prompt Editor section =====
        print("\n--- 检查 5: 提示词编辑器标签 ---")
        try:
            page.goto(f"{BASE_URL}/settings", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            time.sleep(2)
            page.evaluate("window.scrollBy(0, 1500)")
            time.sleep(1)

            # Look for prompt tabs
            prompt_tabs = ["策略师", "评论家", "润色师"]
            for tab in prompt_tabs:
                el = page.locator(f'button:has-text("{tab}")').first
                if el.is_visible():
                    log(f"5-{tab}", f"提示词编辑区 '{tab}' tab 可见", True)
                else:
                    log(f"5-{tab}", f"提示词编辑区 '{tab}' tab 不可见", False)

            page.screenshot(path=str(SCREENSHOT_DIR / "05_prompt_editor.png"))
        except Exception as e:
            log("5", f"提示词编辑器检查异常: {e}", False)

        browser.close()

    # ===== Summary =====
    print("\n" + "=" * 50)
    passed = sum(1 for _, _, p in results if p)
    total = len(results)
    print(f"📊 结果: {passed}/{total} PASS")
    print(f"📁 截图保存至: {SCREENSHOT_DIR}")

    if passed < total:
        print("\n⚠️ 失败项:")
        for cid, desc, p in results:
            if not p:
                print(f"   [{cid}] {desc}")
        sys.exit(1)
    else:
        print("\n🎉 全部通过！")


if __name__ == "__main__":
    run_tests()
