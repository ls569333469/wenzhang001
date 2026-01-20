# 🏗️ Quantum Studio Architecture & Execution Plan

> **版本**: v8.2 (Digital Luxury Edition)  
> **更新日期**: 2026-01-20  
> **状态**: ✅ Phase 3 Complete → Phase 4 Ready  
> **适用框架**: Next.js 16 / React 19 / Tailwind CSS v4+  
> **维护者**: CPO & Lead Architect

---

## 📜 序言：2026 工业级准则 (The 2026 Manifesto)

本项目拒绝平庸。作为 Web3 领域的顶级投研引擎，Quantum Studio 的代码必须体现 **2026 年的工业级标准**：

| 原则 | 描述 |
| :--- | :--- |
| **Atomic Consistency** | 任何 UI 元素必须复用 `src/components/ui` 中的标准组件 |
| **Visual Governance** | 严禁偏离 "Digital Luxury" 设计规范 |
| **Responsive Gravity** | 布局必须具备弹性，支持大屏自适应 |

---

## 🎨 Part 1: Visual Governance (视觉宪法)

### 1.1 核心禁令 (The Ban List) ⛔

> 违反以下任一规则，代码将被回滚。

- ❌ **禁止硬编码颜色**: 严禁使用 HEX 值，必须使用语义变量
- ❌ **禁止默认链接**: `<a>` 标签必须被封装，严禁出现默认蓝色下划线
- ❌ **禁止分裂导航**: 全站只能引用 `src/components/layout/AppSidebar.tsx`
- ❌ **禁止布局僵化**: 核心内容区必须支持 `flex-1` 自适应高度
- ❌ **禁止功能冗余**: 严禁保留后端不支持的 UI 元素

### 1.2 Design Tokens (设计变量)

> 配置已固化在 `tailwind.config.ts` 中

| Token | CSS Class | Value | 用途 |
| :--- | :--- | :--- | :--- |
| Paper | `bg-paper` | #F9F8F6 | 全站唯一背景色 |
| Surface | `bg-surface` | #FFFFFF | 组件容器背景 |
| Ink Primary | `text-ink-primary` | #27272A | 正文，强标题 |
| Ink Muted | `text-ink-muted` | #71717A | 辅助信息 |
| Hairline | `border-hairline` | #E4E4E7 | 极细分割线 |

### 1.3 Digital Luxury 美学原则 (v8.0+)

| 原则 | 实现方式 |
| :--- | :--- |
| **Typography as Interface** | 用字号/字重/浓度构建层级，不用色块堆叠 |
| **Airiness & Breathing Room** | 大量留白，极简分割线 |
| **Anchoring & Gravity** | 行动按钮锚定底部 + 渐变消隐效果 |

---

## 🧩 Part 2: Component Registry (组件注册表)

### 2.1 布局组件 (Layouts)

| 组件 | 路径 | 状态 | 规格 |
| :--- | :--- | :---: | :--- |
| **AppSidebar** | `src/components/layout/AppSidebar.tsx` | ✅ | 280px, shrink-0, 无 Search/Free Plan |
| **WritingCanvas** | `src/features/workbench/components/WritingCanvas.tsx` | ✅ | 垂直居中, 无冗余按钮 |
| **AgentInspector** | `src/features/workbench/components/AgentInspector.tsx` | ✅ | 380px, 全文显示 |

### 2.2 原子组件 (Atoms)

| 组件 | 路径 | 样式 |
| :--- | :--- | :--- |
| **PaperCard** | `src/components/ui/paper-card.tsx` | `bg-surface border-hairline rounded-sm p-6 shadow-sm` |
| **ActionTile** | `src/components/ui/action-tile.tsx` | `flex gap-4 p-4 border-hairline hover:bg-zinc-50` |

---

## 🚀 Part 3: Execution Roadmap (执行路线图)

### ✅ Phase 2: Infrastructure & Dashboard (已完成)

- [x] System Ignition: 后端端口 (8002) 联通，状态灯变绿
- [x] Sidebar Polish: 修复底部遮挡，移除冗余的 Search/Free Plan
- [x] Localization: Dashboard 全面汉化

### ✅ Phase 3: Studio Migration & Refinement (已完成)

**Step 3.1: Layout Structure (Quantum Trinity)**
- [x] 实现左(配置)/中(画布)/右(监测) 三栏布局
- [x] 汉化配置面板与 Inspector

**Step 3.2: Interaction Repair (UX)**
- [x] Button Logic: "开始创作" 按钮固定底部 + 渐变遮罩
- [x] Canvas Cleanup: 移除 "Begin Analysis" 按钮
- [x] 添加 "系统设置" 快捷入口

**Step 3.3: Responsive Gravity (自适应优化)**
- [x] Vertical Center: 画布空状态垂直居中
- [x] Large Screen: 左侧面板 320px，右侧面板 380px
- [x] Button Size: 加大点击区域 (py-4)

**Step 3.4: Digital Luxury Aesthetic (美学重塑)**
- [x] Typography as Interface: 用排版构建层级
- [x] Airiness: 大量留白，极简边框
- [x] Floating Action: 按钮带渐变消隐效果

### ✅ Phase 3.5: System Sweep (已完成)

- [x] 删除僵尸文件 (monitor-card.tsx, SidebarConfig.tsx)
- [x] 更新 Knowledge/Settings 占位页
- [x] 代码卫生审计通过

### 🎯 Phase 4: Knowledge & Settings (当前焦点)

**Step 4.1: Knowledge Page**
- [x] Gallery Grid 布局
- [x] 文档卡片预览
- [x] 搜索框 + 上传按钮
- [ ] 后端 API 联调

**Step 4.2: Settings Page**
- [x] 两栏式表单布局
- [x] LLM Provider / API Key / Temperature / System Prompt
- [x] 飞书集成配置
- [ ] 后端 API 联调

### 📋 Phase 5: Production Ready (Next)

- [ ] 后端 API 全量联调
- [ ] 错误边界与 Loading 状态
- [ ] 性能优化与缓存策略
- [ ] 部署与 CI/CD

---

## 💻 Part 4: Engineering Standards (配置标准)

### 4.1 Tailwind Config (Critical)

```typescript
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}", // 🚨 必须保留
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F9F8F6",
        surface: "#FFFFFF",
        ink: { primary: "#27272A", muted: "#71717A" },
        hairline: "#E4E4E7",
      },
      fontFamily: {
        serif: ["var(--font-newsreader)", "serif"],
        sans: ["var(--font-geist-sans)", "sans-serif"],
      },
    },
  },
};
```

### 4.2 Studio 三层布局结构 (v8.2)

```tsx
<aside className="w-[320px] h-full flex flex-col">
  {/* TIER 1: Header (shrink-0) */}
  <div className="px-6 pt-8 pb-6 shrink-0">...</div>
  
  {/* TIER 2: Scrollable Content (flex-1) */}
  <div className="flex-1 overflow-y-auto px-6">...</div>
  
  {/* TIER 3: Sticky Footer (shrink-0 + gradient) */}
  <div className="shrink-0 relative">
    <div className="absolute -top-20 h-20 bg-gradient-to-t from-white to-transparent" />
    <div className="bg-white px-6 pb-6 pt-4">
      <button>开始创作</button>
    </div>
  </div>
</aside>
```

---

## 📊 Current Status Summary

```
┌─────────────────────────────────────────────────────────┐
│                   Quantum Studio v8.2                   │
├─────────────────────────────────────────────────────────┤
│  Phase 2: Infrastructure     ████████████████████ 100%  │
│  Phase 3: Studio Migration   ████████████████████ 100%  │
│  Phase 4: Knowledge/Settings ████████████░░░░░░░░  60%  │
│  Phase 5: Production Ready   ░░░░░░░░░░░░░░░░░░░░   0%  │
├─────────────────────────────────────────────────────────┤
│  🎯 Current Focus: Phase 4 - Backend API Integration    │
└─────────────────────────────────────────────────────────┘
```

---

<p align="center">
  <b>Quantum Studio</b> — Digital Luxury for Web3 Research
</p>