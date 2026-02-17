# Quantum Studio v10.0 - 项目手册

> **更新日期**: 2026-02-13  
> **版本**: v10.0 (P24 全模式独立管线)  
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
| **LLM 模型** | 火山引擎 (豆包 Seed / DeepSeek V3.2) |
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
│  • 6 种独立 Writer (per-mode .py + .jinja2)  │
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

### 6 种创作模式

| 模式 | 字数 | Critic | Polisher | 阈值 | 最多重写 | 定位 |
|------|:---:|:---:|:---:|:---:|:---:|------|
| `hot_take` 锐评 | 50-150 | ⏭️ 跳过 | ⏭️ 跳过 | — | — | Twitter 一句话快评 |
| `short_article` 短篇 | 50-300 | ✅ | ⏭️ 跳过 | 85 | 1 | 每日快评/碎句节奏 |
| `mid_article` 中篇 | 150-800 | ✅ | ✅ | 85 | 2 | 深度 Thread |
| `long_article` 长篇 | 900-1800 | ✅ | ✅ | 90 | 3 | 专题研究报告 |
| `tutorial` 教程 | 400-1500 | ✅ | ✅ | 85 | 2 | 技术教程/指南 |
| `rewrite` 改写 | 按原文 | ✅ | ✅ | 85 | 1 | 内容改写/调性转换 |

### 核心特性

| 特性 | 阶段 | 说明 |
|------|:---:|------|
| TipTap 富文本编辑器 | P19 | 流式输出、AI 局部重写、版本历史+Diff对比、统一侧边栏 |
| Context Card 事件脉络 | P20 | Strategist 自动生成 summary/time_context/forward_look |
| Anti-AI Trace 痕迹消除 | P21 | 250+ 禁用词库 (YAML) 自动注入所有 Agent |
| 智能模式匹配 | P22 | Strategist 分析素材后自动推荐 short/mid/long |
| 每日素材源系统 | P23 | ChainCatcher 爬虫 → AI 预筛选 → Sheets 存储 → 前端素材中心 |
| 全模式独立管线 | P24 | Critic/Polisher per-mode 独立模板 + 模型配置 |

---

## 📂 目录结构

```
├── backend/
│   └── app/
│       ├── main.py                     # API 入口
│       ├── graph.py                    # LangGraph 工作流编排
│       ├── agents/
│       │   ├── strategist.py           # 策略师 (mode 变量注入)
│       │   ├── writer/                 # ✅ 6 模式独立 Writer
│       │   │   ├── hot_take.py
│       │   │   ├── short_article.py
│       │   │   ├── mid_article.py
│       │   │   ├── long_article.py
│       │   │   ├── tutorial.py
│       │   │   └── rewrite.py
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

## � 当前状态

| 指标 | 值 |
|------|-----|
| **当前阶段** | P24-D (一致性补全) — 前端工作 |
| **前端端口** | `localhost:3000` |
| **后端端口** | `localhost:8000` |
| **Git 分支** | `feature/p10-workflow-refactor` (main 待合并) |

### 🤖 模型配置

> **详细文档**: [docs/volcengine_models.md](file:///d:/AI_Projects/2026001/docs/volcengine_models.md)

| 模型 | ID | 适用场景 |
|------|-----|----------|
| **豆包 Seed** | `doubao-seed-1-8-251228` | 通用任务/多模态 |
| **DeepSeek V3.2** | `deepseek-v3-2-251201` | 深度推理/联网搜索 |

### P24-D 待完成事项

> 后端 0 改动，纯前端工作 (~12 文件)

- Schema: 新增 `ModeStrategistConfigSchema` / `SKIP_MODES`
- Store: 策略师/评论家/润色师 per-mode store (v2 迁移)
- UI: Settings 页 4 智能体 × 6 模式统一卡片
- P15: Strategist/Critic/Polisher 提示词编辑器加 6 模式 sub-tabs
- API: `useAgentStore.ts` 覆盖 4 agent per-mode 配置下发

详见: [P24_全模式独立管线.md](file:///d:/AI_Projects/2026001/reports/设计文档/P24_全模式独立管线.md)

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
| **P24** | **全模式独立管线 (A/B/C done, D 待完成)** | 🔄 |

---

## 🎯 后续规划

| 优先级 | 任务 | 说明 |
|:---:|------|------|
| 🔴 | P24-D 一致性补全 | 4智能体×6模式前端统一 |
| � | Git 整理 | 提交未提交变更 + 合并 feature 到 main |
| 🟡 | 短篇提示词定稿 | 开头/结尾组合写入正式模板 (P23) |
| 🟡 | 提示词质量迭代 | 基于评估报告优化（融合密度链+结构化钩子） |
| 🟢 | 扩展数据源 | 吴说区块链 + 深潮 TechFlow fetcher |
| 🟢 | 定时抓取 | 素材源 cron 自动化 |
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

*Last updated: 2026-02-13 13:30*
