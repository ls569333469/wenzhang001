# Quantum Studio v5.0 核心操作流程详解

> **文档密级**: 内部公开
> **版本**: v1.0
> **更新日期**: 2026-01-15
> **适用对象**: 运营团队、内容制作人

本文档详细拆解 Quantum Studio v5.0 从数据清洗到爆文产出的全链路操作流程及核心架构设计。

---

## 0. 系统架构设计 (System Design)
**设计理念**: "Human-in-the-loop" (人在回路) 与 "Agentic Workflow" (代理工作流) 的深度结合。

### 0.1 核心架构图
```mermaid
graph TD
    User((用户/运营)) -->|1. 输入指令| Frontend(Next.js UI)
    Frontend -->|2. SSE 流式请求| Backend(FastAPI)
    
    subgraph "Quantum Engine (LangGraph)"
        Strategist(策略 Agent) -->|3. 生成选题| HumanSelection{人工选题}
        HumanSelection -->|4. 确认角度| Writer(写手 Agent)
        
        subgraph "内容生产闭环"
            Writer -->|5. 初稿| Critic(毒舌 Agent)
            Critic -->|6. 反馈/打回| Writer
            Critic -->|7. 通过| Polisher(润色 Agent)
        end
    end
    
    subgraph "Data Layer (RAG)"
        LarkBase[(飞书多维表格)] <-->|Sync| VectorDB(本地向量/索引)
        Cleaner(清洗 CLI) -->|ETL| LarkBase
    end
    
    Writer <..>|Few-Shot 检索| LarkBase
    Polisher -->|8. 最终交付| Frontend
```

### 0.2 技术栈 (Tech Stack)
*   **前端**: Next.js 14 + TailwindCSS + Shadcn/UI (极简主义设计)
*   **后端**: FastAPI + Uvicorn (异步高并发)
*   **AI 编排**: LangGraph (有向无环图状态机) + Asyncio
*   **数据流**: Server-Sent Events (SSE) 实现打字机效果
*   **LLM 适配**: 支持 OpenAI / Claude / DeepSeek / Doubao 多模型热切换

---

## 1. 数据清洗 (Data Cleaning)
**目标**: 将原始无序的“素材”转化为 AI 可理解、可模仿的高质量“样本”(Few-Shot Samples)。

### 1.1 核心机制: 壳肉分离法 (Shell-Kernel)
我们不仅仅是存文本，而是将文章拆解为：
*   **Shell (壳)**: 语气、排版、Emoji 使用习惯、情绪渲染手法。
*   **Kernel (核)**: 核心观点、逻辑推导公式。

### 1.2 操作步骤
1.  **准备素材**: 将 txt/md 文件放入 `backend/data/raw/{style_name}` 目录。
2.  **执行清洗**: 使用 CLI 工具进行智能化处理。
    ```bash
    # 进入后端目录
    cd backend
    
    # 运行清洗工具 (以咪蒙风格为例)
    python -m tools.cleaner_cli clean \
      --folder data/raw/mimeng \
      --author "咪蒙" \
      --style "mimeng" \
      --source-category "Official Account"
    ```
3.  **自动入库**: 工具会自动打分 (`quality_score`) 并上传至 Lark Base。只有分数 > 7 的素材会被 Writer 检索。

---

## 2. 知识库调用 (Lark Retrieval)
**目标**: 让 AI 在写作时“像”特定的博主，实现千人千面。

### 2.1 动态检索逻辑 (RAG)
Writer Agent 在生成内容前，不会凭空捏造风格，而是执行以下检索：
1.  **锁定坐标**: 获取当前任务的 `mode` (如 `mimeng`) 和 `emotion` (如 `anxiety`).
2.  **Lark 查询**: 调用 `sync_service` 搜索 Lark Base。
    *   *Filter*: `style == mode` AND `quality_score >= 8`
    *   *Sort*: 优先匹配 `emotion`，其次按 `quality_score` 降序。
    *   *Limit*: Top 3 Records.
3.  **Prompt 注入**: 将这 3 篇样本的 `content` 和 `logic_pattern` 注入到 System Prompt 的 "Few-Shot Context" 区域。

---

## 3. 智能选题 (Strategist Agent)
**目标**: 解决“写什么”的问题，从源头确保内容的吸引力。

### 3.1 分析流程
1.  **输入**: 用户在前端输入 "Core Instruction" (如：Web3 游戏现状) 并可选附带 URL 参考资料。
2.  **信息锚点提取**: LLM 分析输入，提取 `info_anchors`：
    *   *Must Mention*: 必提实体 (e.g., "StepN", "Axie Infinity")
    *   *Key Data*: 关键数据 (e.g., "DAU 下跌 90%")
3.  **策略生成**: 生成 3-4 个切入角度 (Strategy Options)，每个包含：
    *   **Hook**: 开篇第一句话（黄金 3 秒）。
    *   **Pain Point**: 直击用户痛点。
    *   **Outline**: 文章大纲。

---

## 4. 爆文编写 (Writer Agent)
**目标**: 执行具体的写作任务，平衡逻辑与情绪。

### 4.1 写作逻辑
1.  **加载模板**: 根据 `mode` 加载对应的 System Prompt 模板 (定义了语气、禁忌词)。
2.  **融合样本**: 结合 Lark 检索到的 3 篇范文进行“临摹”。
3.  **流式生成**: 采用 Async Iterator 逐字输出。如果在生成过程中 LLM 判定需要更正，会自动触发 Self-Correction。

> **关键技术点**: v5.0 已修复 "Async Timeout" 问题，支持 2000+ 字长文的稳定生成，Writer 运行在独立的线程池中，不阻塞主线程。

---

## 5. 润色与质检 (Critic & Polisher)
**目标**: 模拟人类编辑部的审核流程。

### 5.1 毒舌主编 (Critic)
*   **角色**: 极其挑剔的审核员。
*   **检查项**:
    *   *情绪浓度*: 是否太干瘪？
    *   *逻辑漏洞*: 有没有前后矛盾？
    *   *幻觉检测*: 有没有编造数据？
*   **输出**: 这里的 Feedback 会直接打回给 Writer 进行 "Rewrite" (最多 2 轮)。

### 5.2 最终润色 (Polisher)
*   **角色**: 排版编辑。
*   **职责**:
    *   添加 Markdown 格式 (H1/H2/Bold)。
    *   智能插入 Emoji 😃。
    *   生成 Social Media 摘要 (Tweet Thread)。

---

## 6. 全流程操作 SOP (Summary)
**场景**: 你想写一篇通过 "DeepSeek 崛起" 讽刺 "OpenAI 停滞" 的文章。

1.  **准备 (Lark)**: 确认 Lark 库中有 "科技得瑟" 或 "商业评论" 风格的优质样本。如果没有，先用 `cleaner_cli` 洗几篇。
2.  **输入 (Frontend)**:
    *   *Mode*: 选择 "banfo" (半佛仙人体)。
    *   *Instruction*: "DeepSeek V3 发布，性能对标 GPT-4 但成本只有 1/10。OpenAI 这一年都在画饼。无论技术多强，不降价就是耍流氓。"
3.  **选题 (Strategist)**: 点击 "Analyze"。系统提供 3 个角度，选择 "商业降维打击" 这个角度。
4.  **生成 (Writer)**: 点击 "Generate"。观察 Logs，确认 Writer 成功调用了 Lark 样本。
5.  **优化 (Critic)**: 如果第一版太温和，Critic 会要求 "加强讽刺力度"，Writer 会自动重写。
6.  **出稿**: 获取最终 Markdown 内容，复制到发布平台。
