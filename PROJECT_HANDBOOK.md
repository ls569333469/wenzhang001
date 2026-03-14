# Quantum Studio v13.0 - 项目手册

> **更新日期**: 2026-03-11  
> **版本**: v13.0 (P36 投研管线修复 + 催化剂评分系统)  
> **维护者**: AI 开发团队

---

##  项目概述

**Quantum Studio** 是一个基于多 Agent 协作的 **Web3 内容生成引擎**，包含两大核心模块：

| 模块 | 功能 | 管线 |
|------|------|------|
| **创作工坊** | 爆款 Web3 文章生成 | Strategist → Writer → Critic → Polisher |
| **投研快报** | 自动化项目调研 + 推文生成 | Scout → Strategist → Enrichment → Reviewer → Tweet → Card |

### 技术栈

| 层 | 技术 |
|---|------|
| **前端** | Next.js 16 + Tailwind CSS + Shadcn/UI + TipTap 富文本编辑器 |
| **后端 API** | FastAPI (Python 3.13) + Uvicorn |
| **Agent 编排** | LangGraph (有状态工作流) |
| **LLM 模型** | 火山引擎 (豆包/DeepSeek) + Google Gemini |
| **投研搜索** | Surf AI API (surf-1.5) + leak.me KOL Tracker |
| **实时数据** | Grok API (X/Twitter 实时搜索) |
| **数据存储** | Google Sheets + ChromaDB (本地) + 本地文件系统 |
| **配图截图** | Playwright (无头浏览器, subprocess 隔离) |

---

## 🩸🥩 核心理念：血与肉

> ⚠️ **创作工坊的灵魂，必须牢记！**

| | 定义 | 来源 | 作用 |
|:---:|------|------|------|
| **🩸 血** | Web2 博主风格素材 | 咪蒙/半佛/新世相/视觉志... | 提供 **写作技巧和爆款风格** |
| **🥩 肉** | Web3 媒体专业知识 | ChainCatcher/Lark 知识库 | 提供 **行业内容和专业度** |

**最终产出** = 用 Web2 爆款技巧包装 Web3 专业内容

---

## 🏗️ 系统架构

### 一、创作工坊管线 (4 级 Agent)

```
用户输入素材
    ↓
┌─ Strategist ────────────────────────────────┐
│  • RAG 检索 (Google Sheets 知识库)            │
│  • 生成 Context Card (事件脉络感知)            │
│  • 推荐创作模式 (智能模式匹配)                 │
└─────────────────────────────────────────────┘
    ↓
┌─ Writer ────────────────────────────────────┐
│  • 8 种独立 Writer (per-mode .py + .jinja2)  │
│  • Anti-AI 禁用词约束 (250+ 词)              │
│  • 生成 3 个变体版本供选择                    │
└─────────────────────────────────────────────┘
    ↓
┌─ Critic ────────────────────────────────────┐
│  • 5 维度评分 + AI 痕迹检测                   │
│  • score < 阈值 → 自动触发重写                │
└─────────────────────────────────────────────┘
    ↓
┌─ Polisher ──────────────────────────────────┐
│  • 最终检查清单 (节奏、禁用词、格式)           │
└─────────────────────────────────────────────┘
    ↓
最终文章输出 (TipTap 富文本编辑器)
```

### 二、投研快报管线 (P31-P36, 10 步流水线)

> **P35 重构后的模块化管线**，支持自动模式和重组模式。

```
┌─────────────────────────────────────────────────────────────┐
│                    两种运行模式                               │
│  🔄 自动模式: Scout 搜索 → 全流程自动                         │
│  � 重组模式: 用户选择项目 → 从磁盘加载策略官报告 → 后半段重组   │
└─────────────────────────────────────────────────────────────┘

Step 1  🔭 侦察官 (Scout)
        │  Surf API 搜索 @leakmealpha (leak.me)
        │  输出: 项目表格 (名称/Twitter/赛道/KOL数/催化剂)
        │  代码: backend/app/agents/research/scout.py
        ↓
Step 2  ☑️ 用户选择项目 (前端勾选 + 项目库混合)
        │  支持跨日期选择: 今日发现 + 历史项目库
        │  代码: frontend/src/features/studio/components/data/ResearchPanel.tsx
        ↓
Step 3  � 策略官 (Strategist)
        │  逐项调用 Surf API 深度调研
        │  输出: 项目报告 .md (定位/团队/融资/催化剂/风险)
        │  存储: reports/research/projects/{handle}_{date}.md
        │  代码: backend/app/services/daily_report_service.py → run_strategist()
        ↓
Step 4  ✅ 6551 验证 (Twitter Handle 校验)
        │  调用 6551 API 验证 Twitter 账号真实性
        │  代码: backend/app/services/daily_report_service.py → _verify_6551()
        ↓
Step 5  📋 数据回填 (Enrichment)
        │  从策略官报告提取: summary (项目定位) + catalyst (催化剂)
        │  P36: 催化剂只保留策略官「卡片催化剂」行，不再做代码评分和三级 fallback
        │  P36: 模糊子串匹配 (Anchorage ↔ Anchorage Digital)
        │  代码: backend/app/services/daily_report_service.py → _enrich_projects()
        ↓
Step 6  📋 审核官 (Summarizer/Reviewer)
        │  LLM 总结归纳所有项目报告
        │  代码: backend/app/services/daily_report_service.py → _run_reviewer()
        ↓
Step 7  🐦 推文写手 (Tweet Writer)
        │  聚合项目生成 Alpha 速报推文 (主推文 + 各项目推文)
        │  P36: 自动注入 @handle 到推文文本
        │  P36: 清理 LLM 杂质 (### 项目N / 注释 / 分隔线)
        │  存储: reports/research/tweets_{date}.md + .json (双保存)
        │  代码: backend/app/services/daily_report_service.py → _run_tweet_writer()
        ↓
Step 8  📸 配图生成 (Card Generator)
        │  生成 1200×675 HTML 配图 (瑞士金融报纸风)
        │  Playwright 无头浏览器截图为 PNG (subprocess 隔离)
        │  P36: _clip(summary, 60) 安全截断, 移除空格分词
        │  存储: reports/research/card_{date}.html + .png
        │  代码: backend/app/services/card_generator.py
        ↓
Step 9  🔍 质检官 (Post-Card Reviewer)
        │  P36: 移到配图后执行 (检查最终数据质量)
        │  检查: 催化剂≤20字, 定位≤30字, 翻译, 截断修复
        │  代码: backend/data/prompts/research/reviewer.jinja2
        ↓
Step 10 📡 API 返回前端展示
```

### 催化剂评分系统 (P36)

> 用于侦察官阶段筛选高价值催化事件，决定前端显示红色🔥标签还是灰色文字。

| 分数 | 类型 | 关键词示例 | 显示 |
|:---:|------|----------|------|
| **+10** | 直接参与机会 | TGE, 空投, airdrop, 代币上线, 主网上线, 白名单, 测试网, 上币, 上所, 预售, launchpad | 🔥 红色标签 |
| **+5** | 生态进展 | Galxe, Zealy, quest, 产品发布, 功能上线, Season, 质押, staking, mint, 公测, 黑客松 | 🔥 红色标签 |
| **+4** | 一般事件 | 积分系统, Campaign, Points, 代币解锁, DAO治理, 排行榜, 路线图 | 🔥 红色标签 |
| **0** | 普通信息 | 融资, 投资, 领投 | 灰色文字 |
| **-1** | 噪声 | KOL提及, 浏览量, 审计 | 不显示 |

代码位置: `backend/app/services/card_generator.py → _catalyst_importance()`

---

## 📂 目录结构

```
├── backend/
│   └── app/
│       ├── main.py                     # API 入口
│       ├── graph.py                    # LangGraph 工作流编排
│       ├── agents/
│       │   ├── strategist.py           # 策略师 (创作工坊)
│       │   ├── writer/                 # 8 模式独立 Writer
│       │   ├── critic/                 # 5 模式独立 Critic
│       │   ├── polisher/               # 4 模式独立 Polisher
│       │   └── research/
│       │       └── scout.py            # P31 侦察官 (Surf API + 表格解析)
│       ├── api/
│       │   ├── research.py             # P31 投研 API (/scout, /reassemble, /latest)
│       │   ├── materials.py            # P23 素材 CRUD
│       │   ├── creations.py            # P27 创作保存 CRUD
│       │   └── rewrite.py              # P19 AI 局部重写
│       ├── core/
│       │   ├── prompts.py              # 模板渲染 + 词库注入
│       │   └── forbidden_patterns.py   # P21 禁用词加载器
│       └── services/
│           ├── daily_report_service.py # ⭐ 投研管线核心 (1350+ 行)
│           ├── card_generator.py       # P31 HTML 配图 + 催化评分
│           ├── surf_service.py         # Surf AI API 封装
│           ├── data_service.py         # Google Sheets 读写
│           ├── creation_store.py       # 本地 Markdown 存储
│           └── material_fetcher/       # P23 爬虫框架
│   └── data/
│       ├── config/
│       │   ├── forbidden_patterns.yaml # P21 禁用词库
│       │   └── google_service_account.json # Sheets 凭证 (不提交 Git)
│       └── prompts/
│           ├── strategist.jinja2       # 策略师模板
│           ├── writer/ (6 个)          # Writer 模板
│           ├── critic/ (5 个)          # Critic 模板
│           ├── polisher/ (4 个)        # Polisher 模板
│           └── research/
│               ├── scout.jinja2        # 侦察官提示词
│               ├── tweet_digest.jinja2 # 推文写手提示词
│               └── reviewer.jinja2     # 质检官提示词 (P36 更新)
│
├── frontend/src/features/
│   ├── studio/
│   │   └── components/
│   │       ├── data/
│   │       │   └── ResearchPanel.tsx   # ⭐ 投研左侧面板 (侦察官+项目库)
│   │       ├── pipeline/
│   │       │   └── ProgressTab.tsx     # 管线进度展示
│   │       ├── HeroInput.tsx           # 输入区
│   │       ├── WritingCanvas.tsx       # 创作画布
│   │       └── editor/                 # TipTap 编辑器组件
│   └── research/
│       └── TweetCards.tsx              # 推文展示 + 复制
│
├── reports/
│   ├── research/                       # 投研产出 (自动生成)
│   │   ├── projects/                   # 策略官报告 ({handle}_{date}.md)
│   │   ├── tweets_{date}.md            # 推文 Markdown
│   │   ├── tweets_{date}.json          # 推文 JSON (P36 保留 twitter handle)
│   │   ├── card_{date}.html            # 配图 HTML
│   │   └── card_{date}.png             # 配图截图
│   ├── 设计文档/                        # P00-P36 设计方案
│   └── 工作日志/                        # 交接报告
│
├── PROJECT_HANDBOOK.md                 # 本文档
└── PROJECT_STATUS.md                   # 项目状态
```

---

## 📍 当前状态

| 指标 | 值 |
|------|-----|
| **当前阶段** | P36 投研管线修复 (已完成) |
| **前端端口** | `localhost:3000` |
| **后端端口** | `localhost:8000` |
| **投研报告总数** | 123 个 (跨 9 个日期, 2026-02-27 ~ 2026-03-10) |
| **Surf API** | ⚠️ 余额不足, 待充值 |

### 🤖 模型配置

| 模型 | ID | 适用场景 |
|------|-----|----------|
| **豆包 Seed** | `doubao-seed-1-8-251228` | 通用任务/多模态 |
| **DeepSeek V3.2** | `deepseek-v3-2-251201` | 深度推理/联网搜索 |
| **Surf AI** | `surf-1.5` | 投研深度调研 (策略官) |
| **Surf AI (instant)** | `surf-1.5-instant` | 侦察官快速搜索 |
| **Grok** | `grok-3-mini-beta` | 吹捧/Kaito 实时数据 |

### 环境变量 (.env)

| 变量 | 用途 |
|------|------|
| `SURF_API_KEY` | Surf AI 调研搜索 |
| `ANTHROPIC_API_KEY` | Anthropic Claude (备用) |
| `TWITTER_TOKEN` | 6551 API Twitter 验证 |
| `BINANCE_SQUARE_API_KEY` | 币安广场 API |

---

## � API 端点参考

### 投研模块 (P31-P36)

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/research/scout` | 侦察官搜索 (调用 Surf API, 返回项目列表) |
| `POST` | `/api/research/reassemble` | 重组模式 (选中项目, 执行后半段管线) |
| `GET` | `/api/research/latest` | 获取最新推文 (优先 JSON, 回退 Markdown) |
| `GET` | `/api/research/card-image/{date}` | 获取配图 (Base64 PNG) |
| `GET` | `/api/data/research` | 获取 Google Sheets 投研记录 |

### 创作工坊

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/analyze` | SSE 流式分析, 策略选项 + Context Card |
| `POST` | `/generate` | SSE 流式生成, Writer → Critic → Polisher |
| `POST` | `/hot-take` | 锐评模式独立 API |

### 素材 + 创作 + 配置

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/materials/fetch` | 爬取 + AI 预筛选 + 写入 Sheets |
| `GET` | `/materials/list` | 素材列表 (筛选+分页) |
| `POST/GET` | `/creations/save` `/list` `/id` | 创作保存 CRUD |
| `POST` | `/api/rewrite` | AI 局部重写 |
| `GET` | `/health` | 健康检查 |

---

## 📜 版本进度汇总

| 阶段 | 名称 | 状态 |
|:---:|------|:---:|
| P00-P04 | 前端基建 + Island 架构 + UI/UX | ✅ |
| P05-P09 | E2E 测试 + 爆款能力 + 数据管线 + Strategist | ✅ |
| P10-P14 | Sheets 迁移 + 安全防护 + 模块化架构 | ✅ |
| P15-P18 | Prompt 编辑器 + Studio UX + 独立 Writer | ✅ |
| P19-P22 | TipTap 编辑器 + Context Card + Anti-AI + 模式匹配 | ✅ |
| P23-P27 | 素材源系统 + 独立管线 + Benchmark + 创作保存 | ✅ |
| P30 | 吹捧模式提示词定稿 | ✅ |
| **P31** | **投研模块 POC (Surf API + 4 层架构 + 配图)** | ✅ |
| **P32** | **前端投研面板 (ResearchPanel + 项目库 + 进度条)** | ✅ |
| **P34** | **6551 同步 + 币安广场 + 推文优化** | ✅ |
| **P35** | **核心重组重构 (10 步管线 + 重组模式 + JSON 保存)** | ✅ |
| **P36** | **投研管线修复 (催化剂简化 + 评分系统 + 跨日期)** | ✅ |

### P36 修复清单 (2026-03-11 完成)

| 修复项 | 说明 |
|--------|------|
| 催化剂流程简化 | 移除代码评分/三级 fallback/7天检查, 仅保留策略官 prompt |
| 质检官后移 | 从 enrichment 后移到配图后 (终检) |
| tweets JSON 双保存 | 保留 twitter handle 等结构化字段 |
| 跨日期重组 | 支持混选不同日期的项目, 自动去重取最新 |
| 推文清理 | 正则清除 `### 项目N` / `（注：...）` / `---` |
| 配图截断修复 | 移除空格断词, summary 限制 40→60 字 |
| 推文 @handle 注入 | 自动插入 @handle 到推文文本 (可复制) |
| 侦察官红标签 | 前端 catalyst 字段映射 + localStorage 兼容 |
| 催化剂评分过滤 | `_catalyst_importance()` 扩充至 55+ 关键词 |

---

## 🚀 快速启动

### 1. 启动后端
```bash
cd d:/AI_Projects/2026001/backend
.\venv\Scripts\activate       # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端
```bash
cd d:/AI_Projects/2026001/frontend
npm run dev
```

### 3. 访问
| 页面 | URL |
|------|-----|
| 创作工坊 | http://localhost:3000/studio |
| 投研面板 | http://localhost:3000/studio (左侧 ResearchPanel) |
| 素材中心 | http://localhost:3000/studio?view=materials |
| 设置 | http://localhost:3000/settings |
| 健康检查 | http://localhost:8000/health |

---

## � 安全规范

### 敏感文件 (绝对不能提交到 Git)

- `backend/config/user_config.json` — API 密钥配置
- `.env` / `.env.local` — 环境变量
- `backend/venv/` — Python 虚拟环境
- `config/google_service_account.json` — Google Sheets 凭证

### Pre-commit 安全扫描

提交前执行: `python scripts/pre_commit_scan.py`  
自动检测: API key 泄露、硬编码密钥、敏感文件

---

## 🎯 后续规划

| 优先级 | 任务 | 说明 |
|:---:|------|------|
| 🔴 | Surf API 充值 | 侦察官搜索恢复, 当前 INSUFFICIENT_CREDIT |
| 🔴 | 完整自动模式验证 | Scout → 全流程端到端测试 |
| 🟠 | 催化剂 LLM 标注 | Scout prompt 加"催化优先级"列, 替代纯关键词 |
| 🟠 | 知识库集成 | ChromaDB 存储历史报告, RAG 增强 |
| 🟠 | Kaito Yap 模式 | 项目嘴撸任务内容生成 |
| 🟡 | 定时任务引擎 | APScheduler 每日自动出报 |
| 🟡 | X/Twitter API 发布 | 自动推送推文至 X |
| 🟢 | 广场模式短帖 | 币安广场短文自动化 |

---

## 📈 项目里程碑

| 日期 | 版本 | 关键交付 |
|------|------|----------|
| **2026-03-11** | **v13.0** | **P36 投研管线修复: 催化剂简化/评分系统/跨日期重组/推文清理** |
| 2026-03-10 | v12.8 | P35 核心重组重构: 10 步管线/重组模式/JSON 保存 |
| 2026-03-09 | v12.5 | P35 Phase 1: 模块化管线/重组 500 修复/DeepSeek 默认 |
| 2026-03-08 | v12.3 | P34 6551 同步/币安广场/推文优化/动态卡片布局 |
| 2026-03-07 | v12.1 | P32 前端投研面板/项目库/进度条 |
| 2026-02-25 | v12.0 | P31 投研模块 POC + 4 层架构设计 |
| 2026-02-24 | v11.5 | P30 吹捧模式提示词定稿 |
| 2026-02-20 | v11.2 | P27 创作保存 + 8 模式重构规划 |
| 2026-02-10 | v10.0 | P23 素材源系统全交付 |
| 2026-02-04 | v8.0 | P19 TipTap 编辑器完成 |
| 2026-01-15 | v5.0 | Alpha 技术闭环 |

---

*Last updated: 2026-03-11 22:11*
