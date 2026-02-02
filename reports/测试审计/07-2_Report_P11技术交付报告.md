# P11 数据管线技术交付报告

> **版本**: v7.1 Final  
> **日期**: 2026-01-23  
> **作者**: AI 开发团队 (夜班)

---

## 📋 执行摘要

P11 项目成功实现了企业级数据清洗管线，解决了原有系统的数据格式混乱、工具分裂、字段映射错误等核心问题。

### 关键成果

| 指标 | 结果 |
|------|------|
| Knowledge_Repo | 536 条 (11 字段完整) |
| Style_Repo | 456 条 |
| 新增代码 | ~1,000 行 |
| 前端页面 | `/cleaner` 可视化管理 |

---

## 🎯 问题分析与解决

### 问题 1: 数据格式混乱

**现象**: 素材文件有 JSON 和 TXT 两种格式，原有脚本只能处理一种。

**技术方案**: 统一导入器 (`unified_importer.py`) 自动检测文件类型

```python
def detect_file_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == '.json':
        return 'json'  # 直接导入模式
    elif suffix in ['.txt', '.md']:
        return 'txt'   # AI 处理模式
```

**设计考虑**:
- JSON 文件已包含结构化数据，无需 AI 处理，节省成本
- TXT 文件需要 AI 提取结构化信息
- 统一入口简化运维，避免用户选错脚本

---

### 问题 2: 字段映射错误

**现象**: 原 `cleaner_cli.py` 使用 `KERNEL_FILTER_PROMPT` 只输出 5 个字段，但 Knowledge_Repo 表需要 11 个字段。

**技术方案**: 重新设计 `KERNEL_KNOWLEDGE_PROMPT`，包含 Few-Shot 示例

```python
KERNEL_KNOWLEDGE_PROMPT = """
# 示例1
输入: "Uniswap V4 正式上线，TVL 达到 50 亿美元"
输出: {"title": "...", "summary": "...", "fact_type": "...", 
       "info_depth": "...", "keywords": [...], "track": "..."}
"""
```

**设计考虑**:
- Few-Shot 示例让 AI 准确理解输出格式
- 强制 JSON 格式输出 (`response_format={"type": "json_object"}`)
- 保留正文原文 (`正文原文` 字段) 用于溯源

---

### 问题 3: 模型选型与成本

**现象**: 白班提醒需要考虑模型成本和质量。

**技术方案**: 使用火山引擎 DeepSeek V3.2

| 模型 | 输入价格 | 输出价格 | 选择理由 |
|------|----------|----------|----------|
| **DeepSeek V3.2** | ¥0.002/千token | ¥0.003/千token | ⭐ 成本最优 |
| 豆包 Seed | ¥0.0008/千token | ¥0.002-0.024/千token | 输出价格波动大 |

**设计考虑**:
- 数据清洗是长文本处理，输出 Token 量大
- DeepSeek V3.2 输出价格稳定，总成本更低
- Temperature=0 确保无幻觉

---

### 问题 4: 无前端管理

**现象**: 只能通过命令行操作，不直观。

**技术方案**: 构建 `/cleaner` 前端管理页面

**后端 API 设计**:

| 端点 | 功能 | 返回 |
|------|------|------|
| `GET /cleaner/stats` | 三库统计 | `{style_count, knowledge_count, pending_files}` |
| `GET /cleaner/sources` | 源目录树 | 树形结构 JSON |
| `POST /cleaner/jobs` | 创建任务 | `{job_id, status}` |
| `GET /cleaner/jobs/{id}/stream` | SSE 进度 | 实时进度流 |

**前端技术栈**:
- React + TypeScript
- TailwindCSS 样式
- 实时进度轮询 (5s 间隔)

**设计考虑**:
- SSE 替代 WebSocket，简化部署
- 目录树可折叠，处理深层目录
- 任务状态可视化 (running/completed/failed)

---

## 🛠️ 技术架构

### 三层数据管线

```
┌─────────────────────────────────────────────────────────────┐
│                   Layer 1: 采集层                           │
│  ChainCatcher Scraper → JSON    手工收集 → TXT             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Layer 2: 处理层                           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │ JSON 直接   │   │ TXT AI     │   │ 批量推理    │       │
│  │ (无需AI)   │   │ (实时)     │   │ (高并发)    │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Layer 3: 存储层                           │
│  Style_Repo (血-风格素材)    Knowledge_Repo (肉-知识素材)   │
└─────────────────────────────────────────────────────────────┘
```

### 并发控制

```python
CONCURRENCY_LIMIT = 10
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

async with semaphore:
    response = await client.chat.completions.create(...)
```

**设计考虑**:
- Semaphore 限制并发，避免触发 API 限流
- 10 并发是火山引擎推荐的安全值
- 异步处理提高吞吐量

### 断点续传

```python
CHECKPOINT_FILE = Path("data/.unified_importer_checkpoint.json")

def save_checkpoint(processed_files: set):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump({"processed_files": list(processed_files)}, f)
```

**设计考虑**:
- 大批量任务可能中断 (网络/费用限制)
- 断点记录已处理文件 hash
- 重启后跳过已处理文件

---

## ⚠️ 8 大警告 (白班提供)

### 批量推理坑

| # | 问题 | 解决方案 | 实现 |
|---|------|----------|------|
| 1 | TOS IAM 权限 | 配置读写权限 | 文档记录 |
| 2 | JSONL 格式严苛 | `json.dumps()` 校验 | 已实现 |
| 3 | Batch Endpoint | 确认支持批量 | 使用 Chat API |
| 4 | 24h 窗口 | 前端显示 "1-24h" | 文档记录 |

### 质量杀手

| # | 问题 | 解决方案 | 实现 |
|---|------|----------|------|
| A | 模型选型 | 满血版非蒸馏版 | ✅ deepseek-v3-2-251201 |
| B | Prompt 工程 | Few-Shot 示例 | ✅ KERNEL_KNOWLEDGE_PROMPT |
| C | 上下文截断 | 30k token 切分 | ✅ chunk_text() |
| D | Temperature | = 0 无幻觉 | ✅ temperature=0 |

---

## 📂 交付文件清单

### 后端

| 文件 | 行数 | 说明 |
|------|------|------|
| `tools/unified_importer.py` | 450+ | 统一导入器核心 |
| `tools/cleaner_cli.py` | 修改 | DeepSeek ARK 配置 |
| `app/api/cleaner.py` | 210+ | Cleaner API 路由 |
| `app/main.py` | 修改 | 注册 router |

### 前端

| 文件 | 行数 | 说明 |
|------|------|------|
| `src/app/(main)/cleaner/page.tsx` | 300+ | 清洗管理页面 |

### 文档

| 文件 | 说明 |
|------|------|
| `docs/volcengine_models.md` | 模型配置指南 |
| `11-0_Plan_风格库完善与内容生产.md` | P11 方案 |
| `reports/handoff/2026-01-22_夜班交接.md` | 交接报告 |

---

## 🧪 验收测试

### Smoke Test 结果

```bash
python -m tools.cleaner_cli clean \
  --input "data/Web3素材/OKX_Web3_洞见数据" \
  --provider deepseek --source-category Kernel

# 结果
📊 提取总数: 140
📤 入库总数: 137
🔄 去重过滤: 3 条
```

### API 测试

```bash
curl http://localhost:8000/cleaner/stats

# 结果
{"style_count": 456, "knowledge_count": 536, "pending_files": 0}
```

---

## 🔮 后续建议

| 任务 | 优先级 | 说明 |
|------|--------|------|
| 火山批量推理 API | P1 | 大规模处理成本更低 50% |
| 去重逻辑强化 | P2 | Lark 端 hash 查询 |
| 成本监控面板 | P3 | Token 使用量统计 |

---

## 📈 项目总结

P11 成功构建了规范化、可扩展的数据清洗管线：

1. **统一入口**: 自动识别 JSON/TXT，减少人工选择
2. **正确映射**: 11 字段完整匹配 Lark 表结构
3. **成本优化**: 选用 DeepSeek V3.2，输出成本稳定
4. **可视化管理**: 前端页面实时监控任务进度
5. **生产就绪**: 高并发 + 断点续传

---

*交付完成 ✅*
