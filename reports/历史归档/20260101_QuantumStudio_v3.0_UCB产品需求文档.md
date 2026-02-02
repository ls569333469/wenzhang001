# 📑 Quantum Studio v3.0 - Unified Content Brain (UCB) 产品需求文档

| **项目名称** | **Quantum Studio v3.0 (Twin-Engines)** | **密级** | **核心机密 (Core Confidential)** |
| --- | --- | --- | --- |
| **版本号** | **V3.1 (Final Executable)** | **架构师** | Quantum Architect |
| **核心变更** | **全链路 TXT 流标准化**：基于本地文件夹结构与 TXT 强协议，实现自动化清洗入库。 |  |  |
| **适用角色** | 开发工程师 (Python), 数据运营, 提示词工程师 (PE) |  |  |

---

## 1. 核心设计哲学 (Design Philosophy)

本系统基于 **“骨肉魂 (Bone-Flesh-Soul)”** 理论构建，旨在解决 AI 写作“有形无神”的痛点。

- **🦴 骨 (Bone - Structure)**：文章的逻辑骨架（开头、论证、结尾）。由 **`Snippet_Type`** 字段控制。
- **🥩 肉 (Flesh - Knowledge)**：Web3 的行业事实与逻辑。由 **左脑 (Knowledge_Repo)** 提供，**严格对应本地 42 个赛道文件夹**。
- **👻 魂 (Soul - Style)**：Web2 博主的语气与修辞。由 **右脑 (Style_Repo)** 提供，**严格对应 Lark 现有风格表**。

---

## 2. 系统架构与数据流 (System Architecture)

### 2.1 数据流向图 (Data Flow)

代码段

`graph TD
    %% 样式定义
    classDef file fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef logic fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef db fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    subgraph "Local Environment (本地数据源)"
        A[📂 文件夹: MemeCoin_研究所]:::file
        B[📂 文件夹: Layer2动态与分析]:::file
        C[📄 文件: 2026_01_资料.txt]:::file
        A & B --> C
    end

    subgraph "ETL Engine (Python处理层)"
        D[⚙️ 递归扫描 (Recursive Scan)]:::logic
        E[✂️ 切片分割 (Split by '===')]:::logic
        F[🧠 智能解析 (Meta Parser)]:::logic
        G{🔀 路由与回退 (Router)}:::logic
    end

    subgraph "Lark Cloud (云端大脑)"
        H[(🎨 Style_Repo / 风格库)]:::db
        I[(🧠 Knowledge_Repo / 知识库)]:::db
    end

    C --> D --> E --> F --> G
    G -- "Meta含 Author" --> H
    G -- "Meta含 Topic 或 文件夹推断" --> I`

---

## 3. 数据库详细设计 (Lark Schema)

请在 Lark 多维表格中严格配置以下字段。

### 3.1 表 A：Style_Repo (风格库)

> 数据源：对应之前的咪蒙/王川语录。
> 
> 
> 结构参考：您提供的 Lark 截图 1。
> 

| **字段名称** | **类型** | **必填** | **备注/约束** |
| --- | --- | --- | --- |
| **Content** | 多行文本 | ✅ | 存储 `[Body]` 内容 |
| **Author** | 单选 | ✅ | 核心索引 (如: 咪蒙, 王川) |
| **Style_Tags** | 多选 | ✅ | 风格标签 (如: 毒舌, 焦虑) |
| **Snippet_Type** | 单选 | ✅ | 选项: `Hook`, `Body`, `Ending`, `Golden`, `CTA` |
| **Logic_Formula** | 文本 | ❌ | AI 总结的逻辑公式 (如: "反讽 + 情绪宣泄") |
| **Quality_Score** | 数字 | ✅ | 范围: 1-5 (保留 1 位小数) |
| **Emotion** | 单选 | ❌ | 选项: `Positive`, `Negative`, `Neutral`, `High Arousal` |
| **Status** | 流程 | ✅ | 默认: `待处理` |

### 3.2 表 B：Knowledge_Repo (知识库)

> 数据源：对应本地 42 个文件夹。
> 
> 
> 结构参考：您提供的文件夹截图 2。
> 

| **字段名称** | **类型** | **必填** | **备注/约束** |
| --- | --- | --- | --- |
| **Content** | 多行文本 | ✅ | 存储 `[Body]` 内容 |
| **Topic_Category** | **单选** | ✅ | **选项必须与 42 个文件夹名称完全一致** (如 `DeFi进展与分析`) |
| **Publish_Date** | **日期** | ✅ | 格式: `YYYY-MM-DD` (**极其重要，用于时效过滤**) |
| **Fact_Type** | 单选 | ✅ | 选项: `Hard_Fact` (事实), `Narrative` (叙事), `Slang` (黑话) |
| **Source_File** | 文本 | ❌ | 记录来源 TXT 文件名，方便溯源 |
| **Status** | 流程 | ✅ | 默认: `待处理` |

---

## 4. TXT 录入协议 (Ingestion Protocol)

为了确保 Python 脚本能准确识别，**所有 TXT 文件必须遵守以下强协议**。

### 4.1 物理分隔符 (Physical Separator)

每一条独立的数据，必须使用 **`===`** (三个等号) 独占一行进行物理分隔。

### 4.2 知识库录入格式 (Knowledge Mode)

> 适用场景：将 42 个文件夹里的资料录入系统。
> 

**文件位置**：例如 `/Web3素材/DeFi进展与分析/2026_01.txt`

Plaintext

`===
[Meta]
Topic: DeFi进展与分析  <-- (选填，不填则自动取文件夹名)
Date: 2026-01-17      <-- (必填，YYYY-MM-DD)
Type: Hard_Fact       <-- (必填，Hard_Fact/Narrative/Slang)

[Body]
Uniswap v4 的 hook 机制引发了关于流动性碎片化的讨论，但也带来了定制化 AMM 的新机会。
===
===
[Meta]
Date: 2026-01-16
Type: Narrative

[Body]
(这条没写Topic，脚本会自动抓取父文件夹名 'DeFi进展与分析')
Vitalik 认为 L2 的未来在于互操作性。
===`

### 4.3 风格库录入格式 (Style Mode)

> 适用场景：录入咪蒙、王川等人的语录。
> 

Plaintext

`===
[Meta]
Author: 咪蒙
Tags: 毒舌, 焦虑
Type: Golden
Score: 5

[Body]
你之所以觉得累，是因为你不够强。成年人的世界，没有“容易”二字。
===`

---

## 5. ETL 脚本逻辑详解 (Python Logic)

请将此逻辑交付给开发人员。脚本名为 `ingest_master.py`。

### 5.1 递归扫描与智能推断 (Recursive Scan & Inference)

脚本需要遍历根目录下的所有子文件夹。

Python

`# 伪代码逻辑
for root, dirs, files in os.walk("Web3素材库"):
    current_folder_name = os.path.basename(root) # 获取当前文件夹名，如 "DeFi进展与分析"
    
    for file in files:
        if file.endswith(".txt"):
            process_file(file_path, default_topic=current_folder_name)`

### 5.2 解析与路由核心 (Parser & Router)

Python

`def process_file(file_path, default_topic):
    content = read_file(file_path)
    snippets = content.split('===') # 物理切片
    
    for snippet in snippets:
        if not snippet.strip(): continue
        
        # 1. 提取 [Meta] 和 [Body]
        meta_dict, body_text = parse_meta_body(snippet)
        
        # 2. 路由逻辑 (Router)
        if 'Author' in meta_dict:
            # ---> 写入 Style_Repo
            data = {
                'Author': meta_dict['Author'],
                'Content': body_text,
                'Snippet_Type': meta_dict.get('Type', 'Body'),
                'Quality_Score': float(meta_dict.get('Score', 3))
            }
            lark.create_record("Style_Repo", data)
            
        else:
            # ---> 写入 Knowledge_Repo
            # 智能回退：如果 Meta 里没写 Topic，就用文件夹名
            final_topic = meta_dict.get('Topic', default_topic)
            
            # 日期格式强校验
            date_str = meta_dict.get('Date')
            if not validate_date(date_str):
                log_error(f"日期格式错误: {date_str}, 文件: {file_path}")
                continue
                
            data = {
                'Topic_Category': final_topic,
                'Content': body_text,
                'Publish_Date': date_str,
                'Fact_Type': meta_dict.get('Type', 'Hard_Fact')
            }
            lark.create_record("Knowledge_Repo", data)`

---

## 6. 运营操作 SOP (Standard Operating Procedure)

请发给数据运营人员。

1. **文件归档**：
    - 所有的 Web3 资料，必须扔进对应的 **42 个文件夹** 里。不要乱放。
    - 文件名随意，建议带上日期，如 `20260117_补充.txt`。
2. **格式录入**：
    - 打开 TXT，每条资料之间必须打 **`===`**。
    - **Web3 资料**：必须写 `Date` 和 `Type`。`Topic` 可以不写（只要文件在对的文件夹里）。
    - **Web2 语录**：必须写 `Author`。
3. **运行脚本**：双击运行 `ingest_master.py`。
4. **Lark 检查**：
    - 每天下班前，去 Lark 表格看一眼。
    - 如果发现 `Status` 是 `待处理`，人工快速扫一眼，没问题就改成 `已入库`。
    - **Writer Agent 只会读取 `已入库` 的数据。**

---

## 7. 潜在风险与防御 (Risk Management)

| **风险点** | **严重性** | **解决方案** |
| --- | --- | --- |
| **日期格式错误** | 高 | 脚本中加入正则校验 `^\d{4}-\d{2}-\d{2}$`。不符合的直接报错跳过，防止污染数据库。 |
| **文件夹名不匹配** | 中 | 脚本在启动时，先拉取 Lark 的 `Topic_Category` 选项列表。如果本地文件夹名（如 `DeFi`）不在 Lark 选项里，抛出警告。 |
| **分隔符丢失** | 高 | 如果单条 `[Body]` 长度超过 2000 字，视为分隔符丢失，脚本自动拒绝入库并报警。 |
| **重复入库** | 中 | 计算 `Body` 内容的 MD5 哈希值。入库前先查重。 |