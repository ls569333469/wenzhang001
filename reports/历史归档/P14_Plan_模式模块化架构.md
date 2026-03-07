# P14 方案 8 终版：创作模式模块化架构

**更新**: 2026-02-01 17:30  
**状态**: ✅ 审核通过 (可执行)  
**审计人**: Claude + 同事反馈 + Gemini 复查

---

## 📋 审计问题汇总 (10条)

| # | 问题 | 严重级 | 修正状态 |
|:-:|------|:------:|:--------:|
| 1 | 时效惩罚项与维度不一致 | 🔴 高 | ✅ 已修正 |
| 2 | 权重硬编码 | 🟡 中 | ✅ 已修正 |
| 3 | 维度描述太简短 | 🟡 中 | ✅ 已修正 |
| 4 | 缺少轻微问题豁免 | 🟡 中 | ✅ 已修正 |
| 5 | JSON缺少初步分/扣分明细 | 🟡 中 | ✅ 已修正 |
| 6 | 缺少模式专属阈值 | 🔴 高 | ✅ 已修正 |
| 7 | 维度数写死5 | 🟡 中 | ✅ 已参数化 |
| 8 | 惩罚项未参数化 | 🟡 中 | ✅ 已修正 |
| 9 | 未处理锐评跳过 | 🔴 高 | ✅ 已修正 |
| 10 | 缺少调试输出 | 🟢 低 | ✅ 已添加 |

---

## 📂 修正后文件结构

```
backend/data/prompts/
├── shared/
│   ├── base_critic.jinja2       # 基础评审 (参数化)
│   └── base_polisher.jinja2     # 基础润色 (参数化)
├── writer/
│   ├── hot_take.jinja2          # 锐评专用
│   ├── mid_take.jinja2          # 中篇专用
│   ├── deep_analysis.jinja2     # 深度专用
│   └── tutorial.jinja2          # 教程专用
├── critic/
│   └── critic_router.jinja2     # 评审路由
└── polisher/
    └── polisher_router.jinja2   # 润色路由

backend/app/core/
└── mode_configs.py              # 🆕 模式配置 (所有参数集中管理)
```

---

## 📊 mode_configs.py (完整版)

```python
"""
创作模式配置 - 集中管理所有模式参数
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
    {"id": "minor_issue", "name": "轻微问题", "range": [0, -5],  # 🔧 新增豁免区间
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
        "skip_critic": True,      # 🔧 锐评跳过评审
        "skip_polisher": True,
        "output_count": 3,
        "scoring": None           # 无评分
    },
    "mid_take": {
        "name": "中篇点评",
        "length": {"min": 150, "max": 800, "target": 500},
        "length_locked": False,
        "skip_strategist": False,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,  # 🔧 完整维度列表
            "penalty_rules": PENALTY_RULES,    # 🔧 完整惩罚规则
            "penalty_cap": 30,
            "max_revisions": 2,
            "pass_threshold": 85,              # 🔧 新增阈值
            "refine_threshold": 70
        }
    },
    "deep_analysis": {
        "name": "深度分析",
        "length": {"min": 900, "max": 1800, "target": 1200},
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
            "pass_threshold": 90,              # 🔧 深度阈值更高
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
    "rewrite": {
        "name": "改写润色",
        "length": None,
        "length_locked": False,
        "skip_strategist": True,
        "skip_critic": False,
        "skip_polisher": False,
        "output_count": 1,
        "scoring": {
            "dimensions": SCORING_DIMENSIONS,
            "penalty_rules": PENALTY_RULES,
            "penalty_cap": 20,
            "max_revisions": 1,
            "pass_threshold": 85,
            "refine_threshold": 70
        }
    }
}

# 🔧 模式命名兼容映射 (复查反馈新增)
MODE_ALIASES = {
    "quick_summary": "mid_take",   # 旧前端命名 → 新命名
    "quick_take": "mid_take",       # 其他旧值
}


def get_mode_config(mode: str) -> dict:
    """获取模式配置 (含兼容映射)"""
    # 兼容旧命名
    mode = MODE_ALIASES.get(mode, mode)
    return MODE_CONFIGS.get(mode, MODE_CONFIGS["mid_take"])
```

---

## 📄 base_critic.jinja2 (修正版)

```jinja2
{# 基础评审模板 - 完全参数化 #}

Current Time: {{ current_time_str }}

你是Web3+AI领域权威中文内容评审专家，评审标准基于EEAT框架扩展。

## 📋 当前评审配置
{# 🔧 调试输出 #}
{% if debug %}
[DEBUG] 模式: {{ mode_name }}
[DEBUG] 维度数: {{ dimensions | length }}
[DEBUG] 惩罚上限: {{ penalty_cap }}分
[DEBUG] PASS阈值: {{ pass_threshold }}分
{% endif %}

---

## {{ dimensions | length }}维度评分 (每维0-10分)

| 维度 | 权重 | 评分要点 |
|------|------|----------|
{% for dim in dimensions %}
| {{ loop.index }}. {{ dim.name }} | {{ dim.weight }}% | {{ dim.desc }} |
{% endfor %}

---

## 惩罚规则 (总扣分上限 {{ penalty_cap }} 分)

| 惩罚项 | 扣分区间 | 触发条件 |
|--------|----------|----------|
{% for rule in penalty_rules %}
| {{ rule.name }} | {{ rule.range[0] }}~{{ rule.range[1] }} | {% for lvl in rule.levels %}{{ lvl.trigger }}({{ lvl.points }}){% if not loop.last %}; {% endif %}{% endfor %} |
{% endfor %}

---

## 阈值说明
- **PASS**: ≥{{ pass_threshold }}分 → 进入润色
- **REFINE**: {{ refine_threshold }}-{{ pass_threshold - 1 }}分 → 精修
- **REWRITE**: <{{ refine_threshold }}分 → 重写

---

待评生成文 ({{ word_count }}字)：
{{ draft }}

## 输出格式 (仅输出JSON)
```json
{
  "dimensions": {
    {% for dim in dimensions %}
    "{{ dim.id }}": {"score": 8, "reason": "..."}{% if not loop.last %},{% endif %}
    {% endfor %}
  },
  "penalties": [
    {"item": "轻微问题", "points": -3, "detail": "第3段略显啰嗦"}
  ],
  "raw_score": 82,           // 🔧 初步分 (维度加权)
  "penalty_total": -3,       // 🔧 扣分总计
  "total_score": 79,         // 🔧 最终分
  "verdict": "REFINE",
  "suggestions": ["..."]
}
```
```

---

## 📄 critic_router.jinja2 (修正版)

```jinja2
{# 评审路由 - 根据mode加载配置 #}

{# 🔧 锐评跳过判断 #}
{% if mode == "hot_take" %}
{# 锐评模式不需要评审，直接输出 #}
{"skip": true, "reason": "锐评模式无需评审"}
{% else %}

{# 从 mode_configs 加载配置 #}
{% set config = mode_configs[mode] %}
{% set scoring = config.scoring %}

{# 注入参数到基础模板 #}
{% set dimensions = scoring.dimensions %}
{% set penalty_rules = scoring.penalty_rules %}
{% set penalty_cap = scoring.penalty_cap %}
{% set pass_threshold = scoring.pass_threshold %}
{% set refine_threshold = scoring.refine_threshold %}

{% include 'shared/base_critic.jinja2' %}

{% endif %}
```

---

## 📄 base_polisher.jinja2 (修正版)

```jinja2
{# 基础润色模板 - 参数化 #}

Current Time: {{ current_time_str }}

你是资深中文编辑，负责最终润色。

## 润色配置
- 模式: {{ mode_name }}
- 润色强度: {{ polish_level }}

---

{% if polish_level == "light" %}
## 轻度润色规则
✓ 仅修正错别字、标点
✓ 保持原文结构
✗ 不改动内容表达

{% elif polish_level == "medium" %}
## 中度润色规则
✓ 修正错别字、标点
✓ 优化不通顺的句子
✓ 删除高频套话 (众所周知、值得一提等)
✗ 不添加新内容

{% else %}
## 强力润色规则
✓ 全面优化语言表达
✓ 增强开头吸引力
✓ 优化结尾升华
✓ 删除所有AI痕迹
{% endif %}

---

⚠️ 严禁添加 (硬约束):
- 原文没有的具体价格/数据
- 任何投资建议/操作建议
- 未经证实的市场预测

---

待润色内容 ({{ word_count }}字)：
{{ content }}

直接输出润色后的完整文章，不要任何解释。
```

---

## 📊 模式矩阵 (修正版)

| 模式 | 字数 | 评分阈值 | 惩罚上限 | 修订 | 输出 |
|------|:----:|:--------:|:--------:|:----:|:----:|
| **锐评** | 50-150 | ❌ 跳过 | 0 | 0次 | 3条 |
| **中篇** | 150-800 | PASS≥85 | 30分 | 2次 | 1条 |
| **深度** | 900-1800 | PASS≥90 | 45分 | 3次 | 1条 |
| **教程** | 400-1500 | PASS≥85 | 30分 | 2次 | 1条 |
| **改写** | 无限制 | PASS≥85 | 20分 | 1次 | 1条 |

---

## 🔧 代码改动清单 (修正版)

| # | 文件 | 改动 | 工时 |
|:-:|------|------|:----:|
| 1 | `mode_configs.py` | 🆕 完整配置 (含维度/惩罚) | 40min |
| 2 | `base_critic.jinja2` | 🆕 参数化模板 | 30min |
| 3 | `critic_router.jinja2` | 🆕 含跳过判断 | 20min |
| 4 | `base_polisher.jinja2` | 🆕 参数化模板 | 20min |
| 5 | `polisher_router.jinja2` | 🆕 润色路由 | 15min |
| 6 | `hot_take.jinja2` | 🆕 锐评Writer | 30min |
| 7 | `mid_take.jinja2` | 🆕 中篇Writer | 30min |
| 8 | `deep_analysis.jinja2` | 🆕 深度Writer | 30min |
| 9 | `tutorial.jinja2` | 🆕 教程Writer | 30min |
| 10 | `graph.py` | 🔄 路由逻辑 | 40min |
| 11 | `main.py` | 🔄 API端点 | 30min |
| 12 | 前端 | 🔄 UI调整 | 45min |
| **总计** | | | **6.5h** |

---

## ✅ 审计通过检查项

- [x] 时效惩罚已删除 (维度内无时效)
- [x] 权重完全参数化
- [x] 维度描述已细化 (EEAT标准)
- [x] 轻微问题豁免区间 (0~-5)
- [x] JSON含初步分/扣分明细
- [x] 模式专属阈值 (中篇85/深度90)
- [x] 锐评跳过判断
- [x] 调试输出支持
- [x] 🆕 模式命名兼容映射 (quick_summary → mid_take)
- [x] 🆕 hot_take 独立 API 明确

---

## 📝 复查反馈 (Gemini)

### 1. 模式命名兼容

**问题**: 代码 (`graph.py`) 使用 `quick_summary`，文档使用 `mid_take`

**解决**: 在 `mode_configs.py` 添加 `MODE_ALIASES` 兼容映射

```python
MODE_ALIASES = {
    "quick_summary": "mid_take",
    "quick_take": "mid_take",
}
```

### 2. Hot Take 独立 API

**明确**: `hot_take` 走**独立极简流程**，不走 LangGraph StateGraph

```
hot_take 流程:
  /hot_take API → 直接读取 mode_configs → 调用 LLM → 返回 3 条候选

其他模式流程:
  /generate API → StateGraph → Strategist → Writer → Critic → Polisher
```

**注意**: `hot_take` 配置中的 `skip_xxx` 参数仅作标记，实际跳过逻辑在独立 API 中实现。
