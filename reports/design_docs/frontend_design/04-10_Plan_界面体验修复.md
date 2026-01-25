# Phase 6: 界面体验修复实施计划 (Pragmatic Fix)

## 目标 (Goal)
仅针对用户反馈的三个核心痛点（输入体验差、知识库繁琐、提示词不可改）进行务实的 UI 修正，不涉及后端架构变更。同时适配后端已有的“角度选择”业务流。

## 用户审查点 (User Review Required)
- **Hero Input 位置**: 确认将输入框从左下角移动到屏幕中央 (WritingCanvas 区域)。
- **智能知识库**: confirm "自动匹配" (Auto) 将作为默认选项，传给后端的 ID 为 `null` 或特殊标记。
- **Settings MVP**: 确认仅使用 LocalStorage 存储自定义 Prompt，并通过 **Input Prefix** 方式注入（因为后端 `APIConfig` 不支持传 prompt）。
- **业务流**: 确认前端将改为“两段式”调用：先 `/analyze` 获取选项，用户选择后，再 `/generate` 生成全文。

## 变更提案 (Proposed Changes)

### 1. 重构输入区 (Hero Input)
**目标**: 将输入框搬到屏幕中间，提供沉浸式写作体验。

- **`src/features/studio/components/HeroInput.tsx` [NEW]**:
    - 创建一个新的居中输入组件。
    - 样式：`max-w-2xl`, 居中阴影卡片, 高度自适应 Textarea。
    - 逻辑：包含 `StartButton` 的逻辑。
- **`src/features/studio/components/WritingCanvas.tsx` [MODIFY]**:
    - 引入 `HeroInput`。
    - 逻辑：当 `content` 为空时显示 `HeroInput`。
- **`src/features/studio/components/ConfigPanel.tsx` [MODIFY]**:
    - **移除**底部的 `Textarea` 和 `StartButton`。

### 2. 知识库默认逻辑 (Auto Knowledge)
**目标**: 降低配置负担，默认由 AI 决定。

- **`src/config/constants.ts` [MODIFY]**:
    - 添加 `{ id: 'auto', name: '✨ 智能匹配 (Auto)' }`。
- **`src/features/studio/components/ConfigPanel.tsx` [MODIFY]**:
    - 默认选中 `['auto']`。
    - 交互逻辑：`auto` 互斥。

### 3. Settings MVP & Prompt Injection
**目标**: 允许用户自定义 Agent 人设，且不改后端代码。

- **`src/app/(main)/settings/page.tsx` [MODIFY]**:
    - 新增三个 Prompt 文本框 (Strategy/Writer/Critic)。
    - **默认值**: 从 `src/config/constants.ts` (预埋后端默认 Prompt) 加载，方便用户在此基础上修改。
    - 保存到 `localStorage`。
- **`src/features/agent/stores/useAgentStore.ts` (Injection) [MODIFY]**:
    - 在 `startSession` 中读取 `localStorage`。
    - **注入策略**: 由于后端 `GenerateRequest.agent_config` 不支持传递 Prompt，我们将采用 **Payload Prefix** 方式：
      ```text
      [SYSTEM OVERRIDE]
      Strategist: {local_strategist_prompt}
      Writer: {local_writer_prompt}
      
      [USER INPUT]
      {original_input}
      ```
      *(注意：这依赖后端 LLM 遵循 Prompt 中的指令，虽不如 System Prompt 强力，但在不改后端前提下是唯一解)*

### 4. 业务流适配 (Workflow Adaptation)
**目标**: 适配后端 `/analyze` -> `Select` -> `/generate` 流程。

- **`src/features/agent/stores/useAgentStore.ts` [MODIFY]**:
    - 拆分 `startSession` 为 `analyzeRequest` 和 `generateRequest`。
    - 新增状态 `strategyOptions` 存储后端返回的选项。
    - 新增状态 `isWaitingForSelection`。
- **`src/features/studio/components/StrategySelector.tsx` [NEW]**:
    - 在 `WritingCanvas` 中显示。
    - 当 `isWaitingForSelection` 为 true 时渲染卡片列表。
    - 用户点击卡片 -> 调用 `confirmSelection(option)` -> 触发 `/generate`。

## 验证计划 (Verification Plan)

### 1. 功能模块测试 (Functional Testing)
- **Hero Input 交互**:
    - [ ] 验证页面加载时 Input 居中显示。
    - [ ] 验证输入多行文本时高度自适应。
    - [ ] 验证点击 "Start" 或按 `Cmd+Enter` 正确触发生效状态 (Loading)。
- **智能知识库 (Auto Knowledge)**:
    - [ ] 验证 ConfigPanel 默认选中 "✨ 智能匹配"。
    - [ ] 验证选中 "Auto" 时，其他选项互斥 (自动取消)。
    - [ ] 验证取消 "Auto" 时，可多选其他知识库。
- **配置持久化 (Settings Persistence)**:
    - [ ] 在 `/settings` 页面修改 3 个 Prompt 并保存。
    - [ ] 刷新页面，验证修改内容依然存在 (LocalStorage)。
    - [ ] 清除浏览器缓存，验证恢复默认值 (从 constants.ts 加载)。

### 2. 业务流集成测试 (Workflow Integration)
- **Prompt 注入验证**:
    - [ ] 修改 Writer Prompt 为明显的测试指令 (e.g. "以海盗口吻写作")。
    - [ ] 发起请求，观察 Network Tab 的 `/analyze` 或 `/generate` Payload。
    - [ ] 确认 `input` 字段前是否正确拼接了 `[SYSTEM OVERRIDE] ...` 内容。
- **两段式状态流转**:
    - [ ] **Step 1**: 输入 -> 提交。
    - [ ] **Expect**: Timeline 显示 "Strategist Analyze"，随后 WritingCanvas 出现 "StrategySelector" 卡片组。
    - [ ] **Step 2**: 选中任意卡片 -> 确认。
    - [ ] **Expect**: Timeline 进入 "Writer Drafting" -> "Critic Reviewing" -> "Polishing"。

### 3. 全链路模拟测试 (E2E Simulation)
*模拟真实用户操作，跑通完整闭环。*

**场景**: 创作一篇关于 "Web3 模块化区块链" 的深度分析文章。

1.  **准备**:
    - 后端服务运行中 (`python -m app.main`)。
    - 前端服务运行中 (`npm run dev`)。
2.  **执行**:
    - 打开首页，在 Hero Input 输入 "模块化区块链的现状与未来"。
    - 侧边栏保持 "智能匹配" 和 "深度分析" 模式。
    - 点击开始。
3.  **监控**:
    - **前端**: 观察 Timeline 动画流畅度，无卡顿或报错。
    - **后端**: 观察控制台日志，确认 `node_strategist`, `node_writer` 等节点依次执行。
    - **生成**: 确认最终输出 Markdown 文章，包含标题、正文、且格式正常。
4.  **结果验收**:
    - 文章字数是否符合 "Medium" 设置 (~1500字)。
    - 是否包含了 "行业黑话" (由 Polisher 注入)。
    - (若修改了 Prompt) 是否体现了自定义的人设风格。
