# Phase 5.8: 本地化对齐实施计划 (Alignment & Localization)

## 目标 (Goal)
将 UI 从“通用英文原型”转变为“中文业务应用”，通过本地化内容、解耦配置和修复导航缺失来实现。

## 用户审查点 (User Review Required)
- **术语 (Terminology)**:
  - Temperature -> "创意程度 (随机性)"
  - Top P -> "思维发散度 (Top P)"
- **路由 (Routes)**:
  - `/knowledge` -> 知识库管理 (占位页)
  - `/agents` -> 智能体状态 (占位页)

## 变更提案 (Proposed Changes)

### 1. 配置解耦 (`src/config/constants.ts`) [NEW]
创建一个中心化的常量文件来管理下拉选项和 UI 配置。
- `CREATION_MODES`: 定义 "深度分析", "快速摘要" 等模式。
- `ARTICLE_LENGTHS`: 定义 "短篇", "中篇", "长文"。
- `WEB3_KNOWLEDGE_BASES`: 从 `ConfigPanel` 移动至此。
- `UI_TEXT`: 通用 UI 标签常量 (可选)。

### 2. UI 重构 (`ConfigPanel.tsx`) [MODIFY]
- **导入常量**: 将硬编码的 `SelectionCard` 列表替换为 `.map(CREATION_MODES...)`。
- **本地化 (Localization)**:
  - 替换 "Core Settings" -> "✨ 核心配置"
  - 替换 "Advanced Settings" -> "⚡ 高级模型设置" (默认折叠)
  - 替换 输入框 Placeholder -> "请输入您的研究主题或指令..."
  - 替换 按钮 -> "开始深度创作"
- **UX**:
  - 默认折叠 "高级模型设置" (从 Accordion `defaultValue` 中移除)。

### 3. 导航与页面 [NEW]
- **`src/app/(main)/knowledge/page.tsx`**: 空状态页面。
- **`src/app/(main)/agents/page.tsx`**: 空状态页面。
- **`src/components/layout/AppSidebar.tsx`**: 更新链接指向这些新路由。

### 4. 组件本地化 [MODIFY]
- **`src/features/studio/components/timeline/AgentTimeline.tsx`**: 将 "Strategy", "Drafting" 等状态本地化为 "策略分析", "正在撰写"。

## 验证计划 (Verification Plan)
1.  **视觉检查**:
    - 确认 ConfigPanel 中的所有文本均为中文。
    - 确认 "高级模型设置" 初始即为折叠状态。
    - 确认下拉菜单/卡片从 `constants.ts` 正确渲染。
2.  **导航检查**:
    - 点击侧边栏 "知识库 (Knowledge Brain)" -> 跳转至 `/knowledge` -> 显示 "功能开发中"。
    - 点击 "智能体团队 (Agent Team)" -> 跳转至 `/agents` -> 显示 "功能开发中"。
