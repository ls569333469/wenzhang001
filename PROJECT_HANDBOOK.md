# Quantum Studio v6.1 - 项目手册

> **更新日期**: 2026-01-19  
> **版本**: v6.1 (Enforcement Edition)  
> **维护者**: AI 开发团队

---

## 📐 文档规范

> 本手册是项目的 **Single Source of Truth**，所有重要决策、进度、问题追踪都应记录在此。

### 章节标准

| 图标 | 含义 | 使用场景 |
|:----:|:-----|:---------|
| 🟡 | 待处理问题 | 需要关注但未修复的问题 |
| 🟠 | 低优先级问题 | 可延后处理的问题 |
| 🟢 | 已修复问题 | 已解决的问题归档 |
| 📅 | 未来计划 | 短期和中期规划 |
| ✅ | 已完成 | 标记在 Initiative 标题后 |
| 🛠️ | 进行中 | 当前正在开发的功能 |

### 更新规则

1. **每次值班结束**时更新 `已知问题` 和 `未来计划`
2. **完成 Initiative**时在标题后添加 ✅ 并填写完成日期
3. **Bug 修复**记录在 `已修复问题` 章节，标注日期
4. **重大变更**需同步更新 `reports/` 目录下的交接报告

## 📦 项目概述

**Quantum Studio** 是一个基于多 Agent 协作的 AI 写作引擎，采用 LangGraph 编排多个专业化 Agent（Strategist、Writer、Critic、Polisher）完成高质量内容生成。

## 3. 系统架构 (System Architecture)

### 3.1 前端架构 (v6.2 Island Architecture)
> **状态**: Phase 3 (Island Layout)
> **文档**: `reports/design_docs/frontend_design/PHASE3_ISLAND_DESIGN.md`

前端采用 **Next.js 16 (App Router)** 构建的多页面应用 (MPA)，升级为 **Island Architecture** (岛屿架构)。

*   **路由结构**:
    *   `/dashboard`: 全局概览。
    *   `/studio`: **[核心]** 创作工坊，采用 **Z-Stack 浮岛布局**。
    *   `/knowledge`: 知识库管理。
    *   `/settings`: 系统配置。

*   **UI 布局 (The Athenaeum)**:
    1.  **Config Island (Left)**: 悬浮配置面板 (Mode, Style, Length)。
    2.  **Agent Island (Right)**: 悬浮智能体时间轴 (Thinking/Active/Done)。
    3.  **Central Canvas (Center)**: 沉浸式创作白板。
    4.  **Studio Navbar (Top)**: 胶囊式全局导航。

*   **状态管理**:
    *   `useStudioUI` (Zustand): UI 状态。
    *   `nuqs`: URL 状态同步。

### 3.2 后端架构 (FastAPI + LangGraph)
*   **服务入口**: `app.main:app` (FastAPI)。
*   **业务逻辑**:
    *   `/analyze`: 策略生成 (Strategist Agent)。
    *   `/generate`: 流式正文生成 (Writer Agent)。
    *   `/config/*`: 配置与 Lark 同步。
*   **Agent 编排**: 基于 `LangGraph` 的状态机模型，支持 Human-in-the-loop。

### 3.3 数据流 (Data Flow)
1.  **Ingestion**: `cleaner_cli.py` 清洗本地 TXT/MD -> 存入 Lark Base (双脑: Knowledge + Style)。
2.  **Retrieval**: Writer Agent 运行时，根据 `mode` 和 `topic` 从 Lark 检索 Top N 样本。
3.  **Generation**: SSE 流式推送 Token 到前端。
├── frontend/                    # Next.js 前端
│   └── src/
│       ├── app/                 # 页面路由
│       │   ├── page.tsx         # Dashboard
│       │   └── studio/          # Studio (Island Layout)
│       ├── components/          # UI 组件
│       │   ├── layout/          # Island, Navbar
│       │   └── timeline/        # AgentTimeline
│       └── features/            # 业务模块 (studio/...)
│
├── backend/                     # FastAPI 后端
│   └── app/
│       ├── main.py              # API 入口
│       ├── graph.py             # LangGraph 工作流
│       └── agents/              # Agent 实现
│
└── PROJECT_HANDBOOK.md          # 本文档
```

---

## ✅ 已完成功能 (Milestone)

### 🔹 Phase 3 - Island Architecture (v6.2) ✅
> **Goal**: 实现 "High-End Minimalism" 视觉风格，采用浮岛架构提升认知清晰度。
> **完成日期**: 2026-01-20

#### 核心交付
*   **Design Lab**: 验证了三种布局方案，最终选定 Visual Variant A。
*   **架构升级**:
    *   `IslandContainer`: 统一封装悬浮、阴影、圆角逻辑。
    *   `Z-Stack Layout`: 层叠式后的背景纹理与主体内容。
*   **组件实现**:
    *   `ConfigPanel`: 接入 `nuqs` 实现 URL 状态同步。
    *   `AgentTimeline`: 可视化 Agent 思考过程 (Pulse 动画)。
*   **技术债清理**:
    *   降级 Tailwind CSS 至 v3.4.17 以确保生态兼容性。
    *   清理了旧的 `(studio)` 路由组。

#### 关联文档
*   📄 **[Phase 1 Summary](reports/design_docs/frontend_design/PHASE1_SUMMARY.md)**
*   📄 **[Phase 2 Summary](reports/design_docs/frontend_design/PHASE2_SUMMARY.md)**
*   📄 **[Phase 3 Design](reports/design_docs/frontend_design/PHASE3_ISLAND_DESIGN.md)**

### 🔹 P1 - Agent 独立模型配置 ✅
- **后端**: 支持 Agent 级别的 API Key 和模型配置
- **前端**: 设置页面可为每个 Agent 分配不同的 LLM 提供商

### 🔹 P2 - 提示词工程系统 ✅
- **后端**: 基于 Jinja2 的 Prompt 模板系统，支持 API 读写
- **前端**: Prompt Engineering 独立标签页，带语法高亮编辑器

### 🔹 P3 - 选题参考功能 ✅
- **后端**: `GenerateRequest` 支持 `references` 字段
- **Strategist**: 结合参考素材进行选题分析
- **前端**: 三栏布局 + "Extra References" 动态列表输入

#### 3. 关联文档
*   📄 **[Lark 集成操作手册](reports/Lark_Integration_Guide.md)**
*   📄 **[素材库设计方案](reports/Material_Integration_Design.md)**
*   📄 **[Lark 数据清洗规范 v3.0](reports/design_docs/Lark_Data_Cleaning_v3.0.md)** ✨ NEW
*   📄 **[白班员工审查报告](reports/白班员工_代码检查报告_20260111.md)**

### 🔹 P12.2 - Lark 数据清洗 v3.0 ✅ (2026-01-18)
> **Goal**: 实现 Web3 知识库的 Antigravity 智能清洗，解决长文本问题，优化 RAG 检索效果。

#### 核心交付
*   **双引擎架构**: Web2 风格库 (教"怎么写") + Web3 知识库 (给"写什么")
*   **Antigravity 接入**: LLM 自动提取结构化 JSON (标题、摘要、关键词、深度、类型)
*   **表结构统一**: 全中文字段名，核心摘要（3-5句话）替代长文本
*   **入库脚本**: `scripts/ingest_antigravity.py` 支持批量自动化入库

#### 字段设计要点
| 字段 | 说明 |
|------|------|
| 核心摘要 | 3-5句话，用于 RAG 检索首选 |
| 信息深度 | 快讯 / 资讯 / 深度 |
| 事实类型 | 事实 / 观点 / 黑话 |
| 正文原文 | 完整原文备份，仅查证时调用 |

#### 关联文档
📄 **[Lark 数据清洗规范 v3.0](reports/design_docs/Lark_Data_Cleaning_v3.0.md)**

### 🔹 P8 - 智能素材熔炉 (Lark Integrated) ✅
> **Goal**: 接入 **Lark Base (飞书多维表格)** 作为素材中台，实现 Web3 投研素材的自动化采集与风格化注入。

#### 核心交付
*   **同步层 (Sync)**: `SyncService` 定时拉取 Lark 数据，支持中英文自动映射和本地缓存。
*   **生成层 (Gen)**: `Writer Agent` 成功接入 `FewShotSelector`，实现了基于 Lark 真实素材的风格化写作。
*   **前端 (UI)**: 新增 Status Monitor 面板 (已知存在 UI 重复渲染问题，列入 P10 修复)。

#### 2. 配置清单 (.env)
系统依赖以下 Lark API 凭证 (已获取):
- `Lark App ID`: `cli_a9e999fdc138c060`
- `Lark App Secret`: `oRJHGiCj5vQIL8OCp85ssdTJvLgLtk1E`
- `Lark Base Token`: `CSfdbzErqay4bnsISxEuuVais3g`
- `Lark Table ID`: `tblbHfS1y8Nuk34j`

###  P4 - 交互式选题 (Human-in-the-Loop) ✅
- **Strategist Prompt**: 生成多个选题方案 (Options)
- **API 拆分**:
  - `POST /analyze` — 仅运行 Strategist，返回选题选项
  - `POST /generate` — 接收 `selected_option`，跳过 Strategist 直接生成
- **前端流程**: "分析 → 选择 → 生成" 两阶段交互

### 🔹 P5 - Strategist UI 反馈优化 ✅
- **后端**: `/analyze` 端点改造为 SSE 流式响应
- **Agent 模块化**: `strategist.py` 拆分为：
  - `build_strategist_context()` — 加载上下文
  - `build_strategist_prompt()` — 构建提示词
  - `execute_strategist_analysis()` — 执行 LLM 调用
- **前端**: `handleAnalyze` 消费 SSE 流，实时显示思考进度

---

## 🔄 当前状态

| 指标 | 值 |
|------|-----|
| **阶段** | Phase 3 (Island Design) 完成，准备接入 Deep Research |
| **前端端口** | `localhost:3002` (Auto-allocated) |
| **后端端口** | `localhost:8004` (通过 `frontend/src/config/api.ts` 配置) |
| **已集成模型** | Gemini, DeepSeek, Doubao (火山引擎), OpenAI |

---

## 🔧 近期打磨方向 (Polish Backlog)

> 以下是可立即着手优化的细节任务，优先级从高到低排列。

### 🔴 高优先级

| 任务 | 说明 | 预估工时 |
|------|------|----------|
| **Prompt 精调** | 优化各 Agent 提示词，提升输出质量和一致性 | 2-4h |
| **API Key 持久化** | 改用后端 Session 或配置文件存储，避免浏览器缓存丢失 | 2h |
| **错误处理优化** | 添加 LLM 调用超时重试、友好错误提示 | 1-2h |

### 🟡 中优先级

| 任务 | 说明 | 预估工时 |
|------|------|----------|
| **风格库扩充** | 为各写作风格添加更多高质量样本文档 | 3-5h |
| **内容后处理** | 自动格式化输出、智能分段、标题层级优化 | 2-3h |
| **导出功能** | 支持一键导出为 Markdown / HTML 文件 | 1-2h |

### 🟢 低优先级

| 任务 | 说明 | 预估工时 |
|------|------|----------|
| **UI 动画细节** | 添加微交互、过渡动画、骨架屏加载态 | 2-3h |
| **深色模式** | 实现暗色主题切换 | 1-2h |
| **移动端适配** | 响应式布局调整 | 3-4h |

---

## 🎯 未来规划 (Roadmap)

### 📌 P6 - 内容历史与版本管理 (暂缓)
- [ ] 保存生成的内容到本地数据库 (SQLite/IndexedDB)
- [ ] 支持历史记录浏览和恢复
- [ ] 实现内容 Diff 对比

### 🚀 P6 (New) - 健壮性与持久化优化 (已完成) ✅
> 解决 API Key 丢失与 LLM 调用不稳定的痛点。

- [x] **后端配置持久化**:
  - [x] 实现 `/config/keys` 读写接口
  - [x] 使用 JSON 文件存储密钥 (带 gitignore)
- [x] **LLM 错误处理**:
  - [x] 引入 `tenacity` 实现指数退避重试
  - [x] 添加 LLM 请求超时控制
  - [x] 优化错误提示信息 (友好化)
- [x] **前端集成**:
  - [x] Settings 页面同步保存到后端
  - [x] 显示更详细的错误与重试状态

### 🚀 P7 (New) - 项目全盘体检与治理 (已完成) ✅
> 对项目进行首次全面健康检查，消除隐患，夯实基础。

- [x] **代码质量审计**:
  - [x] 前端 Lint/Type Check (消除 `any` 类型)
  - [x] 后端 PEP8 规范检查与无用代码清理
- [x] **功能完整性验证**:
  - [x] 核心链路 E2E 测试 (分析 -> 生成)
  - [x] 边界情况测试 (空输入、超长文本、服务宕机)
- [x] **架构与安全治理**:
  - [x] 目录结构规范化检查
  - [x] 敏感信息扫描 (Key 泄露检查)
  - [x] 文档与代码一致性核对

### 🩺 P7 体检报告 (Audit Report - 2026.01.10)

> 📄 **[点击查看详细报告文件](reports/P7_Audit_Report_20260110.md)**
> 📄 **[点击查看 2026 竞品分析报告](reports/Competitor_Analysis_2026.md)**

| 维度 | 状态 | 详情 |
|------|------|------|
| **后端代码** | 🟢 优秀 | `flake8` 扫描通过 (0 errors)。核心逻辑覆盖率高。 |
| **前端代码** | 🟢 良好 | 已修复 `require()` 引用和主要未使用变量。剩余少量 Warning。 |
| **功能验证** | 🟢 通过 | `/health`, `/config/keys` 接口响应正常。全流程 ( 分析 -> 生成) 正常运行。 |
| **安全性** | 🟢 安全 | `.gitignore` 正确包含 `user_config.json`。API Key 接口已脱敏。 |
| **架构健康** | 🟢 良好 | 目录结构清晰，配置管理 (Backend/Env) 优先级逻辑正确。 |

> **行动建议**: 下一步开发前建议优先修复前端的 Lint 警告，保持代码库零异味。

### � P10 - 前端清理与 Lark 深度集成 (进行中)
> **Goal**: 偿还 P8 开发过程中的前端技术债务，并完善“手动触发 -> 自动归档”的闭环。

- [ ] **前端修复**: 解决 Lark Status UI 重复渲染的 Bug。
- [ ] **代码清理**: 消除 ESLint 警告。
- [ ] **结果回写**: 仅在用户手动生成完成后，可选将结果归档回 Lark 表格。

### ⚠️ P9 - 自动化工作流引擎 (已废弃/Pivot)
> **Decision**: 经产品讨论，用户倾向于保留“人工触发”的控制权，拒绝后台自动生成。
> **Pivot**: 原 P9 的“自动 Worker”方案被取消，转而专注于 P10 的“辅助增强”路线。

### 📌 P11 - 导出与多渠道发布 (计划中)
- [ ] 导出为 Markdown / HTML / PDF
- [ ] 集成推送到 CMS (如 WordPress, Ghost)

### 📌 P11 - 风格微调系统 (远期)
- [ ] 支持上传样本文章进行风格学习
- [ ] 风格强度调节滑块
- [ ] 自定义禁用词列表

### 🛠️ P12 - Lark 数据清洗工具 (独立工具) ✅
> **Goal**: 一个独立的 Python 脚本/GUI 工具，用于批量清洗、去重、格式化 Lark Base 中的素材数据。
> **完成日期**: 2026-01-12

**交付物**:
- `backend/tools/cleaner_cli.py` - 核心 CLI 工具 (Shell-Kernel 壳肉分离法)
- 更新 `sync_service.py` FIELD_MAPPING (新增 `逻辑公式`, `质量分` 字段)
- 更新 `writer.py` Few-Shot 展示 (显示 `logic_pattern` 和 `snippet_type`)

**使用示例**:
```bash
# 处理单个文件
python -m tools.cleaner_cli clean --input data/mimeng/咪蒙2.txt --author 咪蒙 --style mimeng

# 处理整个文件夹
python -m tools.cleaner_cli clean --input data/mimeng/ --author 咪蒙 --style mimeng
```

### ⚡ P12.1 - 工业级清洗工具升级 ✅
> **Goal**: 将 P12 清洗工具升级为工业级版本，支持并发处理、断点续传、智能去重。
> **完成日期**: 2026-01-13

**核心升级 (Phase 1+2)**:
| 特性 | 说明 | 阶段 |
|:-----|:-----|:----:|
| AsyncIO 并发 | Semaphore(5) 控制，速度提升 5-10x | P1 |
| 断点续传 | `processed_log.json` 记录进度 | P1 |
| 智能分片 | 3000 字符/片，按段落切分 | P1 |
| API 自动重试 | `tenacity` 指数退避 (429/Timeout) | P2 |
| 双重去重 | 本地 MD5 + 服务端 Lark 查询 (`content_hash`) | P2 |
| 智能识别 | `--input` 支持单文件或文件夹 | P1 |

**效果**: 200万字处理时间 < 20 分钟，且具备高并发下的强鲁棒性。

**2026-01-13 Bug 修复**:
- 前端 API 端口配置 (8004 → 8002)
- Critic API Key 回退逻辑
- Lark Schema 补充 `content_hash` 字段
- LarkClient 增加 `filter` 支持

### ⚡ P12.2 - cleaner_cli v2.2 融合升级 ✅
> **Goal**: 融合 v2.0 异步架构与 v2.1 智能规划思想，打造最终工业级清洗工具。
> **完成日期**: 2026-01-14

**v2.2 新增特性**:
| 特性 | 说明 |
|:-----|:-----|
| 预扫描规划器 | 启动前显示文件数、总字符、分片数、预计耗时 |
| 多条提取 Prompt | 优化 Prompt 明确要求提取所有有价值素材 |
| 增强启动信息 | 更清晰的运行状态展示 |

**效果**: 957KB 文件提取 230 条素材 (较 v2.0 提升 35%)


---

## ⚠️ 已知问题与注意事项

### 🟡 待处理问题 (2026-01-13)

1. **LLM 时间感知错误**
   - *Issue*: 生成的文章中出现 "2024年" 而非 "2026年"
   - *原因*: LLM 未正确感知当前时间
   - *建议*: 在 Prompt 中注入当前日期

2. **Lark 旧 PS 内容**
   - *Issue*: 已入库的 PS 开头内容未被过滤
   - *建议*: 手动将 PS 内容的 quality_score 改为 1，或重新运行 cleaner_cli

### 🟢 已修复问题 (2026-01-15: Day Shift)

1. **Bug: Writer 节点超时 (P0)**:
   - *Issue*: `/generate` 工作流在 Writer 阶段因同步 LLM 调用阻塞 Loop 而超时。
   - *Fix*: `backend/app/graph.py` 中 `node_writer` 改为异步，并利用 `asyncio.to_thread` 将计算密集型/阻塞型操作移入线程池。

2. **UI: Lark Status 重复 (P2)**:
   - *Issue*: `page.tsx` 中重复渲染 Lark 状态组件。
   - *Fix*: 封装 `<LarkStatusCard />` 组件，清理冗余代码。

3. **Dev: 前端 Lint 警告 (P2)**:
   - *Issue*: 累积 20+ Lint 警告。
   - *Fix*: 修复 `any` 类型声明，移除未使用的变量和引用。

### 🟢 已修复问题 (2026-01-13)

1. **API 端口配置错误**:
   - *Issue*: 前端配置 8004，后端运行在 8002
   - *Fix*: `frontend/src/config/api.ts` 改为 8002

2. **Critic API Key 缺失**:
   - *Issue*: Critic 配置使用 deepseek 但无 Key
   - *Fix*: `graph.py` 增加回退逻辑，无 Key 时使用 volcengine

3. **Lark 情绪字段缺失**:
   - *Issue*: 上传时报 FieldNameNotFound
   - *Fix*: 运行 `update_lark_schema.py` 添加字段

### 🟢 已修复问题 (历史归档)

1. **API Key 存储 (Fixed in v5.0/P6)**:
   - *Issue*: Key 存储在前端 localStorage，易丢失。
   - *Fix*: 引入后端 `/config/keys` 接口与 `user_config.json` 进行持久化存储。

2. **LLM 调用超时 (Fixed in v5.0/P6)**:
   - *Issue*: 缺乏重试机制，网络波动导致任务失败。
   - *Fix*: 引入 `tenacity` 实现 3 次指数退避重试与超时控制。

---

## 📅 未来计划

### 🔜 短期 (本周)
- [x] 修复 LLM 时间感知问题 (已在 Prompt 中注入当前日期) ✅
### 🔜 短期 (本周)
- [x] 修复 LLM 时间感知问题 (已在 Prompt 中注入当前日期) ✅
- [x] 清理前端 Lint 警告 ✅
- [x] 移除重复的 Lark Status 组件 ✅
- [x] **回归核心功能 - 爆款内容生成测试** (已修复 Writer 超时问题) ✅
- [ ] 优化 UI 交互动画

### 📌 中期 (暂缓)
- [ ] Workflow Worker 集成 cleaner_cli (暂缓)
- [ ] 添加 chunk_index 字段支持入库排序

### 📌 远期 (P11)
- [ ] 支持上传样本文章进行风格学习
- [ ] 风格强度调节滑块
- [ ] 自定义禁用词列表

---

## 🚀 快速启动指南

### 1. 启动后端
```bash
cd d:/AI_Projects/2026001/backend
.\venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### 2. 启动前端
```bash
cd d:/AI_Projects/2026001/frontend
npm run dev
```

### 3. 访问应用
- 主页: http://localhost:3000
- 设置: http://localhost:3000/settings
- 健康检查: http://localhost:8002/health

---

## 📡 API 端点参考

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/analyze` | SSE 流式分析，返回选题选项 |
| `POST` | `/generate` | SSE 流式生成，执行完整工作流 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/config/models` | 获取可用模型列表 |
| `GET` | `/config/keys` | (新增) 获取 API Key 配置 |
| `POST` | `/config/keys` | (新增) 更新 API Key 配置 |
| `GET` | `/config/prompts` | 获取所有 Agent Prompt |
| `POST` | `/config/prompts/{agent}` | 更新指定 Agent Prompt |
| `GET` | `/config/styles` | 获取风格配置 |

---

## 📈 项目复盘 (Project Reviews)

本章节记录关键里程碑的深度复盘文档，用于指导后续迭代。

| 日期 | 版本 | 阶段 | 关键文档 | 核心结论 |
|------|------|------|----------|----------|
## 📈 项目复盘 (Project Reviews)

本章节记录关键里程碑的深度复盘文档，用于指导后续迭代。

| 日期 | 版本 | 阶段 | 关键文档 | 核心结论 |
|------|------|------|----------|----------|
| 2026-01-15 | v5.0 | Alpha | [项目复盘_20260115_v5.0_Alpha.md](reports/reviews/项目复盘_20260115_v5.0_Alpha.md) | 技术闭环完成，需进行全真长文压力测试以验证内容质量。 |

> 📂 **文档结构说明**:
> * `reports/daily_log/`: 日常交接报告与审计日志
> * `reports/design_docs/`: 技术方案、PRD与设计文档
> * `reports/reviews/`: 项目阶段性深度复盘


---

## 🧪 测试脚本


```bash
# 测试交互式流程 (SSE)
python backend/test_interactive_flow.py

# 测试完整工作流
python backend/test_full_flow.py

# 测试火山引擎连接
python backend/test_volcengine.py
```

---

## 📞 联系与支持

如有问题，请联系开发团队或在项目仓库提交 Issue。

---

*Last updated: 2026-01-10 22:53*
