# **AI 内容创作工具 - UI/UX 设计规范 (v5.8.3)**

## **1. 全局视觉基调 (Global Theme)**

应用采用 **沉浸式深色模式 (Immersive Dark Mode)**，风格偏向现代科技感与 Web3 极客风。

- **主背景**: bg-slate-900 (#0f172a) - 深蓝灰色，提供高对比度基础。
- **卡片/面板背景**: bg-slate-800/50 (50% 透明度) - 半透明磨砂感，用于区分层级。
- **强调色 (Primary)**:
    - **Cyan**: text-cyan-400 / bg-cyan-500 - 用于高亮、激活状态、主要按钮。
    - **Violet**: text-violet-400 / bg-violet-500 - 用于次要强调或渐变搭配。
    - **Gradient**: from-cyan-400 to-violet-500 - 用于主标题和核心操作按钮。
- **文本颜色**:
    - 主要文本: text-slate-200 (#e2e8f0)
    - 次要文本/说明: text-slate-400 (#94a3b8)
    - 微弱提示: text-slate-500 (#64748b)

---

## **2. 页面布局架构 (Layout Structure)**

应用采用 **全屏单页应用 (SPA)** 布局，垂直方向分为三部分，核心工作区采用 **10列网格系统**。

### **2.1 外层容器 (App Shell)**

- **视口高度**: h-screen (100vh)，内容超出时内部滚动，而非整体页面滚动。
- **全局内边距 (Padding)**:
    - Mobile: p-4 (16px)
    - Tablet: sm:p-6 (24px)
    - Desktop: lg:p-8 (32px)
- **布局流**: Flex Column (flex-col).

### **2.2 顶部导航区 (Header & Tabs)**

- **Header 高度区域**: 约 80px - 100px (包含 Title 和 TabSelector)。
- **间距**:
    - Header 与 TabSelector 间距: mt-8 (32px)。
    - TabSelector 与 主内容区间距: mt-6 (24px)。

### **2.3 核心工作区 (Main Workspace Grid)**

这是仿写、原创、Alpha Hunter 等页面的核心布局，使用了 CSS Grid。

- **Grid 定义**: grid-cols-10 gap-6 (10列网格，列间距 24px)。
- **列分配 (三栏式布局)**:
    1. **左侧栏 (配置与输入)**: 占 **4列** (col-span-4)。
        - 用途: 原文输入、参数配置、历史记录。
    2. **中间栏 (结果展示)**: 占 **3列** (col-span-3)。
        - 用途: 预览生成结果、交互式重构。
    3. **右侧栏 (AI 工作台)**: 占 **3列** (col-span-3)。
        - 用途: 思考过程流、推特预览、衍生内容生成。

> 响应式适配: 在移动端，Grid 会自动坍缩为单列布局 (grid-cols-1)，各板块垂直堆叠。
> 

---

## **3. 组件详细尺寸 (Component Dimensions)**

### **3.1 容器卡片 (Cards / Panels)**

所有功能模块（如输入框容器、历史记录、热点面板）都统一使用此样式。

- **圆角**: rounded-2xl (16px)。
- **内边距**: p-6 (24px)。
- **边框**: border border-slate-700 (1px 实线)。
- **阴影**: shadow-lg。

### **3.2 文本输入框 (Textareas)**

- **圆角**: rounded-lg (8px)。
- **背景**: bg-slate-900/80 (深色高透明度)。
- **高度**:
    - 标准输入区: h-64 (256px) 或 h-80 (320px) 或 h-40 (160px) 取决于模块。
- **内边距**: p-4 (16px)。
- **交互**: Focus 时 ring-2 ring-cyan-500。

### **3.3 按钮 (Buttons)**

### **A. 核心操作按钮 (Action Button - Primary)**

用于“智能仿写”、“开始生成”等触发 AI 的操作。

- **高度**: py-4 (约 56px 高)。
- **宽度**: w-full (占满容器)。
- **背景**: 渐变 bg-gradient-to-r from-cyan-500 to-violet-500。
- **圆角**: rounded-lg (8px)。
- **字号**: text-base font-bold (16px 粗体)。
- **动效**: Hover 时 scale-105 (放大 5%)。

### **B. 标签切换按钮 (Tab Selector Buttons)**

顶部的主导航。

- **容器圆角**: rounded-xl (12px)。
- **容器内边距**: p-1.5 (6px)。
- **单个 Tab**:
    - 内边距: px-3 py-2.5 (水平12px, 垂直10px)。
    - 圆角: rounded-lg (8px)。
    - 激活态: bg-cyan-500 text-white。
    - 默认态: text-slate-300 hover:bg-slate-700/50。

### **C. 风格选择胶囊 (Style Pills)**

用于选择写作风格的小按钮。

- **内边距**: px-4 py-3。
- **圆角**: rounded-lg (8px)。
- **布局**: Grid 布局，grid-cols-2 或 grid-cols-4。

### **3.4 模态框 (Modals)**

用于“风格预览”、“全文重构”、“IP 锻造”等。

- **遮罩层**: bg-black/60 backdrop-blur-sm (黑色半透明 + 背景模糊)。
- **主体容器**:
    - 最大宽度: max-w-3xl (768px) 或 max-w-2xl。
    - 最大高度: max-h-[80vh] 或 max-h-[90vh]。
    - 圆角: rounded-2xl (16px)。
    - 背景: bg-slate-800。

---

## **4. 排版规范 (Typography)**

- **字体家族**: 系统默认 Sans-serif (Inter, Roboto, SF Pro 等)。
- **层级尺寸**:
    - **H1 (App Title)**: text-4xl (36px) ~ text-5xl (48px)，font-extrabold。
    - **H2 (Section Title)**: text-xl (20px) ~ text-2xl (24px)，font-semibold，通常配合 text-cyan-400。
    - **H3 (Card Title)**: text-lg (18px)，font-semibold。
    - **Body (正文)**: text-base (16px) 或 text-sm (14px)。
    - **Label/Meta (辅助信息)**: text-xs (12px)。

---

## **5. 特殊交互区域 (Special UX Areas)**

### **5.1 结果展示区 (Result Display)**

- 这是一个富文本交互区域。
- **段落间距**: 使用 Tailwind Typography 插件 (prose)，通常段落间有默认的 margin-bottom。
- **交互**: 鼠标悬停段落时，背景变色 (bg-slate-800/50)，并出现悬浮工具栏 (Magic Wand Icon)。

### **5.2 思考过程 (Thinking Process)**

- 位于右侧工作台。
- 字体: 可能是等宽字体或普通字体，但使用了 Markdown 渲染。
- 引用样式: border-l-4 border-amber-500 pl-4 (左侧琥珀色边框)。

### **5.3 历史记录项 (History Item)**

- **高度**: 约 60px - 70px。
- **内边距**: p-3。
- **背景**: bg-slate-900/60。
- **动效**: Hover 时显示“恢复”按钮。

---

## **6. 总结：关键 CSS 类速查表**元素	核心 CSS 类组合	尺寸/视觉
主背景	bg-slate-900 text-slate-200	深色底，浅色字
功能卡片	bg-slate-800/50 rounded-2xl border border-slate-700 p-6	半透明，圆角16px
主要按钮	bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg py-4 font-bold	渐变，高56px
次要按钮	bg-slate-700 hover:bg-slate-600 rounded-lg px-4 py-2	深灰色
输入框	bg-slate-900/80 border border-slate-600 rounded-lg p-4 focus:ring-cyan-500	深色凹陷感
选中状态	border-cyan-500 或 bg-cyan-500 text-white	亮青色高亮
布局网格	grid grid-cols-10 gap-6	10列，间距24px