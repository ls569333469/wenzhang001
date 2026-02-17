"""
P24 检查点测试 — 模板独立化验证
测试所有模式的 Critic/Polisher 模板加载和渲染
"""
import sys
sys.path.insert(0, '.')

from app.core.prompts import render_prompt
from app.core.mode_configs import get_mode_config
from app.core.forbidden_patterns import load_forbidden_patterns
from app.agents.critic import get_critic, CRITIC_REGISTRY
from app.agents.polisher import get_polisher, POLISHER_REGISTRY

MODES = ["short_article", "mid_article", "long_article", "tutorial", "rewrite", "hot_take"]

SAMPLE_DRAFT = """BTC 跌破 65000 美元，24H 清算 17 亿。
多头清算 15 亿，杠杆踩踏引发链反应。
说白了，又是一群人上杠杆上到爆仓。
每次都一样的剧本，但韭菜永远不长记性。"""

def test_critic_templates():
    print("=" * 60)
    print("📋 Critic 模板渲染测试")
    print("=" * 60)
    
    results = []
    for mode in MODES:
        mode_config = get_mode_config(mode)
        scoring = mode_config.get("scoring", {})
        
        # hot_take 跳过 critic
        if mode_config.get("skip_critic", False):
            func = get_critic(mode)
            print(f"  ✅ {mode:16s} → {func.__name__} (跳过评审)")
            results.append((mode, True, "skip"))
            continue
        
        length_constraints = mode_config.get("length", {"min": 400, "max": 800, "target": 500})
        
        context = {
            "current_time_str": "2026-02-08T23:45:00",
            "mode": mode,
            "length": "thread",
            "length_constraints": length_constraints,
            "style": "auto",
            "word_count": len(SAMPLE_DRAFT),
            "draft": SAMPLE_DRAFT,
            "forbidden_patterns": load_forbidden_patterns(),
            "penalty_cap": scoring.get("penalty_cap", 30),
            "pass_threshold": scoring.get("pass_threshold", 85),
            "refine_threshold": scoring.get("refine_threshold", 70),
        }
        
        rendered = render_prompt(f"critic/{mode}", context)
        
        if rendered.startswith("Error"):
            print(f"  ❌ {mode:16s} → {rendered}")
            results.append((mode, False, rendered))
        else:
            # 检查关键内容
            has_mode = mode in rendered or "评审" in rendered
            has_draft = "BTC" in rendered
            has_threshold = str(scoring.get("pass_threshold", 85)) in rendered
            
            status = "✅" if (has_mode and has_draft and has_threshold) else "⚠️"
            print(f"  {status} {mode:16s} → {len(rendered):4d}字 | 模式标识={has_mode} | 草稿注入={has_draft} | 阈值注入={has_threshold}")
            results.append((mode, has_mode and has_draft and has_threshold, f"{len(rendered)} chars"))
    
    return results

def test_polisher_templates():
    print("\n" + "=" * 60)
    print("✨ Polisher 模板渲染测试")
    print("=" * 60)
    
    results = []
    for mode in MODES:
        mode_config = get_mode_config(mode)
        
        # hot_take, short_article 跳过 polisher
        func = get_polisher(mode)
        if func.__name__ == "skip_polisher":
            print(f"  ✅ {mode:16s} → {func.__name__} (跳过润色)")
            results.append((mode, True, "skip"))
            continue
        
        length_constraints = mode_config.get("length", {"min": 150, "max": 800, "target": 500})
        
        context = {
            "current_time_str": "2026-02-08T23:45:00",
            "draft": SAMPLE_DRAFT,
            "critique_feedback": "开头不够有力，建议加强冲击力",
            "length_constraints": length_constraints,
            "mode": mode,
            "forbidden_patterns": load_forbidden_patterns(),
        }
        
        rendered = render_prompt(f"polisher/{mode}", context)
        
        if rendered.startswith("Error"):
            print(f"  ❌ {mode:16s} → {rendered}")
            results.append((mode, False, rendered))
        else:
            has_draft = "BTC" in rendered
            has_feedback = "冲击力" in rendered
            
            status = "✅" if (has_draft and has_feedback) else "⚠️"
            print(f"  {status} {mode:16s} → {len(rendered):4d}字 | 草稿注入={has_draft} | 反馈注入={has_feedback}")
            results.append((mode, has_draft and has_feedback, f"{len(rendered)} chars"))
    
    return results

def test_registries():
    print("\n" + "=" * 60)
    print("🗂️  Registry 完整性测试")
    print("=" * 60)
    
    all_ok = True
    for mode in MODES:
        critic_func = get_critic(mode)
        polisher_func = get_polisher(mode)
        
        # 检查是否是显式注册（不是 fallback）
        critic_registered = mode in CRITIC_REGISTRY
        polisher_registered = mode in POLISHER_REGISTRY
        
        status = "✅" if (critic_registered and polisher_registered) else "⚠️"
        if not critic_registered or not polisher_registered:
            all_ok = False
        
        print(f"  {status} {mode:16s} → critic={critic_func.__name__} ({'注册' if critic_registered else '❌ FALLBACK'}) | polisher={polisher_func.__name__} ({'注册' if polisher_registered else '❌ FALLBACK'})")
    
    return all_ok

if __name__ == "__main__":
    print("🔍 P24 检查点测试 — 模板独立化验证\n")
    
    critic_results = test_critic_templates()
    polisher_results = test_polisher_templates()
    registry_ok = test_registries()
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 测试汇总")
    print("=" * 60)
    
    critic_pass = sum(1 for _, ok, _ in critic_results if ok)
    polisher_pass = sum(1 for _, ok, _ in polisher_results if ok)
    
    print(f"  Critic 模板:   {critic_pass}/{len(critic_results)} 通过")
    print(f"  Polisher 模板: {polisher_pass}/{len(polisher_results)} 通过")
    print(f"  Registry:      {'✅ 全部注册' if registry_ok else '⚠️ 有缺失'}")
    
    total = critic_pass + polisher_pass + (1 if registry_ok else 0)
    expected = len(critic_results) + len(polisher_results) + 1
    
    if total == expected:
        print(f"\n🎉 全部通过 ({total}/{expected})")
    else:
        print(f"\n⚠️ 部分失败 ({total}/{expected})")
        sys.exit(1)
