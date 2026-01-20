# 📑 Quantum Studio v5.1 - Unified Content Brain (UCB) 升级方案

| **项目名称** | **Quantum Studio v5.1 (UCB Upgrade)** | **密级** | **内部公开** |
| --- | --- | --- | --- |
| **版本号** | **V1.0 (Draft)** | **架构师** | Antigravity Agent |
| **基准版本** | v5.0 (Async Writer) + v3.0 UCB 理论 | **日期** | 2026-01-18 |
| **核心变更** | 引入 **Knowledge_Repo** 双库架构，增加 **时效过滤** 与 **审核流程**。 |  |  |

---

## 1. 设计理念 (Design Philosophy)

本方案融合 v3.0 的 **"骨肉魂 (Bone-Flesh-Soul)"** 理论与 v5.0 的 **工业级基础设施**。

### 1.1 骨肉魂模型 (继承自 v3.0)

| 层级 | 隐喻 | 数据来源 | 控制字段 |
|------|------|----------|----------|
| 🦴 **骨 (Bone)** | 文章结构 | Strategist Agent 生成 | `Snippet_Type`: Hook / Body / Ending / CTA |
| 🥩 **肉 (Flesh)** | 行业知识 | **Knowledge_Repo (新增)** | `Topic_Category`, `Publish_Date`, `Fact_Type` |
| 👻 **魂 (Soul)** | 写作风格 | Style_Repo (现有 Lark 表) | `Author`, `Style_Tags`, `Emotion` |

### 1.2 核心升级点 (相对于 v5.0)

| 问题 | v5.0 现状 | v5.1 解决方案 |
|------|-----------|---------------|
| 知识与风格混杂 | 单表混存 | **双库分离** (Style + Knowledge) |
| 无时效控制 | 可能引用过期数据 | **Publish_Date 字段 + 30 天过滤** |
| 无人工审核 | 自动入库 | **Status 字段**: 待处理 → 已审核 → 已入库 |
| TXT 协议脆弱 | N/A (Cleaner CLI 已较健壮) | **Markdown + YAML Frontmatter** 格式 |

---

## 2. 系统架构 (System Architecture)

### 2.1 数据流向图

```mermaid
graph TD
    subgraph "Local Environment (本地数据源)"
        A[📂 Web3素材/DeFi进展与分析/]
        B[📂 Web3素材/MemeCoin研究所/]
        C[📂 Web2风格/咪蒙/]
        D[📂 Web2风格/半佛仙人/]
    end

    subgraph "ETL Engine (cleaner_cli.py 扩展)"
        E[⚙️ 递归扫描]
        F[✂️ YAML Frontmatter 解析]
        G{🔀 路由判断}
    end

    subgraph "Lark Cloud (云端双脑)"
        H[(🎨 Style_Repo)]
        I[(🧠 Knowledge_Repo)]
    end

    subgraph "Quantum Engine (LangGraph)"
        J[Strategist Agent]
        K[Writer Agent]
        L[Critic Agent]
        M[Polisher Agent]
    end

    A & B --> E
    C & D --> E
    E --> F --> G
    G -- "有 Author 字段" --> H
    G -- "有 Topic 字段" --> I

    K <-.-> |风格检索| H
    K <-.-> |知识检索 (30天内)| I
    J --> K --> L --> M
```

### 2.2 技术栈 (复用 v5.0)

*   **ETL**: `cleaner_cli.py` (扩展 `--repo` 参数)
*   **后端**: FastAPI + LangGraph + AsyncIO
*   **前端**: Next.js + TailwindCSS
*   **数据库**: Lark 多维表格 (双表)

---

## 3. 数据库设计 (Lark Schema)

### 3.1 表 A: Style_Repo (风格库) - 现有表结构升级

> 继承现有 Lark 表，新增 `Status` 字段。

| 字段名称 | 类型 | 必填 | 备注 |
|----------|------|------|------|
| `content` | 多行文本 | ✅ | 风格样本正文 |
| `author` | 单选 | ✅ | 索引 (咪蒙, 半佛仙人, 新世相...) |
| `style` | 单选 | ✅ | 对应 MODE_TO_DIR (mimeng, banfo...) |
| `snippet_type` | 单选 | ✅ | Hook / Body / Ending / Golden / CTA |
| `logic_pattern` | 文本 | ❌ | AI 提取的逻辑公式 |
| `emotion` | 单选 | ❌ | Positive / Negative / Neutral / HighArousal |
| `quality_score` | 数字 | ✅ | 1-10 分 |
| `Status` | 单选 | ✅ | **新增**: 待处理 / 已审核 / 已入库 |

### 3.2 表 B: Knowledge_Repo (知识库) - 全新表

> 存储 Web3 行业事实，独立于风格。

| 字段名称 | 类型 | 必填 | 备注 |
|----------|------|------|------|
| `content` | 多行文本 | ✅ | 知识片段正文 |
| `topic_category` | 单选 | ✅ | **必须与 42 个文件夹名一致** |
| `publish_date` | 日期 | ✅ | **YYYY-MM-DD，用于时效过滤** |
| `fact_type` | 单选 | ✅ | Hard_Fact / Narrative / Slang |
| `source_file` | 文本 | ❌ | 来源文件名，方便溯源 |
| `content_hash` | 文本 | ✅ | MD5 哈希，防重复入库 |
| `Status` | 单选 | ✅ | 待处理 / 已审核 / 已入库 |

### 3.3 Topic_Category 选项 (42 赛道)

```
DeFi进展与分析, Layer2动态与分析, MemeCoin研究所, NFT市场动态,
比特币生态, 以太坊生态, Solana生态, 公链竞争格局,
稳定币与支付, 交易所动态, 监管与合规, 宏观经济与加密,
AI与加密交叉, GameFi与元宇宙, DePIN与硬件, 安全事件与漏洞,
DAO治理, 质押与再质押, 跨链与互操作, 钱包与用户体验,
开发者工具, 融资与投资, 人物与访谈, 社区文化与Meme,
数据分析与指标, 技术深度解析, 项目评测, 行业周报月报,
预测市场, RWA实物资产, 隐私与匿名, 比特币Ordinals,
空投与撸毛, 衍生品与期权, 链上数据分析, 机构动态,
矿业与能源, Web3社交, 去中心化存储, 身份与信用, Telegram生态, 其他热点
```

---

## 4. 素材录入协议 (Ingestion Protocol)

### 4.1 文件格式: Markdown + YAML Frontmatter

放弃 v3.0 的 `===` 分隔符，采用更标准的 Markdown 格式。

#### 知识库录入示例 (Knowledge Mode)

**文件路径**: `Web3素材/DeFi进展与分析/2026_01_uniswap.md`

```markdown
---
topic: DeFi进展与分析
date: 2026-01-17
type: Hard_Fact
---

Uniswap v4 的 hook 机制引发了关于流动性碎片化的讨论，但也带来了定制化 AMM 的新机会。据链上数据显示，v4 池在首周吸引了超过 $500M TVL。
```

#### 风格库录入示例 (Style Mode)

**文件路径**: `Web2风格/咪蒙/焦虑金句集.md`

```markdown
---
author: 咪蒙
style: mimeng
snippet_type: Golden
emotion: HighArousal
score: 9
---

你之所以觉得累，是因为你不够强。成年人的世界，没有"容易"二字。你以为的上限，只不过是别人的起点。
```

### 4.2 Cleaner CLI 扩展命令

```bash
# 清洗 Web3 知识素材 (写入 Knowledge_Repo)
python -m tools.cleaner_cli clean \
  --folder "data/Web3素材/DeFi进展与分析" \
  --repo knowledge \
  --topic "DeFi进展与分析"

# 清洗 Web2 风格素材 (写入 Style_Repo)
python -m tools.cleaner_cli clean \
  --folder "data/Web2风格/咪蒙" \
  --repo style \
  --author "咪蒙" \
  --style "mimeng"
```

---

## 5. Writer Agent 检索逻辑升级

### 5.1 双库并行检索

```python
# writer.py 伪代码
def get_rag_context(mode: str, topic: str, emotion: str) -> str:
    # 1. 风格检索 (Style_Repo)
    style_samples = sync_service.get_samples(
        repo="style",
        style=mode,
        emotion=emotion,
        status="已入库",
        count=3
    )
    
    # 2. 知识检索 (Knowledge_Repo) - 带时效过滤
    knowledge_samples = sync_service.get_samples(
        repo="knowledge",
        topic=topic,
        status="已入库",
        date_filter="30d",  # 仅检索 30 天内的知识
        count=5
    )
    
    # 3. 组装上下文
    context = "=== 风格范例 (模仿语气) ===\n"
    context += format_samples(style_samples)
    context += "\n=== 行业知识 (引用事实) ===\n"
    context += format_samples(knowledge_samples)
    
    return context
```

### 5.2 时效过滤规则

| Fact_Type | 默认时效 | 说明 |
|-----------|----------|------|
| Hard_Fact | 30 天 | 币价、TVL 等硬数据，过期即废 |
| Narrative | 90 天 | 叙事观点，衰减较慢 |
| Slang | 永久有效 | "Diamond Hands" 等黑话不过期 |

---

## 6. 运营 SOP (Standard Operating Procedure)

### 6.1 日常操作流程

1. **素材归档**:
   - Web3 资料 → `data/Web3素材/{赛道名}/` (42 个文件夹)
   - Web2 语录 → `data/Web2风格/{博主名}/`

2. **格式录入**:
   - 每个 `.md` 文件 = 一条独立记录
   - 必须包含 YAML Frontmatter (---包裹)
   - 知识库必填: `date`, `type`
   - 风格库必填: `author`, `style`, `snippet_type`

3. **运行清洗**:
   ```bash
   python -m tools.cleaner_cli clean --folder data/Web3素材/MemeCoin研究所 --repo knowledge
   ```

4. **Lark 审核**:
   - 每日检查 `Status = 待处理` 的记录
   - 人工审核后改为 `已入库`
   - **Writer 仅读取 `已入库` 的数据**

### 6.2 质量红线

| 红线 | 处理方式 |
|------|----------|
| 缺少 `date` 字段 | 拒绝入库，日志报错 |
| `topic_category` 不在 42 选项内 | 警告 + 自动归类为 "其他热点" |
| 内容 MD5 重复 | 跳过，不重复入库 |
| 单条内容 > 3000 字 | 自动分片 |

---

## 7. 实施计划 (Rollout Plan)

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| **Phase 1** | Day 1 | Lark 新建 `Knowledge_Repo` 表，配置 42 个选项 |
| **Phase 2** | Day 2 | 扩展 `cleaner_cli.py` 支持 `--repo knowledge` |
| **Phase 3** | Day 3 | 修改 `writer.py` 双库检索 + 时效过滤 |
| **Phase 4** | Day 4+ | 运营团队批量录入素材 |

---

## 8. 风险与缓解 (Risk Management)

| 风险 | 严重性 | 缓解措施 |
|------|--------|----------|
| 42 赛道维护成本高 | 中 | 脚本启动时自动校验本地文件夹与 Lark 选项一致性 |
| YAML 格式错误 | 低 | Cleaner CLI 增加 YAML 校验 + 详细报错 |
| 双库检索性能 | 低 | 利用 Lark 索引，单次检索 <500ms |
| 运营执行不到位 | 高 | 每周抽查 `Status=待处理` 堆积量 |

---

*文档结束 - Quantum Studio v5.1 UCB 升级方案*
