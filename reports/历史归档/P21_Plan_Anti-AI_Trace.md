# P21 Anti-AI Trace 实施计划

> 目标：降低 AI 写作痕迹，使输出更自然  
> 策略：强化现有提示词，而非新增模块  
> 创建日期：2026-02-05

---

## 1. 背景

### 1.1 问题描述

当前系统输出存在"AI 味重"的问题：
- 套话频繁（众所周知、综上所述等）
- 句式单一（首先...其次...最后）
- 可预测性高（缺乏爆发性/变异性）
- 破折号过度使用（——像这样——的插入解释）

### 1.2 方案演进

| 阶段 | 方案 | 结论 |
|------|------|------|
| 初版 | 新增 Humanizer 模块 + 架构改动 | 工时 9.5h |
| 深度分析 | 对比现有系统 | 发现 70% 功能已存在 |
| **最终** | **强化现有提示词** | **工时 3h** |

---

## 2. 现有能力（无需重复实现）

| 功能 | 位置 | 状态 |
|------|------|------|
| Critic 自动循环 | `graph.py` router_logic | ✅ 已有 |
| AI 痕迹惩罚 | `mode_configs.py` PENALTY_RULES | ✅ 已有 |
| 5 维度评分 | `critic.jinja2` | ✅ 已有 |
| 170+ 禁用词 | `strategist.jinja2` | ✅ 已有 |
| Writer 禁止事项 | `mid_article.jinja2` | ✅ 已有 |

---

## 3. 实施内容

### 3.1 Critic 增强

**文件**：`backend/data/prompts/critic.jinja2`

**现状**：Step 4 只举例 3 个套话

**增强**：添加 24 项 AI 模式完整检测清单

```
Step 4: AI痕迹检测 (24 项检查)

内容模式：
- 夸大象征（"标志着..."、"深刻体现..."）
- 宣传语言（"充满活力的"、"令人叹为观止"）
- 模糊归因（"专家认为"、"行业报告显示"）
- 提纲式挑战部分（"尽管存在挑战..."）

语言模式：
- AI 高频词（此外、至关重要、深入探讨、格局）
- 系动词回避（用"作为"替代"是"）
- 否定排比（不仅...而且）
- 三段式列举（首先...其次...最后）
- 刻意换词（同一事物反复用不同词称呼）

风格模式：
- 破折号过度使用（——像这样——）
- 粗体滥用
- 表情符号过多
- 垂直列表格式

句式模式：
- 连续 3 句长度相同
- 段落以简洁单行结尾
- 虚假范围（"从 X 到 Y"但无意义对比）
```

---

### 3.2 Polisher 增强

**文件**：`backend/data/prompts/shared/base_polisher.jinja2`

**现状**：只说"删除高频套话"

**增强**：添加快速检查清单

```
## 最终检查清单 (每项必查)
✓ 连续三句长度相同？ → 打断其中一个
✓ 段落以简洁单行结尾？ → 变换结尾方式
✓ 揭示前有破折号？ → 删除它
✓ 使用了"此外""然而"？ → 考虑删除
✓ 三段式列举？ → 改为两项或四项
✓ 有解释比喻？ → 信任读者理解力
```

---

### 3.3 禁用词库集中化

**新建文件**：`backend/data/config/forbidden_patterns.yaml`

将分散在各模板的禁用词提取为独立配置文件：

```yaml
# ============================================
# P21 AI 高频禁用词库 (2025-2026 实测版)
# ============================================

# 1. 动词类 (最明显的AI痕迹)
verbs:
  zh:
    - 深入探讨
    - 深入研究
    - 赋能
    - 驱动
    - 助力
    - 提升
    - 增强
    - 革新
    - 变革
    - 转型
    - 探索
    - 启程
    - 导航
    - 揭示
    - 揭开
    - 阐明
    - 凸显
    - 利用
    - 整合
    - 优化
    - 实现
  en:
    - delve / delve into
    - empower
    - drive
    - elevate
    - enhance
    - foster
    - revolutionize
    - transform
    - embark on a journey
    - explore
    - navigate
    - unveil / shed light on
    - underscore / highlight
    - leverage / harness
    - integrate
    - optimize
    - realize / achieve

# 2. 形容词类 ("高级感"修饰)
adjectives:
  zh:
    - 至关重要
    - 不可或缺
    - 深刻
    - 全面
    - 多方面
    - 细致
    - 一丝不苟
    - 强大
    - 无与伦比
    - 宝贵
    - 无价
    - 创新
    - 前沿
    - 动态
    - 丰富
    - 充满活力
    - 卓越
    - 杰出
    - 不断演进
    - 无缝
  en:
    - crucial / pivotal / vital
    - indispensable
    - profound
    - comprehensive
    - multifaceted
    - meticulous
    - robust
    - unparalleled
    - invaluable
    - innovative / cutting-edge
    - dynamic
    - vibrant
    - exemplary
    - ever-evolving
    - seamless

# 3. 名词类 (框架词)
nouns:
  zh:
    - 格局
    - 领域
    - 旅程
    - 基石
    - 见证
    - 交织
    - 复杂性
    - 洞察
    - 范式
    - 生态
  en:
    - landscape / evolving landscape
    - realm / arena
    - journey
    - cornerstone
    - testament
    - tapestry
    - intricacies / complexities
    - actionable insights
    - paradigm
    - ecosystem

# 4. 过渡句/模板句 (最容被抓的结构)
transition_patterns:
  - 值得注意的是
  - 值得一提的是
  - 重要的是
  - 需要强调的是
  - 在当今快速发展的世界
  - 在当今时代
  - 随着……的不断发展
  - 综上所述
  - 总而言之
  - 由此可见
  - 从这个角度来看
  - 换句话说
  - 换言之
  - 不仅……而且
  - 在本质上
  - 让我们深入探讨
  - 可以说
  - 显而易见
  - 毫不夸张地说

# 5. 中文特别高频 (2025-2026 实测)
zh_2026_high_frequency:
  - 赋能产业
  - 赋能未来
  - 创新驱动
  - 数据驱动
  - 在……背景下
  - 基于……视角
  - 致力于
  - 助力高质量发展
  - 开启新篇章
  - 迈向新征程
  - 深刻把握
  - 全面赋能
  - 深度融合
  - 协同共进
  - 行稳致远
  - 守正创新
  - 以……为抓手

# 6. Top 20 最易被检测组合
top20_detectable:
  zh:
    - 深入探究
    - 见证/证明
    - 关键作用
    - 在当今时代
    - 值得注意的是
    - 多方面的
    - 不断发展的
    - 赋能实体经济
    - 深度融合发展
  en:
    - delve into
    - testament to
    - pivotal role
    - in today's world
    - it is worth noting that
    - multifaceted
    - ever-evolving
    - actionable insights
    - tapestry of
    - realm of
    - harness the power of
    - revolutionize the way
    - foster innovation
    - navigate the complexities
```

---

### 3.4 中文特化禁用词 (高命中率)

以下分类针对中文 AI 输出特别优化：

#### 一、机械过渡词 (15条)
| 禁用词 | 问题 |
|--------|------|
| 综上所述 | 收尾必现 |
| 总而言之 | 万能总结 |
| 不仅如此 | 机械递进 |
| 此外 | 极其高频 |
| 与此同时 | 生硬同步 |
| 另一方面 | 死板对比 |
| 首先/其次/最后 | 标准分段 |
| 换句话说 | 废话重说 |
| 也就是说 | 解释过度 |
| 值得注意的是 | 爹味提醒 |
| 显而易见 | 傲慢逻辑 |
| 不得不说 | 强行感叹 |
| 归根结底 | 拔高立意 |
| 由此可见 | 教科书感 |
| 言归正传 | 转折生硬 |

#### 二、翻译腔表达 (20条)
底座模型基于英文逻辑转译的"后遗症"：

| 禁用词 | 英文原词 |
|--------|----------|
| 织锦 | Tapestry |
| 版图 | Landscape |
| 深潜 | Deep dive |
| 解锁 | Unlock |
| 拥抱 | Embrace |
| 培养 | Foster |
| 导航 | Navigate |
| 遗嘱/证明 | Testament |
| 核心 | At the heart of |
| 驱动 | Driven by |
| 动态 | Dynamics |
| 颗粒度 | Granularity |
| 赋能 | Empower (AI最爱) |
| 维度 | Dimension |
| 画布 | Canvas |
| 范式 | Paradigm |
| 蓝图 | Blueprint |
| 引擎 | Engine |
| 愿景 | Vision |
| 协同 | Synergy |

#### 三、互联网黑话 (20条)
AI 学习了大量公关稿/运营文档的"假专业"：

闭环、底层逻辑、打法、沉淀、抓手、痛点、护城河、赛道、破局、心智、差异化、矩阵、链路、对齐、复盘、反哺、迭代、增益、生态位、交付

#### 四、空洞形容词 (20条)
AI 堆砌最高级形容词的"廉价化妆品"：

卓越的、非凡的、令人惊叹的、绝佳的、完美的、独特的、极其重要的、不可或缺的、令人兴奋的、无与伦比的、精彩绝伦的、巨大的、深远的、强有力的、全方位的、多维度的、前所未有的、尖端的、创新的、令人神往的

#### 五、陈旧比喻 (15条)
AI 想象力跌回20年前的"套路"：

双刃剑、十字路口、救命稻草、冰山一角、汪洋大海、里程碑、催化剂、敲门砖、灯塔、春风、钥匙、窗口、缩影、纽带、桥梁

#### 六、八股文句式 (10条)
一旦出现 AI 感直接爆表：

- "随着……的快速发展" (开头第一名)
- "在……的时代背景下"
- "不仅是……更是……" (标志性排比)
- "让我们一起期待……" (尴尬结尾)
- "开启了新篇章/新旅程"
- "迈出了坚实的一步"
- "在这个充满挑战与机遇的时代"
- "揭开了神秘的面纱"
- "矗立在……之巅"
- "写下了浓墨重彩的一笔"

---

## 4. 放弃的功能

| 功能 | 原因 |
|------|------|
| Humanizer 模块 | 现有 Critic + Polisher 已覆盖 |
| Humanization Intensity | 增加用户负担 |
| Style Anchors 用户输入 | 已有样本库自动提取 |
| 前端 AI 检测按钮 | 依赖外部 API |
| 第一人称"我" | 与风格要求冲突 |

---

## 5. 验证计划

### 5.1 测试步骤

1. **基线测试**：使用当前系统生成 3 篇文章，记录 AI 检测率
2. **增强后测试**：更新提示词后生成 3 篇，对比检测率

### 5.2 验收标准

| 指标 | 目标 |
|------|------|
| AI 检测率下降 | ≥10% |
| 第三人称保持 | 100% |
| 生成质量 | Critic 分数无显著降低 |

---

## 6. 全栈架构设计

### 6.1 当前状态

```
strategist.jinja2 (硬编码 170+ 禁用词)
    ↓
writer/*.jinja2 (各模式独立模板)
    ↓
critic.jinja2 (举例 3 个套话)
    ↓
base_polisher.jinja2 (只说"删除套话")
```

**问题**：禁用词分散在多个模板，维护成本高，不一致。

### 6.2 目标架构

```
┌────────────────────────────────────────────────────────────┐
│                 forbidden_patterns.yaml                     │
│                   (单一来源 - 250+ 词)                        │
└────────────────────────────────────────────────────────────┘
                              │
                    load_forbidden_patterns()
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
        Strategist        Writer/Critic    Polisher
        (策略参考)         (写作约束)       (最终检查)
```

---

## 7. 后端实施

### 7.1 创建词库加载器

**新建文件**：`backend/app/core/forbidden_patterns.py`

```python
from pathlib import Path
import yaml
from typing import Dict, Any, List

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "config"
PATTERNS_FILE = DATA_DIR / "forbidden_patterns.yaml"

_cache = None

def load_forbidden_patterns() -> Dict[str, Any]:
    """加载禁用词库 (带缓存)"""
    global _cache
    if _cache is None:
        if PATTERNS_FILE.exists():
            with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
                _cache = yaml.safe_load(f)
        else:
            _cache = {}
    return _cache
```

### 7.2 修改 prompts.py 自动注入

**修改文件**：`backend/app/core/prompts.py`

> ⚠️ **重要**：需要同时修改 `render_prompt` 和 `render_modular_prompt` 两个函数

```python
from .forbidden_patterns import load_forbidden_patterns

def render_prompt(agent_name: str, context: Dict[str, Any]) -> str:
    """Load and render the template with the given context."""
    # P21: 自动注入禁用词库
    context['forbidden_patterns'] = load_forbidden_patterns()
    template_str = load_template(agent_name)
    try:
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        return f"Error rendering prompt: {str(e)}"

def render_modular_prompt(template_path: str, context: Dict[str, Any]) -> str:
    """P14: 渲染子目录中的模板"""
    # P21: 自动注入禁用词库
    context['forbidden_patterns'] = load_forbidden_patterns()
    full_path = PROMPTS_DIR / template_path
    # ... 原有逻辑
```

### 7.2.1 Custom Prompt 分支处理

> ⚠️ **问题**：`strategist.py` 和 `critic/standard.py` 的 Custom Prompt 分支绕过了 `render_prompt()`

**修复方案**：在各 Agent 的 context 构建阶段直接注入词库

**修改 strategist.py `build_strategist_context()`**：

```python
from ..core.forbidden_patterns import load_forbidden_patterns

def build_strategist_context(state: dict) -> dict:
    # ... 原有逻辑 ...
    context = {
        # ... 原有字段 ...
        "forbidden_patterns": load_forbidden_patterns()  # P21: 新增
    }
    return context
```

**修改 critic/standard.py `standard_critic()`**：

```python
from app.core.forbidden_patterns import load_forbidden_patterns

def standard_critic(...) -> dict:
    # ... 原有逻辑 ...
    context = {
        # ... 原有字段 ...
        "forbidden_patterns": load_forbidden_patterns()  # P21: 新增
    }
```

### 7.3 迁移 strategist.jinja2

**删除**：第 93-170 行的硬编码禁用词列表

**替换为**：

```jinja2
{# ===== 禁用词引用 ===== #}
**以下内容严禁出现在生成文本中**：

{% for category, items in forbidden_patterns.items() %}
## {{ category }}
{% if items is mapping %}
{% for lang, words in items.items() %}
【{{ lang }}】{{ words | join(' / ') }}
{% endfor %}
{% else %}
{{ items | join('、') }}
{% endif %}
{% endfor %}
```

---

## 8. 写作流程集成

### 8.1 数据流

```
用户输入
    ↓
┌─────────────────────────────────────────────────────────┐
│ Strategist                                                │
│ - 接收 forbidden_patterns                                 │
│ - 在策略规划中避免使用禁用词                                  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Writer                                                    │
│ - 接收 forbidden_patterns                                 │
│ - 生成时严格避免禁用词                                       │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Critic                                                    │
│ - 使用 forbidden_patterns 进行 AI 痕迹评分                  │
│ - 检测 24 种 AI 模式                                       │
│ - 如果 score < 85，触发自动循环 (max 2 次)                   │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ Polisher                                                  │
│ - 最终检查清单                                             │
│ - 删除遗漏的禁用词                                          │
└─────────────────────────────────────────────────────────┘
```

### 8.2 各 Agent 接收词库的方式

| Agent | 如何注入 forbidden_patterns |
|-------|----------------------------|
| Strategist | ✅ prompts.py 自动注入 |
| Writer | ✅ prompts.py 自动注入 |
| Critic | ✅ prompts.py 自动注入 |
| Polisher | ✅ prompts.py 自动注入 |

**结论**：只需修改 `prompts.py` 的两个 render 函数，所有 Agent 自动获得词库。

---

## 9. 前端设置 (Phase 2 - 可选)

允许用户在设置页面查看/编辑禁用词库。

### API 端点
- `GET /api/settings/forbidden-patterns`
- `PUT /api/settings/forbidden-patterns`

**暂不实施**：Phase 2 优先级较低，先完成后端集中化。

---

## 10. 风险与对策

| 风险 | 对策 |
|------|------|
| 词库过大导致 prompt token 爆炸 | 只注入当前模式需要的子集 |
| 误禁正常词汇 | 允许用户白名单 |
| YAML 加载失败 | 添加 fallback 空词库 |
| **词库内部重复** | YAML 创建时去重 (综上所述、赋能、范式 等重复项) |

---

## 11. 完整修改清单 (11 个文件)

### 11.1 新建文件

| 文件 | 说明 |
|------|------|
| `backend/app/core/forbidden_patterns.py` | YAML 加载器 |
| `backend/data/config/forbidden_patterns.yaml` | 禁用词库 (250+ 条) |

### 11.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `backend/app/core/prompts.py` | 两个 render 函数注入词库 |
| `backend/app/agents/strategist.py` | context 构建注入词库 |
| `backend/app/agents/writer/mid_article.py` | context 构建注入词库 ✅ |
| `backend/app/agents/writer/long_article.py` | context 构建注入词库 |
| `backend/app/agents/writer/tutorial.py` | context 构建注入词库 |
| `backend/app/agents/writer/rewrite.py` | context 构建注入词库 |
| `backend/app/agents/critic/standard.py` | context 构建注入词库 ✅ |
| `backend/app/agents/polisher/standard.py` | context 构建注入词库 |
| `backend/data/prompts/strategist.jinja2` | 删除硬编码词库，引用变量 |

---

## 12. 自定义提示词模板

> 实施完成后，请将以下内容添加到你的自定义提示词中

### 12.1 在自定义提示词中引用词库

在你的自定义 Writer/Critic 提示词**开头**添加：

```
【P21 禁用词约束】
以下词汇和句式严禁使用：

{% if forbidden_patterns %}
{% for category, items in forbidden_patterns.items() %}
{{ category }}: {% if items is mapping %}{% for lang, words in items.items() %}{{ words[:10] | join('、') }}...{% endfor %}{% else %}{{ items[:10] | join('、') }}...{% endif %}
{% endfor %}
{% endif %}

---
```

### 12.2 简化版 (推荐)

如果词库太长导致 token 爆炸，使用简化版：

```
【P21 禁用词约束】
严禁使用以下 AI 高频词：
- 综上所述、总而言之、值得注意的是、此外、与此同时
- 深入探讨、赋能、驱动、格局、范式
- 首先/其次/最后、不仅...而且
- 双刃剑、里程碑、催化剂、灯塔
- "随着...的快速发展"、"让我们一起期待"

【节奏要求】
- 禁止连续 3 句长度相同
- 禁止段落以简洁单行结尾
- 减少破折号插入解释

---
```

---

## 13. 实施计划

| 优先级 | 任务 | 工时 |
|--------|------|------|
| P0 | 创建 `forbidden_patterns.py` 加载器 | 0.5h |
| P0 | 创建 `forbidden_patterns.yaml` 词库 | 1h |
| P0 | 修改 `prompts.py` 两个 render 函数 | 0.5h |
| P1 | 修改 `strategist.py` context 注入 | 0.5h |
| P1 | 修改 4 个 Writer 文件 context 注入 | 1h |
| P1 | 修改 `critic/standard.py` context 注入 | 0.5h |
| P1 | 修改 `polisher/standard.py` context 注入 | 0.5h |
| P1 | 迁移 `strategist.jinja2` 硬编码词库 | 0.5h |
| P2 | 测试验证 | 1h |

**总预估工时：6-7 小时**

---

## 14. 验收标准

| 指标 | 目标 |
|------|------|
| 禁用词库单一来源 | ✅ 只在 YAML 维护 |
| 标准模板覆盖 | ✅ 4 个 Agent 全覆盖 |
| 自定义提示词覆盖 | ✅ context 注入全覆盖 |
| AI 检测率下降 | ≥10% |
| 无硬编码词库残留 | ✅ strategist 迁移完成 |

---

## 15. 参考资料

- WikiProject AI Cleanup (维基百科 AI 写作特征指南)
- 同事提供的 Humanizer 架构方案
- 现有系统 P18 模块化架构

