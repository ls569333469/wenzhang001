💎 2026 Quantum Studio 前端架构与开发规范 (Final Master v3.1)版本: v3.1 (Schema-First & State-Layered)状态: 🔴 最终执行版核心: 以 Schema 为骨架，以 Vibe 为皮囊，以 Server Actions 为血肉。📑 目录核心理念 (Philosophy)数据与状态规范 (Data & State Architecture) ⭐ (修复重点)视觉系统规范 (Visual System)项目结构与岛屿架构 (Island Architecture)组件设计模式 (Co-location)AI 协作工作流 (The Workflow)🚨 当前重构任务清单 (Action Plan)1. 核心理念 (Philosophy)Schema is King: 一切开发始于 schema.ts。它是 UI、API 和 数据库的共同契约。User is Architect: 开发者负责定义“真理”（Schema）和“审美”（Vibe），AI 负责填充代码。Vibe First: 拒绝工业软件的冰冷感。追求“悬浮”、“留白”和“微交互”。2. 数据与状态规范 (Data & State Architecture)💡 这是 React 19 时代最核心的规范。请严格遵守以下分层，严禁混用。2.1 唯一真理源 (Single Source of Truth)所有业务实体定义必须写在 Feature 目录下的 schema.ts 中。严禁手写 TypeScript Interface。TypeScript// features/studio/schema.ts
import { z } from 'zod';

export const CreationConfigSchema = z.object({
  topic: z.string().min(1, "Topic is required"),
  role: z.enum(['professional', 'storyteller']),
  // ...更多字段
});

// ✅ 自动推导类型，随 Schema 自动更新
export type CreationConfig = z.infer<typeof CreationConfigSchema>;
2.2 状态四层模型 (The 4-Layer State Model)状态类型推荐方案 (2026)适用场景示例URL 状态nuqs (Type-safe search params)最优先。配置项、搜索词、Tab切换。让链接可分享。?role=kol&tab=config服务端状态Server Components / Actions数据库数据、生成结果。直接 await 获取，不存客户端 Store。知识库列表、文章内容表单状态React Hook Form + Zod瞬时输入数据、校验错误信息。文章生成配置表单UI 交互状态Zustand (Minimal)最后手段。仅用于纯客户端交互（侧边栏开关、弹窗）。useUIStore.isOpen2.3 Server Actions 规范重业务逻辑（如 LLM 调用）必须封装在 Server Actions 中，前端只负责 invoke。TypeScript// features/studio/actions.ts
'use server'

export async function generate(data: CreationConfig) {
  // 1. 在服务端再次校验 Schema
  const parsed = CreationConfigSchema.parse(data);
  // 2. 执行逻辑
  return await llm.call(parsed);
}
3. 视觉系统规范 (Visual System)3.1 核心色调 (Zinc & Flow)Canvas: bg-zinc-50 (画布)。Islands: bg-white + shadow-sm + border-zinc-100 (悬浮岛)。Accent: 使用黑色 (bg-zinc-900) 作为主要行动点，拒绝高饱和度蓝/绿色。3.2 字体与排版Headings: font-serif (Newsreader) —— 赋予高级编辑感。UI Controls: font-sans (Geist/Inter) —— 保持清晰易读。Radius: rounded-xl (12px) 是基准，大卡片用 rounded-2xl (16px)。4. 项目结构与岛屿架构 (Island Architecture)原则: 扁平化，按“业务域”组织。src/
├── app/
│   ├── layout.tsx            # Canvas Layer (全屏背景)
│   └── (studio)/studio/      # 业务页面
│       └── page.tsx          # 页面入口
│
├── components/
│   ├── ui/                   # ⚡ Primitives (Shadcn基础元件)
│   └── layout/               # 🏝️ Islands (Navbar, SidebarFrame)
│
├── features/
│   └── studio/               # ⚛️ Quantum Studio 核心业务域
│       ├── schema.ts         # ⭐ [STEP 1] 真理源
│       ├── actions.ts        # ⭐ [STEP 3] 服务端逻辑
│       ├── stores/           # 仅存放 UI 状态 (useStudioUI.ts)
│       ├── components/       # 业务组件 (Co-located)
│       │   ├── ConfigPanel.tsx
│       │   ├── AgentTimeline.tsx
│       │   └── PreviewCard.tsx
│       └── hooks/            # 业务 Hooks
│
└── lib/                      # 通用工具
5. 组件设计模式 (Co-location)5.1 废弃清单 (❌ Don't)❌ Atomic Design: 停止思考“这是原子还是分子”。❌ Container/View: 禁止将逻辑和 UI 拆分到不同文件。这会打断 AI 上下文。5.2 岛屿模型 (✅ Do)组件应当是自包含的。TypeScript// features/studio/components/ConfigPanel.tsx
'use client'; 

import { useQueryState } from 'nuqs'; // URL 状态
import { CreationConfigSchema } from '../schema'; // Schema

export function ConfigPanel() {
  // 1. 状态直接挂在 URL 上，刷新不丢失
  const [role, setRole] = useQueryState('role'); 
  
  return (
    // 2. 视觉：悬浮岛屿风格
    <aside className="fixed left-4 top-20 w-80 bg-white rounded-2xl shadow-sm border border-zinc-100 p-6">
       {/* UI Code */}
    </aside>
  );
}
6. AI 协作工作流 (The Workflow)Define (人): 修改 schema.ts，定义数据结构。Prompt (人 -> AI): "基于 schema.ts，为我生成 ConfigPanel 组件。使用 Shadcn UI，所有状态使用 nuqs 同步到 URL。"Generate (AI): AI 生成包含 UI 和 Logic 的完整代码。Refine (人): 微调 Tailwind 类名（如 p-4 改为 p-6），调整动画。7. 🚨 当前重构任务清单 (Action Plan)这是你现在立刻需要执行的任务，请按顺序勾选：Phase 1: 地基清理与配置 (The Purge)[ ] 全局样式重置: 清空 globals.css，只保留 Tailwind 指令。[ ] 视觉配置: 更新 tailwind.config.ts，写入 Zinc 色系和 Fonts。[ ] 依赖安装: 安装 nuqs (npm install nuqs) 用于 URL 状态管理。Phase 2: 核心数据层 (Data Layer)[ ] Schema 完善: 检查 features/studio/schema.ts，确保包含 Topic, Role, Length 等所有字段。[ ] Store 简化: 如果有复杂的 Zustand Store，尝试将其拆分。将业务数据移至 Schema/URL，Zustand 只留 UI 状态（如 isSidebarOpen）。Phase 3: 岛屿重建 (Island Construction)[ ] Canvas: 重写 src/app/layout.tsx，设置背景为 bg-zinc-50。[ ] ConfigPanel: 基于 Schema + nuqs 重写左侧面板。(抛弃旧的下拉框，改用卡片选择)。[ ] Preview: 重写中间区域，实现一个大的 Hero 输入框。[ ] Timeline: 重写右侧，使用 Step 样式展示 Agent 状态。Phase 4: 逻辑接入 (Wiring)[ ] Server Action: 创建 features/studio/actions.ts，实现 generate() 方法。[ ] Binding: 在 ConfigPanel 的提交按钮上绑定 Server Action