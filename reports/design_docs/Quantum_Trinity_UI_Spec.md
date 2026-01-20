# 🎨 Quantum Trinity UI 设计规范 (v1.0)

> **对应版本**: v5.1
> **核心哲学**: Adaptive, Immersive, Agentic.

---

## 1. 布局规范 (Layout Specs)

应用采用 **Fluid Trinity Grid** (流体三栏网格)。

### 1.1 尺寸定义
*   **Viewport**: `h-screen w-screen overflow-hidden` (无滚动)
*   **Left (Sidebar)**: `w-[280px]` (Fixed)
    *   *Border*: `border-r border-white/5`
    *   *Bg*: `bg-zinc-900/50 backdrop-blur-xl`
*   **Center (Canvas)**: `flex-1` (Fluid)
    *   *Max Width*: `max-w-3xl` (文本区居中)
    *   *Padding*: `px-8 py-6`
*   **Right (Inspector)**: `w-[320px]` (Fixed, Collapsible)
    *   *Border*: `border-l border-white/5`
    *   *Bg*: `bg-zinc-900/30 backdrop-blur-md`

### 1.2 颜色系统 (Color System - "Dark Glass")

| Token | Tailwind Class | Hex (Ref) | 用途 |
| :--- | :--- | :--- | :--- |
| `bg-background` | `bg-zinc-950` | `#09090b` | 应用底色 |
| `bg-surface` | `bg-zinc-900/50` | `#18181b80` | 面板背景 |
| `border-border` | `border-white/5` | `rgba(255,255,255,0.05)` | 微妙分割线 |
| `text-primary` | `text-zinc-100` | `#f4f4f5` | 主要文字 |
| `text-muted` | `text-zinc-500` | `#71717a` | 次要文字 |
| `text-accent` | `text-indigo-400` | `#818cf8` | 强调/激活状态 |

---

## 2. 交互规范 (Interaction Specs)

### 2.1 空间切换 (Space Switcher)
*   **Trigger**: 左侧栏顶部 Header。
*   **Behavior**: 点击弹出 `DropdownMenu`。
*   **Transitions**: 侧边栏内容区使用 `AnimatePresence` (如果可能) 或简单的 DOM 替换。

### 2.2 思考时间轴 (Agent Timeline)
*   **Stream**: 新步骤从底部出现 (或顶部，取决于设计，目前推荐顶部最新)。
*   **Status**:
    *   `Pending`: 灰度/Empty Circle.
    *   `Active`: 蓝色脉冲/Loading Spinner.
    *   `Completed`: 绿色对勾.
    *   `Error`: 红色感叹号.

---

## 3. 字体排印 (Typography)
*   **Font Family**: `Inter` (Sans), `JetBrains Mono` (Code/Logs).
*   **H1 (Title)**: `text-2xl font-bold tracking-tight`.
*   **Body**: `text-base leading-relaxed text-zinc-300`.
