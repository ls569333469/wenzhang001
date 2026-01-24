# Lark 数据清洗工具手册

> **版本**: v6.0 (A/B 测试版) | **更新日期**: 2026-01-24

---

## 1. 概述

本手册汇总了 Quantum Studio 中所有与 Lark (飞书多维表格) 数据清洗相关的工具，并详细介绍了 **A/B 测试方案**：旧版脚本作为兜底，新版优化脚本用于生产。

### 1.1 工具索引

| 工具 | 文件路径 | 用途 | 推荐 |
|------|----------|------|:----:|
| **优化版入库** | `scripts/ingest_optimized.py` | 批量清洗并入库 (优化版) | ⭐ |
| **旧版入库** | `scripts/ingest_knowledge.py` | 批量清洗并入库 (兜底版) | |
| **Lark Client** | `app/core/lark_client.py` | Lark API 核心客户端 | |
| **Hash 缓存** | `scripts/batch/hash_cache.py` | 本地查重缓存 | |
| **字段审计** | `scripts/audit_knowledge_fields.py` | 检查/删除/创建表字段 | |
| **清空表** | `scripts/clear_knowledge_repo.py` | 删除表中所有记录 | |
| **数据验证** | `scripts/verify_lark_data.py` | 验证入库数据完整性 | |
| **清洗 CLI** | `tools/cleaner_cli.py` | 工业级素材清洗工具 | |

---

## 2. A/B 测试方案总览

### 2.1 架构图

```
                     ┌─────────────────────────────────────┐
                     │   命令行参数选择 A 或 B 方案         │
                     └─────────────────┬───────────────────┘
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           ▼                                                       ▼
┌─────────────────────────┐                         ┌─────────────────────────┐
│    方案 A (旧版兜底)     │                         │   方案 B (优化版推荐)    │
│ ingest_knowledge.py     │                         │ ingest_optimized.py     │
├─────────────────────────┤                         ├─────────────────────────┤
│ ✗ 2 次 LLM 调用/条      │                         │ ✓ 1 次 LLM 调用/条      │
│ ✗ 单条 Lark 上传        │                         │ ✓ 批量 Lark 上传        │
│ ✗ Lark API 查重         │                         │ ✓ 本地 Hash 缓存        │
│ ✗ 截取前 500 字摘要      │                         │ ✓ LLM 生成一句话摘要    │
├─────────────────────────┤                         ├─────────────────────────┤
│ 费用: ¥16 / 5806 条     │                         │ 费用: ¥8 / 5806 条      │
│ 时间: 5-6h              │                         │ 时间: 2h                │
│ 稳定性: ⭐⭐⭐⭐⭐         │                         │ 稳定性: ⭐⭐⭐⭐ (已验证)  │
└─────────────────────────┘                         └─────────────────────────┘
```

### 2.2 方案对比

| 维度 | 方案 A (旧版) | 方案 B (优化版) | 差异 |
|------|--------------|----------------|------|
| **LLM 调用** | 2 次/条 | 1 次/条 | -50% Token |
| **Lark 上传** | 单条 | 批量 500 条/次 | -99% 网络时间 |
| **查重方式** | Lark API | 本地 Hash 缓存 | -99% 查重时间 |
| **核心摘要** | 截取前 500 字 | LLM 生成一句话 | 质量提升 |
| **费用估算** | ¥16 | ¥8 | **省 50%** |
| **时间估算** | 5-6h | 2h | **省 60%** |

### 2.3 如何选择

| 场景 | 推荐方案 |
|------|---------|
| 日常生产入库 | ⭐ **方案 B (优化版)** |
| 优化版出现问题时 | 方案 A (兜底) |
| 首次部署验证 | 方案 B (--limit 10 测试) |

---

## 3. 方案 B: 优化版入库脚本 (推荐)

> 📁 文件路径: `backend/scripts/ingest_optimized.py`

### 3.1 核心优化点

#### 3.1.1 合并 LLM 调用

**旧版 (2 次调用)**:
```
调用 1: score_content_async() → 返回评分
调用 2: extract_entities_keywords() → 返回实体和关键词
```

**新版 (1 次调用)**:
```python
MERGED_PROMPT = """
分析以下 Web3 内容，返回 JSON:

标题: {title}
赛道: {topic}
内容: {content[:2000]}

返回格式 (严格 JSON，无其他文字):
{
  "quality_score": 1-10,
  "summary": "一句话概括核心观点 (30字以内)",
  "entities": ["项目/人名/代币1", "项目/人名/代币2"],
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "fact_type": "硬数据/深度分析/观点评论/梗_黑话/快讯资讯"
}
"""
```

#### 3.1.2 批量 Lark 上传

```python
# 旧版: 单条上传
for record in records:
    lark_client.create_record(app_token, table_id, record)  # 每条 1 次 API 调用

# 新版: 批量上传 (每批 500 条)
for i in range(0, len(records), 500):
    batch = records[i:i+500]
    lark_client.batch_create_records(app_token, table_id, batch)  # 每批 1 次调用
```

#### 3.1.3 本地 Hash 缓存

```python
# 旧版: 每条记录调用 Lark API 查重
existing = lark_client.list_records(filter=f"内容指纹={hash}")

# 新版: 本地文件缓存查重
hash_cache = get_hash_cache()  # 加载 processed_hashes.json
if hash_cache.contains(content_hash):
    skip()  # 毫秒级查重
```

### 3.2 技术实现

#### 3.2.1 文件结构

```
backend/scripts/
├── ingest_optimized.py      # 主脚本
└── batch/
    ├── __init__.py
    └── hash_cache.py        # 本地 Hash 缓存模块
```

#### 3.2.2 依赖关系

```mermaid
graph TD
    A[ingest_optimized.py] --> B[lark_client.py]
    A --> C[hash_cache.py]
    A --> D[llm.py]
    B --> E[Lark API]
    C --> F[processed_hashes.json]
    D --> G[Volcengine API]
```

### 3.3 使用命令

```bash
cd backend

# 处理单个赛道 (测试用)
python -m scripts.ingest_optimized --folder "DAO与社区治理" --limit 10

# 处理所有赛道 (生产用)
python -m scripts.ingest_optimized --all --limit 0

# 限制每个赛道处理数量
python -m scripts.ingest_optimized --all --limit 5
```

### 3.4 入库流程

```mermaid
flowchart TD
    A[读取 JSON 文件] --> B[清洗内容]
    B --> C[计算 MD5 指纹]
    C --> D{本地 Hash 缓存查重}
    D -->|已存在| E[跳过]
    D -->|不存在| F[调用合并 LLM]
    F --> G[解析 JSON 返回]
    G --> H[构建 Lark 字段]
    H --> I[添加到待上传队列]
    I --> J{队列满 500?}
    J -->|是| K[批量上传 Lark]
    J -->|否| L[继续处理下一条]
    K --> M[更新 Hash 缓存]
    L --> A
```

### 3.5 字段映射

| Lark 字段 | 数据来源 | 说明 |
|-----------|----------|------|
| 上传时间 | `datetime.now()` | 主字段，记录入库时间 |
| 标题 | JSON `title` | 原始标题 |
| 核心摘要 | LLM `summary` | ⭐ 一句话概括 (30字) |
| 正文原文 | JSON `content` | 清洗后全文 |
| 赛道分类 | 文件夹名称 | 42 个赛道分类 |
| 关键词 | LLM `keywords` | 最多 5 个 |
| 项目/人名/代币 | LLM `entities` | 最多 5 个 |
| 事实类型 | LLM `fact_type` | 5 种类型 |
| 质量评分 | LLM `quality_score` | 1-10 分 |
| 发布日期 | JSON `published_at` | 可选 |
| 内容指纹 | MD5 Hash | 查重用 |

### 3.6 输出示例

```
============================================================
🚀 Quantum Studio v5.2 - Knowledge_Repo 优化版入库
============================================================
📋 Base Token: CSfdbzErqay4bnsISxEuuVais3g
📋 Knowledge Table ID: tblkvQK9aKxP0wsk
📋 优化特性: 合并LLM调用 + 批量上传 + 本地Hash缓存

📂 处理文件夹: DAO与社区治理
   找到 10 个 JSON 文件
   入库中... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
   📤 批量上传 10 条记录...
   ✅ 成功: 10 | ⚠️ 跳过: 0 | ❌ 失败: 0

============================================================
📊 入库完成!
============================================================
  ✅ 成功入库: 10
  ⚠️ 重复跳过: 0
  ❌ 失败: 0
```

---

## 4. 方案 A: 旧版入库脚本 (兜底)

> 📁 文件路径: `backend/scripts/ingest_knowledge.py`

### 4.1 功能

从 `data/Web3素材/` 文件夹批量清洗 JSON 文件并入库到 Lark。

### 4.2 使用命令

```bash
cd backend

# 入库所有赛道（每个限制 N 条）
python -m scripts.ingest_knowledge --all --limit 2

# 入库指定赛道
python -m scripts.ingest_knowledge --folder "DAO与社区治理" --limit 5

# 仅统计不上传
python -m scripts.ingest_knowledge --all --dry-run
```

### 4.3 入库流程

```mermaid
flowchart TD
    A[读取 JSON] --> B[计算内容指纹]
    B --> C{Lark API 查重}
    C -->|已存在| D[跳过]
    C -->|不存在| E[LLM 评分]
    E --> F[LLM 提取关键词/实体]
    F --> G[推断事实类型]
    G --> H[单条上传 Lark]
```

### 4.4 与优化版的差异

| 步骤 | 旧版 | 优化版 |
|------|------|--------|
| 查重 | Lark API (慢) | 本地 Hash (快) |
| LLM | 2 次调用 | 1 次调用 |
| 摘要 | 截取前 500 字 | LLM 生成 |
| 上传 | 单条 | 批量 500 |

### 4.5 何时使用

- 优化版脚本出现 Bug 时
- 需要对比测试时
- 网络极不稳定时 (单条重试更可控)

---

## 5. 辅助工具

### 5.1 字段审计 (audit_knowledge_fields.py)

> ⚠️ 用于检查和清理多余字段

```bash
cd backend
python -m scripts.audit_knowledge_fields
```

**输出示例**:
```
✅ 保留字段: 10 个
❌ 待删字段: 1 个
⚠️ 缺失字段: 0 个

待删字段列表:
  - 上传时间 (id=fldBwqHMN7)

是否删除以上字段? (y/n): n
```

### 5.2 清空表 (clear_knowledge_repo.py)

```bash
cd backend
python -m scripts.clear_knowledge_repo
```

> [!WARNING]
> 此操作不可逆，执行前请确认！

### 5.3 数据验证 (verify_lark_data.py)

```bash
cd backend
python -m scripts.verify_lark_data
```

**输出示例**:
```
🔍 Verifying Lark Data Integrity...
✅ Total Records Fetched: 456
```

### 5.4 Hash 缓存管理

```bash
# 查看缓存数量
python -c "from scripts.batch.hash_cache import get_hash_cache; print(len(get_hash_cache()))"

# 清空缓存 (重新入库前需要)
python -c "from scripts.batch.hash_cache import get_hash_cache; c = get_hash_cache(); c.clear()"
```

---

## 6. 字段规范 v4 (11 字段)

| # | 字段 | 类型 | 来源 | 说明 |
|---|------|------|------|------|
| 1 | **上传时间** | 文本 | 系统时间 | 主字段 (无法删除) |
| 2 | 标题 | 文本 | JSON `title` | 原始标题 |
| 3 | 核心摘要 | 文本 | LLM `summary` | 一句话摘要 |
| 4 | 正文原文 | 文本 | JSON `content` | 清洗后全文 |
| 5 | 赛道分类 | 单选 | 文件夹名称 | 42 个选项 |
| 6 | 关键词 | 文本 | LLM `keywords` | 逗号分隔 |
| 7 | 项目/人名/代币 | 文本 | LLM `entities` | 逗号分隔 |
| 8 | 事实类型 | 单选 | LLM `fact_type` | 5 种类型 |
| 9 | 质量评分 | 数字 | LLM `quality_score` | 1-10 |
| 10 | 发布日期 | 日期 | JSON `published_at` | 可选 |
| 11 | 内容指纹 | 文本 | MD5 Hash | 查重用 |

---

## 7. 费用估算

### 7.1 计算公式

```
LLM 费用 = 文档数 × (输入 Token + 输出 Token) × 单价
```

### 7.2 对比 (5806 条 Web3 素材)

| 方案 | 输入 Token/条 | 输出 Token/条 | 调用次数/条 | 总费用 |
|------|--------------|--------------|------------|--------|
| 方案 A (旧版) | ~1500 | ~100 | 2 | **¥16** |
| 方案 B (优化版) | ~1500 | ~130 | 1 | **¥8** |

> 注：基于 DeepSeek V3 定价 (输入 ¥2/M, 输出 ¥8/M)

---

## 8. 环境配置

### 8.1 必需的 .env 变量

```env
# Lark/飞书配置
LARK_APP_ID=cli_xxx
LARK_APP_SECRET=xxx
LARK_BASE_URL=https://open.feishu.cn/open-apis
LARK_BASE_TOKEN=xxx
LARK_KNOWLEDGE_TABLE_ID=tblxxx

# LLM API (清洗评分需要)
ARK_API_KEY=xxx
```

### 8.2 Feature Flag (可选)

```json
// config/user_config.json
{
  "feature_flags": {
    "use_knowledge_repo": true,
    "use_optimized_ingest": true
  }
}
```

---

## 9. 常见问题

### Q1: 入库报错 `FieldNameNotFound`

**原因**: Lark 表中缺少该字段  
**解决**: 运行 `audit_knowledge_fields.py` 创建缺失字段

### Q2: 记录被跳过但 Lark 表中没有

**原因**: 本地 Hash 缓存包含该记录  
**解决**: 清空缓存后重试
```bash
python -c "from scripts.batch.hash_cache import get_hash_cache; c = get_hash_cache(); c.clear()"
```

### Q3: LLM 返回空结果

**原因**: JSON 解析失败  
**解决**: 检查 LLM 返回格式，脚本会使用默认值兜底

### Q4: 批量上传部分失败

**原因**: 网络波动或 Lark API 限流  
**解决**: 失败的记录会被记录，可重新运行入库

---

## 10. 回滚策略

如果优化版脚本出现问题：

```bash
# 1. 停止优化版脚本
Ctrl+C

# 2. 使用旧版脚本继续入库
python -m scripts.ingest_knowledge --all --limit 10
```

---

## 11. 相关文档

| 文档 | 路径 |
|------|------|
| 优化方案详解 | `reports/design_docs/frontend_design/13-1_Plan_Web3批量清洗优化方案.md` |
| 字段调用分析 | `reports/design_docs/frontend_design/13-2_Report_Knowledge字段调用流程分析.md` |
| 费用计算明细 | `reports/design_docs/历史文档/Web3数据清洗成本分析.md` |
| 项目手册 | `PROJECT_HANDBOOK.md` |

---

## 12. 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-01-24 | **v6.0** | 新增 A/B 测试方案，优化版脚本，LLM 摘要，上传时间字段 |
| 2026-01-24 | v5.0 | 整合所有 Lark 清洗工具，新增字段审计工具 |
| 2026-01-24 | v4.0 | 字段规范 v4：移除来源链接等 6 个字段 |
| 2026-01-23 | v3.0 | 新增 LLM 实体提取和质量评分 |
