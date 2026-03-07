# P11 详细执行计划

**日期**: 2026-01-31  
**预计耗时**: 4 小时

---

## ⚠️ 审查发现的问题 (2026-01-31 11:04 更新)

### 🔴 高优先级问题

| 问题 | 说明 |
|------|------|
| **Mode 命名不一致** | 前端 `quick_summary` ≠ 后端 `quick_take` |
| **MODE_LENGTH_MAPPING 需更新** | short/medium/long → tweet/thread/post |

### 📋 完整需修改文件清单

| 文件 | 改动点 | 类型 |
|------|--------|:----:|
| `backend/app/graph.py:8-12` | `LENGTH_MAP` 更新 | � 核心 |
| `backend/app/graph.py:15-20` | `MODE_LENGTH_MAPPING` 更新 | 🔴 核心 |
| `backend/app/main.py:84` | `length="medium"` → `"thread"` | 🟡 默认值 |
| `backend/app/agents/writer.py:65` | `length="medium"` → `"thread"` | 🟡 默认值 |
| `backend/app/agents/critic.py:8` | `length="medium"` → `"thread"` | 🟡 默认值 |
| `backend/data/prompts/writer.jinja2` | 添加 Mode 专属规则 | 🟢 Prompt |
| `frontend/src/features/studio/schema.ts:38-42` | `ArticleLengthSchema` 更新 | 🔴 核心 |
| `frontend/src/features/studio/schema.ts:57` | `.default('medium')` → `'thread'` | 🟡 默认值 |
| `frontend/src/config/constants.ts:31-35` | `ARTICLE_LENGTHS` 更新 | 🟢 UI |

### 修复建议

1. **统一用 `quick_summary`** (后端 graph.py 改)
2. **所有默认值同步改为 `thread`**
3. **前后端必须同时部署**

---

## 阶段 1: 新篇幅体系 (前后端同步) - 1h

### 1.1 后端改动

| 步骤 | 文件 | 具体改动 |
|:----:|------|----------|
| 1.1.1 | `backend/app/graph.py` | 更新 `LENGTH_MAP` |

```python
# 旧值
LENGTH_MAP = {
    "short": (400, 600),
    "medium": (1200, 1800),
    "long": (2500, 4000)
}

# 新值
LENGTH_MAP = {
    "tweet": (150, 300),
    "thread": (500, 800),
    "post": (1000, 1500)
}
```

### 1.2 前端改动

| 步骤 | 文件 | 具体改动 |
|:----:|------|----------|
| 1.2.1 | `frontend/src/features/studio/schema.ts` | 更新 `ArticleLengthSchema` |

```typescript
// 旧值
export const ArticleLengthSchema = z.enum(["short", "medium", "long"]);

// 新值
export const ArticleLengthSchema = z.enum(["tweet", "thread", "post"]);
```

| 步骤 | 文件 | 具体改动 |
|:----:|------|----------|
| 1.2.2 | `frontend/src/config/constants.ts` | 更新 `ARTICLE_LENGTHS` |

```typescript
// 新值
export const ARTICLE_LENGTHS = [
    { id: 'tweet', label: '推文 (~300字)' },
    { id: 'thread', label: '推文串 (~800字)' },
    { id: 'post', label: '帖子 (~1.5k字)' }
];
```

---

## 阶段 2: Mode 专属写作指导 + 禁止虚构 - 30min

| 步骤 | 文件 | 具体改动 |
|:----:|------|----------|
| 2.1 | `backend/data/prompts/writer.jinja2` | 添加 Mode 专属规则 |

```jinja2
{# === P11: Mode 专属写作指导 === #}
{% if mode == "quick_take" or mode == "quick_summary" %}
【快讯模式专属规则】
✓ 直接陈述事实，开门见山
✓ 用数据/引用开头
✗ 禁止虚构人物故事 ("凌晨三点，李哥...")
✗ 禁止编造场景 ("某个交易员...")
✗ 禁止过度情绪渲染
{% elif mode == "deep_analysis" %}
【深度分析模式】
✓ 可使用故事化开头
✓ 多角度论证，数据支撑
✓ 结构完整：引言→分析→结论
{% elif mode == "tutorial" or mode == "translate" %}
【教程指南模式】
✓ 分步骤讲解，编号清晰
✓ 每步配示例
✓ 操作性强，可执行
{% endif %}
```

---

## 阶段 3: Web3 样本接入 (_registry) - 1.5h

### 3.1 分析 _registry 表结构

| 步骤 | 操作 |
|:----:|------|
| 3.1.1 | 运行 `analyze_registry.py` 确认字段 |
| 3.1.2 | 确定赛道匹配逻辑 |

### 3.2 修改 google_sheets_source.py

| 步骤 | 改动 |
|:----:|------|
| 3.2.1 | 添加 `fetch_registry_samples()` 方法 |
| 3.2.2 | 添加赛道关键词映射表 |
| 3.2.3 | 实现 Fallback 逻辑 |

### 3.3 修改 strategist.py

| 步骤 | 改动 |
|:----:|------|
| 3.3.1 | 添加话题分类逻辑 |
| 3.3.2 | 根据话题选择赛道样本 |

---

## 阶段 4: 测试验证 - 1h

| 测试项 | 预期结果 |
|--------|----------|
| 4.1 前端篇幅选择 | 显示 tweet/thread/post |
| 4.2 quick_take 生成 | 无虚构开头，直接陈述 |
| 4.3 deep_analysis 生成 | 允许故事开头 |
| 4.4 Web3 话题匹配 | 命中 _registry 赛道样本 |
| 4.5 Fallback 测试 | 无匹配时用 mimeng 样本 |

---

## 执行顺序总结

```
阶段1 (篇幅) → 阶段2 (Mode指导) → 阶段3 (样本) → 阶段4 (测试)
   1h              30min              1.5h            1h
```

**必须前后端同时部署！**

---

> 创建时间: 2026-01-31 10:59
