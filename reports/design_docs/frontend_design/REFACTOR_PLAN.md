# 🏗️ Quantum Studio Vibe Refactor Plan

> **Status**: 🟡 Phase 1 Complete → Phase 2 Ready  
> **Objective**: Transform legacy UI into 2026 Vibe Coding Standard  
> **Reference**: 请始终遵循 `Frontend_Industry_Standard_2026.md` 中的规范。

---

## ✅ Phase 1: 拆迁与净化 (The Purge)
**目标**: 将项目重置为一张干净的、配置好高级灰（Zinc）色系的白纸。

- [x] **1.1 依赖安装**
  - [x] 执行 `npm install nuqs` (URL状态管理)。
  - [x] 确认 `zod@4.3.5` 已安装。
  - [x] 确认 `clsx@2.1.1`, `tailwind-merge@3.4.0` 已安装。

- [x] **1.2 视觉系统注入 (Visual System)**
  - [x] 更新 `tailwind.config.ts`：
    - [x] 覆盖 `colors` 为 Zinc 色系 (primary: #18181b)。
    - [x] 设置默认 `radius` 为 `0.75rem` (12px)。
    - [x] 注入 `font-sans` (Geist) 和 `font-serif` (Newsreader)。
    - [x] 添加 `shadow-island` 系列阴影。
  - [x] 清理 `globals.css`：删除除了 Tailwind 指令外的所有自定义样式。
  - [x] 强制 Body 背景：`bg-canvas` (#FAFAFA)。

- [x] **1.3 组件库瘦身**
  - [x] 检查 `containers/` / `views/` 目录 → 不存在，无需删除。
  - [x] **保留**: `features/studio/schema.ts` ✓
  - [ ] 清理未使用的旧 UI 组件 (待评估)。

**Phase 1 完成时间**: 2026-01-20 14:00

---

## 🎨 Phase 2: 地基与视觉验证 (Foundation & Design Lab)
**目标**: 确立布局框架，并通过静态页面验证"高级感"风格。

- [x] **2.1 布局重写 (Canvas Layer)**
  - [x] 重写 `src/app/layout.tsx`。
  - [x] 配置 `next/font` (Geist Sans + Newsreader)。
  - [x] 设置全屏画布背景 `bg-canvas`。
  - [x] 添加 `NuqsAdapter` Provider。

- [x] **2.2 岛屿骨架 (Island Skeletons)**
  - [x] 创建悬浮导航栏 (`Navbar`) - Fixed Top。
  - [x] 创建左侧悬浮框架 (`LeftSidebar`) - Fixed Left。
  - [x] 创建右侧悬浮框架 (`RightSidebar`) - Fixed Right。
  - [x] 样式要求：`bg-island rounded-2xl shadow-island border border-zinc-100`。

- [x] **2.3 视觉实验室 (Design Lab)**
  - [x] 创建路由 `app/design-lab/page.tsx`。
  - [x] 使用硬编码数据，组装上述骨架。
  - [x] **验收**: 确认阴影、圆角、字体是否符合 "High-End Minimalism"。
  - [x] **Fix**: Downgraded Tailwind to v3.4.17 to resolve v4 config mismatch.
  - [x] **变体**: Created Variant A (Islands), B (Workbench), C (Zen) for review.

**Phase 2 完成时间**: 2026-01-20 15:10

---

## ⚛️ Phase 3: 业务组件生成 (Component Generation)
**目标**: 基于 Schema 生成真实的业务组件，替换骨架。

- [x] **3.1 核心布局架子 (Island Stacking)**
  - [x] 创建 `IslandContainer` 封装。
  - [x] 创建 `ConfigIsland` (Left) & `AgentIsland` (Right).
  - [x] 创建 `StudioLayout` 并组装 `app/studio/page.tsx`。
- [x] **3.2 配置面板 (`ConfigPanel`)**
  - [x] 接入 `schema.ts` 定义的 Zod 校验。
  - [x] 接入 `nuqs` URL State (Mode, Style, Length).
- [x] **3.3 智能体时间轴 (`AgentTimeline`)**
  - [x] 定义 `TimelineStep` 类型。
  - [x] 实现 Visual States (Idle, Thinking, Active, Completed).
  - [x] 集成到 `AgentIsland` 并验证动画效果。
  - [ ] 状态：idle / active / completed / error。

- [ ] **3.3 预览与画布 (PreviewArea)**
  - [ ] 重写中间区域。
  - [ ] 实现 Hero 风格的输入框。
  - [ ] Empty State 设计。

---

## 🔌 Phase 4: 逻辑接入 (Wiring)
**目标**: 让界面动起来。

- [ ] **4.1 Server Actions**
  - [ ] 创建 `features/studio/actions.ts`。
  - [ ] 实现 `generate()` 方法，调用后端 API。
  - [ ] Zod 验证 + 错误处理。

- [ ] **4.2 交互绑定**
  - [ ] 在 `ConfigPanel` 绑定提交事件。
  - [ ] 使用 `useActionState` 处理 Loading 状态。
  - [ ] 对接 SSE 流式输出。

- [ ] **4.3 最终验收**
  - [ ] 完整流程测试。
  - [ ] 响应式适配。
  - [ ] 性能检查。

---

## 📊 Progress Tracker

```
Phase 1: 拆迁与净化     ████████████████████ 100% ✅
Phase 2: 地基与视觉验证 ░░░░░░░░░░░░░░░░░░░░   0% ← NEXT
Phase 3: 业务组件生成   ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: 逻辑接入       ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## 🎯 AI 指挥术 (How to Use)

### 开始 Phase 2:
```
请读取 Frontend_Industry_Standard_2026.md 作为核心规范。
然后读取 REFACTOR_PLAN.md，仅执行 Phase 2 的所有任务。
每完成一个小项，请在 plan 文件中打勾 [x]。
```

### 开始 Phase 3:
```
Phase 2 已完成。请继续参考规范文档，执行 REFACTOR_PLAN.md 中的 Phase 3。
基于 features/studio/schema.ts 生成组件，使用 nuqs 绑定 URL 状态。
```

---

<p align="center">
  <b>Quantum Studio</b> — Vibe Coding Refactor
</p>
