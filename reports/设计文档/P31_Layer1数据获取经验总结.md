# P31 Layer 1 数据获取经验总结

> **日期**: 2026-02-26  
> **目的**: 整理 Surf API 获取 leak.me 数据的成功经验和失败教训

---

## 一、测试时间线

| 时间 | 测试 | 脚本 | 结果 |
|------|------|------|------|
| 02-25 13:37 | leak.me 首次测试 | `test_surf_leakme.py` | ✅ **8 个项目，数据丰富** |
| 02-25 15:38 | 完整 Pipeline v1 | `generate_research_report.py` v1 | ⚠️ 3 个项目，有脏数据 |
| 02-26 14:08 | Pipeline v2 (24h) | `generate_research_report.py` v2 | ✅ 3 个项目，无脏数据 |
| 02-26 14:20 | Layer 1 扩大范围 (10天) | `test_layer1_10day.py` v1 | ❌ 15 个但质量差 |
| 02-26 14:35 | Layer 1 修正搜 leak.me | `test_layer1_10day.py` v2 | ⚠️ 6 个项目，KOL 数低 |
| 02-26 15:03 | Layer 1 按日期多次搜索 | `test_layer1_10day.py` v3 | ❌ 5天中4天无推文 |
| 02-26 16:58 | **用户手动 Surf 页面测试** | Surf 网页 | ✅ **大量项目** |
| 02-26 17:00 | **简洁 Prompt API 验证** | 内联脚本 | ✅ **4 AI + 多 Web3** |

---

## 二、成功经验

### ✅ 02-25 首次测试（最佳结果）

**脚本**: `test_surf_leakme.py`

**成功要素**:

1. **同时搜索两个数据源**
   - X 推文: `搜索 @leakmealpha`
   - 网站: `请访问和分析 leak.me（https://leak.me/）网站`
   - 两个独立的 Surf API 调用，各搜各的

2. **不限制输出格式**
   - System Prompt: `提供结构化的数据，使用表格格式呈现`
   - 没有要求 JSON 输出
   - Surf 自由组织回答，输出 Markdown 表格

3. **详细的搜索指令**
   - 明确描述 leak.me 是什么服务
   - 明确要求的字段：项目名称、Twitter、类别、KOL 数、KOL 类型、热度原因
   - 要求分两个表格：Web3 项目 + 排除的非项目

4. **使用 `citation: ["source"]`**
   - 启用了来源引用功能
   - 可能触发 Surf 更深层的搜索

**返回质量**:
- 8 个项目: Reveel、Otonix、Saturn Credit、Clude、TechDollar、Takeover、Kyber Network、Taiko
- 每个项目 +20 KOL
- 包含类别、KOL 类型分布、热度原因
- 另有 27 个被排除的个人账号列表

---

## 三、失败教训

### ❌ 问题 1: 强制 JSON 输出

**现象**: 要求 Surf 输出 JSON 后，项目数量和质量显著下降

**原因分析**:
- JSON 格式约束可能改变了 Surf 的搜索策略
- "只输出 JSON" 让 Surf 跳过了表格呈现的中间思考过程
- Surf 的 reasoning 在被约束格式后可能缩减搜索范围

**对比**:

| 输出格式 | 项目数 | 数据质量 |
|---------|-------|---------|
| 自由 Markdown 表格 | 8 | 丰富（类别/KOL/类型/原因） |
| 强制 JSON | 3-6 | 精简（缺少细节） |

**结论**: Layer 1 不应强制 JSON 输出，让 Surf 自由输出，后续用 Python 解析。

### ❌ 问题 2: 只搜推文不搜网站

**现象**: 只搜 @leakmealpha 推文时返回与 leak.me 无关的 AI 产品（Perplexity、Claude）

**原因分析**:
- `搜索 @leakmealpha 最近 24h 的推文` 让 Surf 做了模糊搜索
- Surf 可能搜到了其他账号提及 @leakmealpha 的内容
- 没有给 Surf 明确的上下文（leak.me 是什么）

**对比**:

| Prompt 策略 | 项目类型 | 相关性 |
|------------|---------|-------|
| 只搜 @leakmealpha 推文 | Perplexity/Claude/Flood | ❌ 不相关 |
| 搜推文 + 描述 leak.me 是 KOL tracker | POM/nookplot/Claude | ⚠️ 部分相关 |
| 搜推文 + 搜 leak.me 网站 | Reveel/Saturn/Takeover... | ✅ 高度相关 |

**结论**: 必须同时搜索两个源，并且明确描述 leak.me 的功能。

### ❌ 问题 3: 10 天范围没有增加数据

**现象**: 搜 10 天和搜 24h 项目数量差不多

**原因分析**:
- leak.me 网站的 trending 是**实时数据**，只显示当前 24h 的热点
- Surf 通过 `web_fetch` 访问 leak.me 只能获取当前页面
- X 搜索有时间限制，可能无法精确按日期过滤

**结论**: 如需历史数据，需要按日期逐天搜索推文，而非一次搜 10 天。

### ❌ 问题 4: System Prompt 导致脏数据

**现象**: v1 Pipeline 报告中出现 `db_internal_xxx`、URL、"待验证" 等脏数据

**原因**:
```
所有数据必须有来源支撑，不确定的标注「待验证」  ← 罪魁祸首
```

**对比**:

| System Prompt 指令 | 脏数据 |
|-------------------|-------|
| 英文版（测试）: "Output in English" | ✅ 无 |
| 中文版 v1: "标注来源+标注待验证" | ❌ 大量 |
| 中文版 v2: "不要标注来源/不要写待验证" | ✅ 无 |

**结论**: 已在 v2 prompt 中修复，明确禁止输出来源标记。

---

## 四、最佳实践总结

### Layer 1 数据获取最佳模式

```
1. System Prompt: 简洁角色定义 + 表格格式要求（不限 JSON）
2. User Prompt: 同时搜 leak.me 网站 + @leakmealpha 推文
3. 明确描述 leak.me 是什么（Crypto KOL Tracker）
4. 给出明确的表格字段要求
5. 启用 citation: ["source"]
6. reasoning: high
7. 后处理: Python 解析 Markdown 表格 → 结构化数据
```

### 推荐的 Layer 1 Prompt 结构（v2 修正版）

**System Prompt**:
```
你是一位专业的加密货币研究分析师。请用中文回答。
提供结构化的数据，使用表格格式呈现。
重点关注 Web3/Crypto/AI 相关的项目，排除个人账号和非加密实体。
```

**User Prompt**:
```
请访问和分析 leak.me（https://leak.me/）网站的当前 trending 数据，
以及 @leakmealpha 最近的推文内容。

leak.me 是一个 Crypto KOL Tracker，追踪加密货币 KOL 的新关注行为。

请整理所有被 KOL 集中关注的 Web3 和 AI 项目，输出表格：

| 项目名称 | Twitter 账号 | 类别 | KOL 新关注数 | KOL 类型 | 热度原因 | 参与机会 |

要求：排除个人、交易所、媒体。按 KOL 数量排序。
```

---

## 五、最终结论（02-26 17:00 更新）

### ✅ 根因确认

**Prompt 越简洁，Surf 搜索质量越好。**

用户手动在 Surf 页面用一句话 prompt 获得了最佳结果：
```
检索X账号@leakmealpha 近7天的推文数据，整理出来web3项目和AI项目
```

同样的 prompt 通过 API 调用也同样有效（4 AI + 多 Web3），证明问题不在 API，在 prompt。

### ❌ 失败方案（已排除）

| 方案 | 结果 | 原因 |
|------|------|------|
| 强制 JSON 输出 | ❌ | 限制搜索深度 |
| 按日期逐天搜索 | ❌ | Surf X 搜索找不到历史推文 |
| 复杂 System Prompt | ❌ | 过多约束干扰搜索 |

### ✅ 推荐方案

**Layer 1 prompt 策略：简洁 + 不限格式 + 后处理**

1. 用简洁的自然语言 prompt（一两句话）
2. 不限制输出格式（让 Surf 自由输出表格）
3. Python 后处理：解析 Markdown 表格 → 提取项目列表 → 转 JSON

### 下一步

- [ ] 更新 `generate_research_report.py` 的 Layer 1 prompt 为简洁版
- [ ] 实现 Python 解析 Surf 自由输出 → 结构化数据
- [ ] 重新测试完整 Pipeline
