# Lark 数据清洗工具架构流程图

> **版本**: v1.0 | **更新日期**: 2026-01-25

---

## 1. 系统架构总览

```mermaid
graph TB
    subgraph Frontend["前端 (Next.js)"]
        KP["/knowledge 页面"]
        SP["/settings 页面"]
    end
    
    subgraph Backend["后端 (FastAPI)"]
        API["/ingest/* API"]
        CONFIG["/config/* API"]
    end
    
    subgraph Scripts["入库脚本"]
        OPT["ingest_optimized.py<br>(优化版 推荐)"]
        LEG["ingest_knowledge.py<br>(旧版 兜底)"]
        BATCH["batch_ingest.py<br>(分批执行)"]
    end
    
    subgraph Core["核心模块"]
        LC["lark_client.py<br>(Lark API)"]
        HC["hash_cache.py<br>(本地查重)"]
        LLM["llm.py<br>(LLM 调用)"]
    end
    
    subgraph External["外部服务"]
        LARK["Lark/飞书 API"]
        VOLC["Volcengine LLM"]
    end
    
    KP --> API
    SP --> CONFIG
    API --> OPT
    API --> LEG
    OPT --> LC
    OPT --> HC
    OPT --> LLM
    LEG --> LC
    LEG --> LLM
    BATCH --> OPT
    LC --> LARK
    LLM --> VOLC
```

---

## 2. 入库流程详细图

### 2.1 优化版入库流程 (ingest_optimized.py)

```mermaid
flowchart TD
    START([开始]) --> ARGS[解析命令行参数]
    ARGS --> SOURCE{数据源?}
    
    SOURCE -->|--folder| SINGLE[单个文件夹]
    SOURCE -->|--all| ALL[所有文件夹]
    SOURCE -->|--path| CUSTOM[自定义目录]
    
    SINGLE --> FOLDER[process_folder]
    ALL --> LOOP[遍历所有文件夹]
    CUSTOM --> FOLDER
    LOOP --> FOLDER
    
    FOLDER --> SCAN[扫描 JSON 文件]
    SCAN --> LIMIT{有 limit 限制?}
    LIMIT -->|是| SLICE[截取前 N 个]
    LIMIT -->|否| ALLFILES[所有文件]
    
    SLICE --> CONCURRENT
    ALLFILES --> CONCURRENT
    
    CONCURRENT[并发处理<br>LLM_CONCURRENCY=5]
    
    subgraph PROCESS["process_single_file (并发)"]
        READ[读取 JSON]
        READ --> VALIDATE{content >= 50字?}
        VALIDATE -->|否| SKIP1[跳过]
        VALIDATE -->|是| CLEAN[清洗内容]
        CLEAN --> HASH[计算 MD5 Hash]
        HASH --> CACHE{Hash 缓存查重}
        CACHE -->|已存在| SKIP2[跳过]
        CACHE -->|不存在| LLM_CALL[调用 LLM<br>analyze_content_merged]
        LLM_CALL --> BUILD[构建 Lark 记录]
        BUILD --> QUEUE[添加到上传队列]
    end
    
    CONCURRENT --> PROCESS
    PROCESS --> COLLECT[收集结果]
    COLLECT --> UPLOAD{有记录需上传?}
    UPLOAD -->|是| BATCH_UP[批量上传 Lark<br>每批 500 条]
    UPLOAD -->|否| SAVE_HASH
    BATCH_UP --> SAVE_HASH[保存 Hash 缓存]
    SAVE_HASH --> END([结束])
```

### 2.2 旧版入库流程 (ingest_knowledge.py)

```mermaid
flowchart TD
    START([开始]) --> ARGS[解析命令行参数]
    ARGS --> FOLDER[选择文件夹]
    FOLDER --> SCAN[扫描 JSON 文件]
    
    SCAN --> EACH[逐个处理文件]
    
    subgraph PROCESS["process_json_file (串行)"]
        READ[读取 JSON]
        READ --> CLEAN[清洗内容]
        CLEAN --> HASH[计算 Hash]
        HASH --> API_CHECK{Lark API 查重}
        API_CHECK -->|已存在| SKIP[跳过]
        API_CHECK -->|不存在| LLM1[LLM 调用 1<br>score_content_async]
        LLM1 --> LLM2[LLM 调用 2<br>extract_entities_keywords]
        LLM2 --> BUILD[构建记录]
        BUILD --> SINGLE_UP[单条上传 Lark]
    end
    
    EACH --> PROCESS
    PROCESS --> NEXT{还有文件?}
    NEXT -->|是| EACH
    NEXT -->|否| END([结束])
```

---

## 3. 核心模块依赖图

```mermaid
graph LR
    subgraph Entry["入口点"]
        CLI["命令行<br>python -m scripts.xxx"]
        API["FastAPI<br>/ingest/start"]
    end
    
    subgraph Scripts["主脚本"]
        OPT["ingest_optimized.py"]
        LEG["ingest_knowledge.py"]
    end
    
    subgraph Utils["工具模块"]
        HC["hash_cache.py"]
        HC_DATA["processed_hashes.json"]
    end
    
    subgraph Core["核心服务"]
        LC["lark_client.py"]
        LLM["llm.py"]
    end
    
    subgraph Data["数据目录"]
        W3["data/Web3素材/"]
        W2["data/Web2风格/"]
        CUSTOM["自定义目录"]
    end
    
    CLI --> OPT
    CLI --> LEG
    API --> OPT
    API --> LEG
    
    OPT --> HC
    HC --> HC_DATA
    
    OPT --> LC
    OPT --> LLM
    LEG --> LC
    LEG --> LLM
    
    OPT --> W3
    OPT --> W2
    OPT --> CUSTOM
    LEG --> W3
```

---

## 4. 文件索引

### 4.1 核心入库脚本

| 文件 | 路径 | 功能 | 关键函数 |
|------|------|------|----------|
| **优化版入库** | `scripts/ingest_optimized.py` | 批量入库 (推荐) | `main`, `process_folder`, `process_single_file`, `analyze_content_merged` |
| **旧版入库** | `scripts/ingest_knowledge.py` | 批量入库 (兜底) | `main`, `process_folder`, `process_json_file`, `score_content_async`, `extract_entities_keywords` |
| **分批执行** | `scripts/batch_ingest.py` | 分 9 批执行 | `main`, `run_batch` |

### 4.2 核心模块

| 文件 | 路径 | 功能 | 关键类/函数 |
|------|------|------|-------------|
| **Lark 客户端** | `app/core/lark_client.py` | Lark API 封装 | `LarkClient`, `create_record`, `batch_create_records`, `list_records` |
| **Hash 缓存** | `scripts/batch/hash_cache.py` | 本地查重 | `HashCache`, `get_hash_cache`, `compute_content_hash` |
| **LLM 服务** | `app/core/llm.py` | LLM API 封装 | `call_llm`, `call_volcengine` |

### 4.3 辅助脚本

| 文件 | 路径 | 功能 |
|------|------|------|
| **字段审计** | `scripts/audit_knowledge_fields.py` | 检查/删除/创建表字段 |
| **清空表** | `scripts/clear_knowledge_repo.py` | 删除表中所有记录 |
| **数据验证** | `scripts/verify_lark_data.py` | 验证入库数据完整性 |
| **重建表** | `scripts/recreate_knowledge_repo.py` | 重建 Knowledge 表 |

### 4.4 前端相关

| 文件 | 路径 | 功能 |
|------|------|------|
| **Knowledge 页面** | `frontend/src/app/(main)/knowledge/page.tsx` | 可视化入库管理 |
| **Settings 页面** | `frontend/src/app/(main)/settings/page.tsx` | 数据清洗配置 |

### 4.5 后端 API

| 端点 | 文件 | 功能 |
|------|------|------|
| `POST /ingest/start` | `app/main.py` | 启动入库任务 |
| `GET /ingest/status` | `app/main.py` | 获取入库状态 |
| `GET /ingest/browse` | `app/main.py` | 浏览本地目录 |
| `GET/PUT /config/ingest` | `app/main.py` | 数据清洗配置 |

---

## 5. 函数调用链

### 5.1 优化版入库调用链

```
main()
├── process_folder(folder_path, topic, limit, target)
│   ├── get_hash_cache() → HashCache
│   ├── asyncio.gather(*tasks)
│   │   └── process_single_file(json_file, topic, hash_cache, semaphore)
│   │       ├── json.load() → 读取 JSON
│   │       ├── clean_content(content) → 清洗内容
│   │       ├── compute_hash(content) → MD5 哈希
│   │       ├── hash_cache.contains(hash) → 本地查重
│   │       └── analyze_content_merged(content, title, topic) → LLM 调用
│   │           └── llm.call_volcengine(prompt) → Volcengine API
│   └── lark_client.batch_create_records(records) → 批量上传
│       └── requests.post() → Lark API
└── hash_cache.save() → 保存缓存
```

### 5.2 旧版入库调用链

```
main()
├── process_folder(folder_name, app_token, table_id, limit)
│   └── asyncio.gather(*tasks)
│       └── process_json_file(file_path, topic, app_token, table_id, semaphore)
│           ├── json.load() → 读取 JSON
│           ├── compute_hash(content) → MD5 哈希
│           ├── check_exists_async(hash) → Lark API 查重
│           ├── score_content_async(content, topic) → LLM 调用 1
│           ├── extract_entities_keywords(content, title) → LLM 调用 2
│           └── upload_record_async(...) → 单条上传
│               └── lark_client.create_record() → Lark API
```

---

## 6. 数据流图

```mermaid
flowchart LR
    subgraph Input["输入"]
        JSON["JSON 文件<br>{title, content, published_at}"]
    end
    
    subgraph Processing["处理"]
        CLEAN["清洗内容"]
        HASH["计算 Hash"]
        LLM["LLM 分析<br>{score, summary, entities, keywords, fact_type}"]
    end
    
    subgraph Output["输出"]
        LARK["Lark 记录<br>11 个字段"]
        CACHE["Hash 缓存<br>processed_hashes.json"]
        LOG["日志文件<br>logs/ingest_*.log"]
    end
    
    JSON --> CLEAN
    CLEAN --> HASH
    HASH --> LLM
    LLM --> LARK
    HASH --> CACHE
    LLM --> LOG
```

---

## 7. 配置文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| `.env` | `backend/.env` | 环境变量 (API 密钥等) |
| `processed_hashes.json` | `backend/data/processed_hashes.json` | Hash 缓存 |
| `user_config.json` | `backend/config/user_config.json` | 用户配置 |

### 7.1 必需的环境变量

```env
# Lark/飞书
LARK_APP_ID=cli_xxx
LARK_APP_SECRET=xxx
LARK_BASE_TOKEN=xxx
LARK_KNOWLEDGE_TABLE_ID=tblxxx     # Web3 表格
LARK_WEB2_TABLE_ID=tblxxx          # Web2 表格 (可选)

# LLM
ARK_API_KEY=xxx
```

---

## 8. 优化版 vs 旧版对比

```mermaid
graph LR
    subgraph OLD["旧版 (ingest_knowledge.py)"]
        A1["2 次 LLM 调用"]
        A2["Lark API 查重"]
        A3["单条上传"]
        A4["截取前 500 字摘要"]
    end
    
    subgraph NEW["优化版 (ingest_optimized.py)"]
        B1["1 次 LLM 调用"]
        B2["本地 Hash 查重"]
        B3["批量 500 条上传"]
        B4["LLM 生成一句话摘要"]
    end
    
    A1 -.->|"-50% Token"| B1
    A2 -.->|"-99% 查重时间"| B2
    A3 -.->|"-99% 网络时间"| B3
    A4 -.->|"质量提升"| B4
```

| 维度 | 旧版 | 优化版 |
|------|------|--------|
| LLM 调用 | 2 次/条 | 1 次/条 |
| 查重方式 | Lark API (慢) | 本地 Hash (快) |
| 上传方式 | 单条 | 批量 500 条 |
| 摘要生成 | 截取前 500 字 | LLM 生成 |
| 费用 | ¥16/5806 条 | ¥8/5806 条 |
| 时间 | 5-6h | 2h |

---

## 9. 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-01-25 | v1.0 | 初始版本：系统架构图、入库流程图、模块依赖图、文件索引 |
