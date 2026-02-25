# Quantum Studio v12.0 - 项目手册

> **更新日期**: 2026-02-25  
> **版本**: v12.0 (P31 投研模块 + 自动化内容调度)  
> **维护者**: AI 开发团队

---

##  项目概述

**Quantum Studio** 是一个基于多 Agent 协作的 **爆款内容生成引擎**，采用 LangGraph 编排 4 个专业化 Agent（Strategist → Writer → Critic → Polisher）完成高质量 Web3 内容生成。

### 核心价值主张
> 不只是 AI 写作，而是 **专门帮你打造爆款**。

### 技术栈

| 层 | 技术 |
|---|------|
| **前端** | Next.js 16 + Tailwind CSS + Shadcn/UI + TipTap 富文本编辑器 |
| **后端 API** | FastAPI (Python 3.13) |
| **Agent 编排** | LangGraph (有状态工作流) |
| **LLM 模型** | 火山引擎 (豆包 Seed / DeepSeek V3.2) + Google Gemini |
| **投研数据** | Surf AI API (surf-1.5) + leak.me KOL Tracker |
| **实时数据** | Grok API (X/Twitter 实时搜索) |
| **数据源** | Google Sheets (风格样本 + 知识库 + 素材池) |

---

## 🩸🥩 核心理念：血与肉

> ⚠️ **这是整个项目的灵魂，必须牢记！**

| | 定义 | 来源 | 作用 |
|:---:|------|------|------|
| **🩸 血** | Web2 博主风格素材 | 咪蒙/半佛/新世相/视觉志... | 提供 **写作技巧和爆款风格** |
| **🥩 肉** | Web3 媒体专业知识 | ChainCatcher/Lark 知识库 | 提供 **行业内容和专业度** |

### 系统核心逻辑

```
        🩸 血 (How to Write)           🥩 肉 (What to Write)
   ┌─────────────────────────┐    ┌─────────────────────────┐
   │  咪蒙：情绪戳刺、金句爆发   │    │  DeFi/NFT/L2 深度研究    │
   │  半佛：反常识、案例轰炸     │    │  项目分析/行业趋势       │
   │  新世相：情感共鸣、故事叙述  │    │  热点追踪/投资逻辑       │
   └────────────┬────────────┘    └────────────┬────────────┘
                │                              │
                └──────────┬───────────────────┘
                           ↓
                   🔥 Web3 爆款内容
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
        📱 Twitter                💰 币安广场
        (海外 KOL)                 (中文社区)
```

### 关键理解
- **血** 决定 "怎么写" → 风格、句式、情绪节奏、爆款公式
- **肉** 决定 "写什么" → Web3 专业内容、数据、案例
- **最终产出** = 用 Web2 爆款技巧包装 Web3 专业内容

---

## 🏗️ 系统架构

### 创作管线 (4 级 Agent)

```
用户输入素材
    ↓
┌─ Strategist ────────────────────────────────┐
│  • RAG 检索 (Google Sheets 知识库)            │
│  • 生成 Context Card (P20 事件脉络感知)       │
│  • 生成 3 个标题选项                          │
│  • 推荐创作模式 (P22 智能模式匹配)            │
└─────────────────────────────────────────────┘
    ↓ 用户选择标题 + 确认/覆盖模式
┌─ Writer ────────────────────────────────────┐
│  • 8 种独立 Writer (per-mode .py + .jinja2)  │
│  • Anti-AI 禁用词约束 (P21, 250+ 词)         │
│  • 生成 3 个变体版本供选择                    │
└─────────────────────────────────────────────┘
    ↓
┌─ Critic ────────────────────────────────────┐
│  • 5 个模式专用模板 (P24 独立化)              │
│  • 5 维度评分 + AI 痕迹检测                   │
│  • score < 阈值 → 自动触发重写 (阈值/次数按模式) │
└─────────────────────────────────────────────┘
    ↓
┌─ Polisher ──────────────────────────────────┐
│  • 4 个模式专用模板 (P24 独立化)              │
│  • 最终检查清单 (节奏、禁用词、格式)           │
└─────────────────────────────────────────────┘
    ↓
最终文章输出 (TipTap 富文本编辑器, P19)
```

### 8 种创作模式 (P27 规划)

| 模式 | 字数 | Critic | Polisher | 状态 | 定位 |
|------|:---:|:---:|:---:|:---:|------|
| `hot_take` 🔥 锐评 | 50-150 | ✅ | ✅ | 🔄 改走管线 | Twitter 快评 |
| `bullish_take` 🌸 吹捧 | 50-500 | ✅ | ✅ | ✅ P30 完成 | 币安/CZ/何一正面解读 |
| `kaito_yap` 🎯 Kaito | — | ✅ | ✅ | 🆕 P27 | 项目嘴撸任务 |
| `short_article` 💎 短篇 | 50-300 | ✅ | ⏭️ | ✅ | 每日快评/碎句节奏 |
| `mid_article` ⬛ 中篇 | 150-800 | ✅ | ✅ | ✅ | 深度 Thread |
| `long_article` 📖 长篇 | 900-1800 | ✅ | ✅ | ✅ | 专题研究报告 |
| `tutorial` 📚 教程 | 400-1500 | ✅ | ✅ | ⏸️ 延后 | 技术教程/指南 |
| `project_research` 🔬 投研 | — | — | — | 🔄 P31 | Surf API 投研快报 |
| ~~`rewrite` 改写~~ | — | — | — | ❌ 已删 | ~~占位符~~ |

### P31 投研模块（独立 Pipeline）

```
Layer 1: 选题发现 → Surf API 搜索 @leakmealpha (leak.me KOL Tracker)
Layer 2: 分类定级 → 判断项目阶段/可利用数据/关键事件
Layer 3: 深度分析 → 阶段适配模板（概念/已融资/Pre-TGE/已上线/成熟）
Layer 4: 报告组装 → Markdown 详细版 + HTML 配图（截图发推特）
```

详见: [P31_投研模块设计方案.md](file:///d:/AI_Projects/2026001/reports/设计文档/P31_投研模块设计方案.md)

### 核心特性

| 特性 | 阶段 | 说明 |
|------|:---:|------|
| TipTap 富文本编辑器 | P19 | 流式输出、AI 局部重写、版本历史+Diff对比、统一侧边栏 |
| Context Card 事件脉络 | P20 | Strategist 自动生成 summary/time_context/forward_look |
| Anti-AI Trace 痕迹消除 | P21 | 250+ 禁用词库 (YAML) 自动注入所有 Agent |
| 智能模式匹配 | P22 | Strategist 分析素材后自动推荐 short/mid/long |
| 每日素材源系统 | P23 | ChainCatcher 爬虫 → AI 预筛选 → Sheets 存储 → 前端素材中心 |
| 全模式独立管线 | P24 | Critic/Polisher per-mode 独立模板 + 模型配置 |
| 短篇提示词大优化 | P26 | 连珠炮式节奏、4层内容层级、人味化、25篇 benchmark |
| 创作保存 + 模式重构规划 | P27 | 本地 Markdown 存储、历史浏览、8 模式重构方案 |
| 吹捧模式提示词定稿 | P30 | A/B 测试 + 合规性优化 + 最终 prompt 确定 |
| 投研模块 POC + 设计方案 | P31 | Surf API 验证 + 4 层架构设计 + HTML 配图模板 |

---

## 📂 目录结构

```
├── backend/
│   └── app/
│       ├── main.py                     # API 入口
│       ├── graph.py                    # LangGraph 工作流编排
│       ├── agents/
│       │   ├── strategist.py           # 策略师 (mode 变量注入)
│       │   ├── writer/                 # 8 模式独立 Writer (P27)
│       │   │   ├── hot_take.py
│       │   │   ├── short_article.py
│       │   │   ├── mid_article.py
│       │   │   ├── long_article.py
│       │   │   └── tutorial.py
│       │   ├── critic/                 # ✅ P24 独立化
│       │   │   ├── __init__.py         # CRITIC_REGISTRY (mode→handler)
│       │   │   ├── standard.py         # per-mode render_prompt
│       │   │   └── skip.py             # hot_take 跳过
│       │   └── polisher/               # ✅ P24 独立化
│       │       ├── __init__.py
│       │       ├── standard.py
│       │       └── skip.py
│       ├── api/
│       │   ├── materials.py            # P23 素材 CRUD
│       │   ├── creations.py            # P27 创作保存 CRUD
│       │   ├── rewrite.py              # P19 AI 局部重写
│       │   └── cleaner.py              # 数据清洗工具
│       ├── core/
│       │   ├── prompts.py              # 模板渲染 + 词库注入
│       │   └── forbidden_patterns.py   # P21 禁用词加载器
│       └── services/
│           ├── material_fetcher/       # P23 爬虫框架
│           │   ├── base.py             # BaseFetcher 抽象类
│           │   └── chaincatcher.py     # 链捕手 HTML scraping
│           ├── material_analyzer.py    # P23 AI 预筛选
│           ├── material_sheet.py       # P23 Sheets 读写
│           ├── creation_store.py       # P27 本地 Markdown 存储
│           ├── google_sheets_source.py # 风格样本/知识库数据源
│           └── sample_service.py       # 样本服务
│   └── data/
│       ├── config/
│       │   └── forbidden_patterns.yaml # P21 禁用词库 (250+)
│       └── prompts/
│           ├── strategist.jinja2       # 策略师模板
│           ├── writer/ (6 个)          # P18 独立模板
│           ├── critic/ (5 个)          # P24 独立模板
│           ├── polisher/ (4 个)        # P24 独立模板
│           └── shared/                 # base_critic / base_polisher
│
├── frontend/src/features/
│   ├── studio/
│   │   ├── components/
│   │   │   ├── HeroInput.tsx           # 输入区 + materialPrefill
│   │   │   ├── WritingCanvas.tsx       # 创作画布 + 新建创作
│   │   │   ├── MaterialCenter.tsx      # P23 素材中心
│   │   │   ├── StrategySelector.tsx    # 策略卡片
│   │   │   ├── TitleSelector.tsx       # 标题选择
│   │   │   ├── editor/
│   │   │   │   ├── RichEditor.tsx      # P19 TipTap 编辑器
│   │   │   │   ├── EditorToolbar.tsx
│   │   │   │   └── EditorBubbleMenu.tsx # AI 浮动菜单
│   │   │   └── sidebar/
│   │   │       ├── UnifiedSidebar.tsx  # 统一右侧面板
│   │   │       ├── VersionTab.tsx      # 版本历史
│   │   │       ├── DiffViewer.tsx      # 版本 Diff 对比
│   │   │       └── ExportTab.tsx       # MD/HTML 导出
│   │   └── schema.ts                  # Zod Schemas
│   └── settings/                      # 设置页面
│       ├── stores/usePromptStore.ts    # P15 提示词管理
│       └── constants/defaultPrompts.ts # 默认提示词
│
├── reports/                            # 项目文档 (6 子目录)
│   ├── 设计文档/    (80 文件, P00-P24)
│   ├── 工作日志/    (24 份交接报告)
│   ├── 测试审计/    (23 份测试报告)
│   ├── 历史归档/    (早期文档)
│   ├── 交接报告/    (阶段交接)
│   └── 评估报告/    (质量评估)
│
├── PROJECT_HANDBOOK.md                 # 本文档
└── PROJECT_STATUS.md                   # 项目状态 (待更新)
```

---

## 📍 当前状态

| 指标 | 值 |
|------|-----|
| **当前阶段** | P31 投研模块 (设计完成，Phase 1 开发中) |
| **前端端口** | `localhost:3000` |
| **后端端口** | `localhost:8000` |
| **Git 分支** | `feature/p10-workflow-refactor` |

### 🤖 模型配置

| 模型 | ID | 适用场景 |
|------|-----|----------|
| **豆包 Seed** | `doubao-seed-1-8-251228` | 通用任务/多模态 |
| **DeepSeek V3.2** | `deepseek-v3-2-251201` | 深度推理/联网搜索 |
| **Surf AI** | `surf-1.5` / `surf-1.5-instant` | 投研分析/热点发现（P31） |
| **Grok** | `grok-3-mini-beta` | 吹捧/Kaito 实时数据（P30） |

### P31 当前待执行

详见: [P31_投研模块设计方案.md](file:///d:/AI_Projects/2026001/reports/设计文档/P31_投研模块设计方案.md)

| 任务 | 状态 |
|------|------|
| Surf API 连通性验证 | ✅ |
| leak.me 热点数据获取 | ✅ |
| 端到端报告生成 (3 项目) | ✅ |
| 分类定级逻辑 + 5 套阶段模板 | 🔜 |
| 扩展到 5 个项目 + 质量优化 | 🔜 |
| HTML 配图自动生成 + 截图 | 🔜 |

---

## 📜 版本进度汇总 (P00 → P24)

| 阶段 | 名称 | 状态 |
|:---:|------|:---:|
| P00-P04 | 前端基建 + Island 架构 + UI/UX 打磨 | ✅ |
| P05 | 全链路测试验证 (E2E + DOM) | ✅ |
| P06 | 爆款能力升级 (标题AB/评分/自适应布局) | ✅ |
| P07 | 企业级数据管线 | ✅ |
| P08 | Lark/Knowledge 集成 + Web3 批量清洗 | ✅ |
| P09 | Strategist 创作流程架构 | ✅ |
| P10 | Google Sheets 迁移 + 工作流重构 | ✅ |
| P11 | API 密钥安全防护 + 模式专属指导 | ✅ |
| P12 | 简化版评分系统 | ✅ |
| P13 | 前后端配置同步 (9/11 方案) | ✅ |
| P14 | 模式模块化架构 + Settings UI 重构 | ✅ |
| P15 | 全智能体提示词编辑器 (可视化 Prompt) | ✅ |
| P16 | Studio UX + Target-Centric 字数控制 | ✅ |
| P17 | 统一配置上下文 | ✅ |
| P18 | 方案B全模块独立架构 (Writer 6模式) | ✅ |
| P19 | TipTap 富文本编辑器 (流式/重写/版本/导出) | ✅ |
| P20 | Context Card 事件脉络感知 | ✅ |
| P21 | Anti-AI Trace 痕迹消除 (250+ 禁用词) | ✅ |
| P22 | 智能模式匹配 (short_article Writer) | ✅ |
| P23 | 每日素材源系统 (爬虫+预筛选+素材中心) | ✅ |
| P24 | 全模式独立管线 (Critic/Polisher 独立化) | ✅ |
| P25 | 20 篇 Benchmark 基准测试 | ✅ |
| P26 | 短篇提示词大优化 (连珠炮式/4层层级/人味化) | ✅ |
| P27 | 创作保存 + 模式重构 (8 模式规划 + P0 清理完成) | ✅ |
| P30 | 吹捧模式提示词 (A/B 测试 + 合规优化 + 定稿) | ✅ |
| **P31** | **投研模块 (Surf API + 4 层架构 + 配图模板)** | 🔄 |

---

## 🎯 后续规划：内容自动化调度中心

### 愿景

仪表盘升级为 **内容自动化调度中心**，定时生产 + 推送至 X：

```
仪表盘 (Dashboard)
    ├─ 定时任务引擎
    │   ├─ 每日 2 条 Alpha 投研快报（P31）
    │   ├─ 每日 1 条短文（锐评/Kaito/吹捧）
    │   └─ 每日 1 条其他内容
    ├─ 内容队列（待审核 → 已审核 → 已发布）
    └─ 发布通道 → 定时推送至 X (Twitter API)
```

### 路线图

| 优先级 | 任务 | 说明 |
|:---:|------|------|
| 🔴 | P31 Phase 1 完成 | 分类定级 + 5 项目 + 配图生成脚本稳定 |
| 🔴 | P27 前端重构 | ConfigPanel 拆分 + DataPanel + 吹捧/Kaito UI |
| 🟠 | 定时任务引擎 | 后端 scheduler (APScheduler/Celery) + 前端仪表盘配置 |
| 🟠 | 投研→内容打通 | 投研数据 JSON → Kaito/锐评选题素材 |
| 🟠 | Kaito Yap 模式 | 项目嘴撸任务内容生成 |
| 🟡 | 锐评改管线 | 从独立 API 迁移到 LangGraph |
| 🟡 | 内容队列系统 | 待审核 → 审批 → 排期发布 |
| 🟡 | X/Twitter API 发布 | 自动/手动推送内容至 X |
| 🟢 | 扩展数据源 | 吴说区块链 + 深潮 TechFlow fetcher |
| 🟢 | 深色模式 | Tailwind 配置就绪，待添加切换 UI |

---

## 🔐 安全规范

### API 密钥保护

| 措施 | 状态 |
|------|:----:|
| `.gitignore` 规则 (env, config, venv) | ✅ |
| Pre-commit Hook (自动检测敏感模式) | ✅ |
| 模板文件 `user_config.example.json` | ✅ |

### 敏感文件 (绝对不能提交到 Git)

- `backend/config/user_config.json` — API 密钥配置
- `.env` / `.env.local` — 环境变量
- `backend/venv/` — Python 虚拟环境
- `config/google_service_account.json` — Google Sheets 凭证

---

## � 快速启动指南

### 1. 启动后端
```bash
cd d:/AI_Projects/2026001/backend
.\venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端
```bash
cd d:/AI_Projects/2026001/frontend
npm run dev
```

### 3. 访问应用
- 创作工坊: http://localhost:3000/studio
- 创作历史: http://localhost:3000/studio?view=history
- 素材中心: http://localhost:3000/studio?view=materials
- 设置: http://localhost:3000/settings
- 健康检查: http://localhost:8000/health

---

## 📡 API 端点参考

### 核心创作流程

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/analyze` | SSE 流式分析，返回策略选项 + Context Card + 推荐模式 |
| `POST` | `/generate` | SSE 流式生成，执行完整 Writer→Critic→Polisher 管线 |
| `POST` | `/hot-take` | 锐评模式独立 API (不走 LangGraph，直接生成 3 条) |

### 素材系统 (P23)

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/materials/fetch` | 爬取 + AI 预筛选 + 写入 Sheets |
| `GET` | `/materials/fetch/{job_id}` | 查询抓取任务状态 |
| `GET` | `/materials/list` | 读取素材列表 (支持筛选+分页) |
| `GET` | `/materials/stats` | 素材统计数据 |
| `POST` | `/materials/mark-used?url=` | 标记素材已使用 |

### 创作保存 (P27)

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/creations/save` | 保存创作为本地 Markdown 文件 |
| `GET` | `/creations/list` | 获取创作历史列表（分页） |
| `GET` | `/creations/{id}` | 获取单篇创作详情 |
| `DELETE` | `/creations/{id}` | 删除创作 |

### AI 重写 (P19)

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/rewrite` | 选中文字 → AI 重写/扩展/简化 |

### 配置管理

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `GET` | `/config/models` | 可用模型列表 |
| `GET/POST` | `/config/keys` | API Key 配置读写 |
| `GET/POST` | `/config/prompts/{agent}` | Agent Prompt 模板读写 |
| `GET` | `/config/styles` | 可用风格列表 |
| `GET/POST` | `/config/features` | Feature Flags 配置 |

---

## 📈 项目里程碑

| 日期 | 版本 | 关键交付 |
|------|------|----------|
| 2026-02-25 | v12.0 | P31 投研模块 POC 验证 + 4 层架构设计 + 配图模板 |
| 2026-02-24 | v11.5 | P30 吹捧模式提示词 A/B 测试 + 合规优化 + 定稿 |
| 2026-02-20 | v11.2 | P27 前端全面审计 + 方案B 确认 + P0 清理完成 |
| 2026-02-19 | v11.0 | P27 创作保存功能 + 8 模式重构规划 |
| 2026-02-18 | v10.5 | P25 Benchmark (20篇) + P26 短篇提示词大优化 |
| 2026-02-10 | v10.0 | P23 素材源系统 Phase 0-3 全交付 |
| 2026-02-09 | v9.5 | P24 A/B/C 完成 (Critic/Polisher独立化) |
| 2026-02-08 | v9.0 | P22 智能模式匹配 + P23 短篇提示词 v1 定稿 |
| 2026-02-06 | v8.5 | P21 Anti-AI 禁用词库 + P20 Context Card |
| 2026-02-04 | v8.0 | P19 TipTap 富文本编辑器全 5 阶段完成 |
| 2026-02-03 | v7.5 | P18 方案B全模块独立架构 |
| 2026-01-31 | v7.2 | P13 前后端配置同步 + P14 规划 |
| 2026-01-29 | v7.1 | P10 Google Sheets 迁移完成 |
| 2026-01-21 | v6.2 | E2E 全链路验证通过 |
| 2026-01-15 | v5.0 | Alpha 技术闭环 |

---

*Last updated: 2026-02-25 23:30*
