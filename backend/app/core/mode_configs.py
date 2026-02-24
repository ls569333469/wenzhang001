"""
创作模式配置 - 集中管理所有模式参数
P14 模式模块化架构
"""

# 评分维度定义
SCORING_DIMENSIONS = [
    {"id": "accuracy", "name": "语义保真度/专业准确", "weight": 35, 
     "desc": "事实/数据/机制是否严谨？引用来源可靠？有无偏差或误导？"},
    {"id": "depth", "name": "信息价值&深度", "weight": 25,
     "desc": "有独到洞察/新角度/干货吗？信息密度如何？是否浅尝辄止？"},
    {"id": "logic", "name": "逻辑连贯性&结构完整", "weight": 15,
     "desc": "观点链条清晰？层层递进、无跳跃？首尾呼应？"},
    {"id": "tone", "name": "语言流畅度&调性一致", "weight": 15,
     "desc": "自然流畅？匹配作者风格？无AI生硬感？"},
    {"id": "originality", "name": "原创表观度/去AI痕迹", "weight": 10,
     "desc": "像人工精修？无高频套话(众所周知/值得一提)？无模板痕迹？"}
]

# 惩罚项定义
PENALTY_RULES = [
    {"id": "fact_error", "name": "事实错误", "range": [-10, -30],
     "levels": [
         {"trigger": "小数据偏差", "points": -10},
         {"trigger": "中等错误", "points": -20},
         {"trigger": "严重误导", "points": -30}
     ]},
    {"id": "ai_trace", "name": "AI痕迹高", "range": [-8, -25],
     "levels": [
         {"trigger": "高频套话≥2个", "points": -8},
         {"trigger": "明显模板", "points": -25}
     ]},
    {"id": "minor_issue", "name": "轻微问题", "range": [0, -5],
     "levels": [
         {"trigger": "小瑕疵，鼓励迭代", "points": -3},
         {"trigger": "可忽略问题", "points": 0}
     ]}
]

# 模式配置
MODE_CONFIGS = {
    "hot_take": {
        "name": "锐评/Alpha",
        "length": {"min": 50, "max": 150, "target": 80},
        "length_locked": True,
        "skip_strategist": True,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 3,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 25,
            "max_revisions": 1,
            "pass_threshold": 80,
            "refine_threshold": 65
        }
    },
    "short_article": {  # P22: 短篇 (正常X/Twitter发文)
        "name": "短篇",
        "length": {"min": 50, "max": 300, "target": 200},
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,  # P26: 审核已开启，作为发布前最终把关
        "skip_polisher": False,  # P26: 开启润色（代码预扫+LLM最小修复）
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 25,
            "max_revisions": 1,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    },
    # P16.1: 移除 mid_take 冗余配置，已通过 MODE_ALIASES 映射到 mid_article
    "mid_article": {  # P16: 中篇 (原 mid_take / quick_summary)
        "name": "中篇",
        "length": {"min": 150, "max": 800, "target": 500},  # P14: 中篇字数 150-800
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 30,
            "max_revisions": 2,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    },
    "long_article": {  # P16: 长篇 (原 deep_analysis)
        "name": "长篇",
        "length": {"min": 900, "max": 1800, "target": 1200},  # 深度分析的字数
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 45,
            "max_revisions": 3,
            "pass_threshold": 90,
            "refine_threshold": 80
        }
    },
    "tutorial": {
        "name": "教程指南",
        "length": {"min": 400, "max": 1500, "target": 800},
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 30,
            "max_revisions": 2,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    },
    "bullish_take": {
        "name": "吹捧模式",
        "length": {"min": 100, "max": 300, "target": 200},
        "length_locked": False,
        "skip_strategist": False,  # P30: 启用策略师（对齐P29短篇架构）
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 3,  # P30: 3版本输出
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 25,
            "max_revisions": 1,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    },
    "kaito_yap": {
        "name": "Kaito 嘴撸模式",
        "length": {"min": 150, "max": 400, "target": 250},
        "length_locked": False,
        "skip_strategist": True,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 25,
            "max_revisions": 1,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    },
    "project_research": {
        "name": "投研分析",
        "length": {"min": 800, "max": 1500, "target": 1000},
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 35,
            "max_revisions": 2,
            "pass_threshold": 85,
            "refine_threshold": 75
        }
    }
}

# P18: 移除 MODE_ALIASES - Clean Break 策略
# 旧模式名不再兼容，前端需同步更新
# 已移除: quick_summary, deep_analysis, mid_take, quick_take


def get_mode_config(mode: str) -> dict:
    """获取模式配置 (P18: 无兼容映射)"""
    return MODE_CONFIGS.get(mode, MODE_CONFIGS["mid_article"])

