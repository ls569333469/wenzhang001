# Phase 6: 界面体验修复任务清单 (Pragmatic Fix)

**状态**: 🔴 进行中
**目标**: 修复高优先级的体验痛点，适配后端现有业务流，实现“不改后端代码”的体验升级。
**执行计划**: [6-1_Plan_Pragmatic_Fix.md](./6-1_Plan_Pragmatic_Fix.md)

---

## 📅 核心任务 (Core Tasks)

### 1. 交互体验重构 (Input Experience)
- [ ] **Hero Input 组件开发**
  - [ ] 创建 `src/features/studio/components/HeroInput.tsx` (居中/自适应/阴影)。
  - [ ] 实现 `StartButton` 逻辑迁移 (调用 `startSession`)。
- [ ] **Writing Canvas 集成**
  - [ ] 修改 `WritingCanvas.tsx`: 当 `content` 为空时显示 Hero Input。
  - [ ] 确保动画过渡 (Fade/Zoom) 流畅。
- [ ] **Config Panel 清理**
  - [ ] 移除底部的 Textarea 和 Start 按钮。

### 2. 知识库优化 (Knowledge Base)
- [ ] **常量定义**
  - [ ] `src/config/constants.ts`: 添加 `{ id: 'auto', name: '✨ 智能匹配 (Auto)' }`。
- [ ] **Config Panel 逻辑**
  - [ ] 默认选中 `['auto']`。
  - [ ] 实现互斥逻辑 (选 Auto 清空其他，选其他清空 Auto)。

### 3. 配置与 Prompt 注入 (Settings MVP)
- [ ] **Settings 页面升级**
  - [ ] 新增 `Prompt Configuration` 区域。
  - [ ] 添加 Strategist / Writer / Critic 三个 Textarea。
  - [ ] 实现 LocalStorage 读取与保存 (默认值来自后端 Jinja2 模板)。
- [ ] **In-Flight Injection**
  - [ ] 修改 `useAgentStore.ts`: 在 `startSession` 时读取 LocalStorage。
  - [ ] 实现 **Payload Prefix 注入**: 将 Prompt 拼接到 User Input 前面。

### 4. 业务流适配 (Workflow Adaptation)
- [ ] **两段式调用改造**
  - [ ] 拆分 `startSession` -> `analyze` (Step 1) + `generate` (Step 2)。
  - [ ] Store 新增 `strategyOptions` 和 `isWaitingForSelection` 状态。
- [ ] **Strategy Selector 组件**
  - [ ] 创建 `src/features/studio/components/StrategySelector.tsx`。
  - [ ] 显示 Strategist 生成的选项卡片 (Title, Hook, Outline)。
  - [ ] 点击卡片触发 `generate`。

---

## ✅ 验收标准 (Acceptance Criteria)

### 功能验收
- [ ] **输入**: 首页可见居中大输入框，输入文字后回车可启动。
- [ ] **知识库**: 默认 "智能匹配"，无需手动选择即可开始。
- [ ] **设置**: 刷新页面后，修改过的 Prompt 依然保留。
- [ ] **注入**: 生成的文章风格应该受自定义 Prompt 影响 (e.g. 加口癖)。

### 业务流验收
- [ ] **流程完整性**: Input -> Strategist Thinking -> **Option Selection** -> Writer Drafting -> Critic -> Polish -> Final Output.
- [ ] **数据完整性**: 最终 Markdown 包含标题、正文、并符合选定的长度和风格。

---

## 📝 变更日志 (Changelog)
- **2026-01-20**: 任务清单创建，基于 [6-1 Plan](./6-1_Plan_Pragmatic_Fix.md)。
