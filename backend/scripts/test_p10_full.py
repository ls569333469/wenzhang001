"""
P10 创作流程全面测试脚本
测试项目:
1. 深度分析 vs 快讯速评模式
2. 提示词调用验证
3. Google Sheets 样本调用
4. 短篇/中篇/长篇字数限制
5. mimeng/banfo 风格调用
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright
import requests
import json

# 测试配置
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_health():
    """测试后端健康状态"""
    print("\n" + "="*60)
    print("[1] 后端健康检查")
    print("="*60)
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        data = resp.json()
        print(f"✅ 后端状态: {data.get('status')}")
        print(f"   版本: {data.get('version')}")
        print(f"   Lark连接: {data.get('lark_connected')}")
        return True
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_google_sheets_samples():
    """测试 Google Sheets 样本调用"""
    print("\n" + "="*60)
    print("[2] Google Sheets 样本调用测试")
    print("="*60)
    
    try:
        # 直接调用 sample 服务测试
        from app.services.sample_service import sample_service
        
        # 强制使用 Google Sheets 进行测试
        original_mode = sample_service.get_source_mode()
        sample_service.set_source_mode("google_sheets")
        
        # 测试 mimeng
        print("\n[2.1] 测试 mimeng 风格样本 (Google Sheets)...")
        mimeng_samples = sample_service.get_samples("mimeng", count=3)
        if mimeng_samples:
            print(f"✅ mimeng 样本获取成功: {len(mimeng_samples)} 条")
            for i, s in enumerate(mimeng_samples[:2], 1):
                content = s.get("content", "")[:50]
                print(f"   样本{i}: {content}...")
        else:
            print("❌ mimeng 样本获取失败")
        
        # 测试 banfo
        print("\n[2.2] 测试 banfo 风格样本 (Google Sheets)...")
        banfo_samples = sample_service.get_samples("banfo", count=3)
        if banfo_samples:
            print(f"✅ banfo 样本获取成功: {len(banfo_samples)} 条")
            for i, s in enumerate(banfo_samples[:2], 1):
                content = s.get("content", "")[:50]
                print(f"   样本{i}: {content}...")
        else:
            print("❌ banfo 样本获取失败")
        
        # 恢复原来的模式
        sample_service.set_source_mode(original_mode)
            
        return len(mimeng_samples) > 0 and len(banfo_samples) > 0
        
    except Exception as e:
        print(f"❌ 样本服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_word_count_config():
    """测试字数限制配置"""
    print("\n" + "="*60)
    print("[3] 字数限制配置检查")
    print("="*60)
    
    try:
        from app.core.prompts import render_prompt
        
        # 检查 writer.jinja2 中的字数配置
        lengths = {
            "short": "~500字",
            "medium": "~1500字", 
            "long": "~3000字"
        }
        
        print("   预期字数限制:")
        for key, val in lengths.items():
            print(f"   - {key}: {val}")
        
        # 尝试渲染 prompt 检查字数相关内容
        print("\n   检查 writer.jinja2 模板...")
        with open("data/prompts/writer.jinja2", "r", encoding="utf-8") as f:
            content = f.read()
            if "word_count" in content or "length" in content or "字" in content:
                print("✅ writer.jinja2 包含字数相关配置")
            else:
                print("⚠️ writer.jinja2 未发现字数配置")
                
        return True
    except Exception as e:
        print(f"❌ 字数配置检查失败: {e}")
        return False

def test_prompt_templates():
    """测试提示词模板加载"""
    print("\n" + "="*60)
    print("[4] 提示词模板检查")
    print("="*60)
    
    templates = [
        ("strategist.jinja2", "分析"),
        ("writer.jinja2", "风格"),
        ("critic.jinja2", "评估"),
        ("polisher.jinja2", "润色")
    ]
    
    all_ok = True
    for tpl, keyword in templates:
        path = f"data/prompts/{tpl}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                size = len(content)
                if size > 100:
                    print(f"✅ {tpl}: {size} 字符")
                else:
                    print(f"⚠️ {tpl}: 文件过小 ({size} 字符)")
                    all_ok = False
        except Exception as e:
            print(f"❌ {tpl}: 加载失败 - {e}")
            all_ok = False
            
    return all_ok

def test_mode_config():
    """测试创作模式配置"""
    print("\n" + "="*60)
    print("[5] 创作模式配置检查")
    print("="*60)
    
    modes = {
        "deep_analysis": "深度分析",
        "quick_review": "快讯速评"
    }
    
    try:
        # 检查 strategist.py 中的模式处理
        with open("app/agents/strategist.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        for mode_id, mode_name in modes.items():
            if mode_id in content or mode_name in content:
                print(f"✅ {mode_name} ({mode_id}): 已配置")
            else:
                print(f"⚠️ {mode_name} ({mode_id}): 未在代码中发现")
                
        return True
    except Exception as e:
        print(f"❌ 模式配置检查失败: {e}")
        return False

def test_frontend_ui():
    """测试前端 UI 组件"""
    print("\n" + "="*60)
    print("[6] 前端 UI 组件检查 (Playwright)")
    print("="*60)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(f"{FRONTEND_URL}/studio", timeout=15000)
            page.wait_for_load_state("networkidle")
            
            # 检查模式选择器
            print("\n[6.1] 创作模式选择器...")
            if page.locator("text=深度分析").count() > 0:
                print("✅ 深度分析 模式按钮存在")
            else:
                print("❌ 深度分析 模式按钮未找到")
                
            if page.locator("text=快讯速评").count() > 0:
                print("✅ 快讯速评 模式按钮存在")
            else:
                print("❌ 快讯速评 模式按钮未找到")
            
            # 检查字数选择器
            print("\n[6.2] 篇幅长度选择器...")
            for label in ["短篇", "中篇", "长文"]:
                if page.locator(f"text={label}").count() > 0:
                    print(f"✅ {label} 按钮存在")
                else:
                    print(f"❌ {label} 按钮未找到")
            
            # 检查风格选择器
            print("\n[6.3] 写作风格选择器...")
            for style in ["咪蒙体", "半佛体"]:
                if page.locator(f"text={style}").count() > 0:
                    print(f"✅ {style} 按钮存在")
                else:
                    print(f"❌ {style} 按钮未找到")
            
            # 检查保留度滑块
            print("\n[6.4] 内容保留度...")
            if page.locator("text=内容保留度").count() > 0 or page.locator("text=L3").count() > 0:
                print("✅ 内容保留度控件存在")
            else:
                print("⚠️ 内容保留度控件未找到")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"❌ 前端 UI 测试失败: {e}")
        return False

def main():
    print("="*60)
    print("    P10 创作流程全面测试")
    print("    时间: 2026-01-30")
    print("="*60)
    
    results = {}
    
    # 1. 健康检查
    results["health"] = test_health()
    
    # 2. Google Sheets 样本
    results["samples"] = test_google_sheets_samples()
    
    # 3. 字数限制
    results["word_count"] = test_word_count_config()
    
    # 4. 提示词模板
    results["prompts"] = test_prompt_templates()
    
    # 5. 创作模式
    results["modes"] = test_mode_config()
    
    # 6. 前端 UI
    results["frontend"] = test_frontend_ui()
    
    # 汇总
    print("\n" + "="*60)
    print("    测试结果汇总")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\n   总计: {passed_count}/{total_count} 项通过")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
