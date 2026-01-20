Quantum Studio Architecture & Execution Plan v6.2更新日期: 2026-01-20版本: v6.2 (Live Standard)状态: Active Execution (Phase 3.6 Refinement)适用框架: Next.js 16 / React 19 / Tailwind CSS v4+维护者: CPO & Lead Architect核心变更: 集成 Studio 交互重构规范 (UX Refinement) 与大屏自适应标准 (Responsive Gravity)。📜 序言：2026 工业级准则 (The 2026 Manifesto)本项目拒绝平庸。作为 Web3 领域的顶级投研引擎，Quantum Studio 的代码必须体现 2026 年的工业级标准：Atomic Consistency (原子一致性): 任何 UI 元素（按钮、卡片、输入框）必须复用 src/components/ui 中的标准组件，严禁手写 HTML 标签。Visual Governance (视觉治理): 任何偏离 "Paper Mode" 设计规范的样式（如默认蓝色链接、纯白背景、无衬线正文）均视为 Critical Bug。Responsive Gravity (自适应重力): 界面布局必须具备弹性 (Flex)，核心内容区需支持 flex-1 自动填充，严禁在大屏设备上出现内容挤压或布局失衡。🎨 Part 1: Visual Governance (视觉宪法)1.1 核心禁令 (The Ban List) ⛔违反以下任一规则，代码将被回滚。❌ 禁止硬编码颜色: 严禁使用 HEX 值（如 #F9F8F6），必须使用语义变量 bg-paper, text-ink-primary。❌ 禁止默认链接: <a> 标签必须被封装，严禁出现浏览器默认的蓝色/紫色下划线。❌ 禁止分裂导航: 全站必须且只能引用的唯一侧边栏组件是 src/components/layout/AppSidebar.tsx。❌ 禁止布局僵化: 核心内容区必须支持 flex-1 自适应高度，空状态内容必须垂直居中。❌ 禁止功能冗余: 严禁保留后端不支持的 UI 元素（如搜索框、计费状态）。1.2 Design Tokens (设计变量)配置已固化在 tailwind.config.ts 中TokenCSS ClassValue用途Paperbg-paper#F9F8F6全站唯一背景色 (Warm White)Surfacebg-surface#FFFFFF组件容器背景 (Sidebar, Cards)Ink Primarytext-ink-primary#27272A正文，强标题 (Zinc-800)Ink Mutedtext-ink-muted#71717A辅助信息 (Zinc-500)Hairlineborder-hairline#E4E4E7极细分割线 (Zinc-200)🧩 Part 2: Component Registry (组件注册表)Rule: 任何新页面开发，必须优先使用以下组件。2.1 布局组件 (Layouts)AppSidebar (Singleton)Path: src/components/layout/AppSidebar.tsxStatus: ✅ v6.2 标准化 (Clean Version)Specs: 宽度 280px，shrink-0 防遮挡，已移除 Search/Free Plan。WritingCanvas (Studio Core)Path: src/features/studio/components/WritingCanvas.tsxStatus: 🔄 Phase 3.6 重构中Specs: 必须支持垂直居中 (justify-center)，移除所有冗余按钮。2.2 原子组件 (Atoms)PaperCard (Container)Path: src/components/ui/PaperCard.tsxStyle: bg-surface border border-hairline rounded-sm p-6 shadow-smActionTile (Interactive)Path: src/components/ui/ActionTile.tsxStyle: flex items-center gap-4 p-4 border border-hairline bg-surface hover:bg-zinc-50MonitorCard (Dashboard Feature)Path: src/features/dashboard/components/MonitorCard.tsx⚙️ Part 3: Engineering Standards (配置标准)3.1 Tailwind Config (Critical)必须保持以下配置，防止样式丢失：TypeScriptconst config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}", // 🚨 核心配置：必须保留
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
🚀 Part 4: Execution Roadmap (执行路线图) [Updated]✅ Phase 2: Infrastructure & Dashboard (已完成)[x] System Ignition: 后端端口 (8002) 联通，状态灯变绿。[x] Sidebar Polish: 修复底部遮挡 (shrink-0)，移除冗余的 Search/Free Plan。[x] Localization: Dashboard 全面汉化。🔥 Phase 3: Studio Migration & Refinement (当前焦点)Goal: 打造符合人体工学的大屏适配创作工坊。Step 3.1: Layout Structure (Quantum Trinity)[x] 实现左(配置)/中(画布)/右(监测) 三栏布局。[x] 汉化配置面板与 Inspector。Step 3.2: Interaction Repair (UX)[ ] Button Logic: "开始创作" 按钮必须跟随内容流，严禁在大屏下沉底。[ ] Canvas Cleanup: 移除冗余的 "Begin Analysis" 按钮，仅保留中文提示。Step 3.3: Responsive Gravity (自适应优化)[ ] Vertical Center: 画布空状态提示必须在屏幕物理正中心 (h-full + justify-center)。[ ] Fluid Layout: 左侧配置列表需支持 flex-1 弹性伸缩，避免大屏下内容挤在顶部。📋 Phase 4: Knowledge & Settings (Next)Step 4.1: 知识库页面迁移 (Card List View)。Step 4.2: 设置页面表单开发。💻 Part 5: Golden Code (标准实现参考)AI 指令: 在执行开发时，必须使用以下代码片段作为实现的唯一真理。5.1 AppSidebar (v6.2 Clean Standard)已移除搜索框与免费版，包含防遮挡结构。TypeScriptimport React from "react";
import { LayoutGrid, FileText, Settings } from "lucide-react"; 
import Link from "next/link";

export function AppSidebar() {
  return (
    <aside className="w-[280px] h-full flex flex-col border-r border-hairline bg-paper text-ink-primary overflow-hidden">
      {/* Header */}
      <div className="h-14 flex items-center px-4 border-b border-hairline shrink-0">
        <div className="flex items-center gap-2 font-serif font-bold text-lg text-ink-primary">
          <LayoutGrid size={18} /><span>Quantum Studio</span>
        </div>
      </div>
      
      {/* Content - 弹性伸缩 */}
      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        <div className="space-y-1">
           <div className="px-2 text-[10px] font-semibold text-ink-muted uppercase tracking-wider mb-2">最近项目</div>
           <button className="w-full flex items-center gap-3 px-2 py-2 text-sm text-ink-muted hover:bg-zinc-200/50 rounded-sm transition-colors text-left">
             <FileText size={16}/>
             <span>DeFi 周报 (草稿)</span>
           </button>
        </div>
      </div>

      {/* Footer - 防遮挡结构 (shrink-0 + z-10) */}
      <div className="p-3 border-t border-hairline shrink-0 bg-paper z-10">
        <button className="w-full flex items-center gap-3 p-2 hover:bg-zinc-200/50 rounded-sm transition-colors text-left">
          <div className="w-8 h-8 bg-zinc-300 rounded-full flex items-center justify-center text-xs font-serif text-ink-primary">QS</div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate text-ink-primary">Web3 Master</div>
          </div>
          <Settings size={14} className="text-ink-muted" />
        </button>
      </div>
    </aside>
  );
}
5.2 WritingCanvas (v6.2 Center Layout)垂直居中，无冗余按钮。TypeScriptimport React from "react";

export function WritingCanvas({ status, content }: any) {
  if (status === 'idle') {
    return (
      // 核心：h-full + justify-center 实现全屏垂直居中
      <div className="h-full flex flex-col items-center justify-center select-none space-y-6 text-ink-muted">
        <div className="w-20 h-20 rounded-full bg-zinc-100/50 flex items-center justify-center ring-1 ring-zinc-200/50">
          <span className="text-3xl grayscale opacity-30">❖</span>
        </div>
        <div className="text-center space-y-2">
          <p className="text-lg font-medium text-ink-primary">量子引擎已就绪</p>
          <p className="text-sm opacity-60">请在左侧配置参数并点击 "开始创作"</p>
        </div>
      </div>
    );
  }
  return <div className="p-8 prose prose-zinc max-w-none">{content}</div>;
}
5.3 ActionTile StandardTypeScriptimport Link from "next/link";
export function ActionTile({ icon: Icon, title, description, href }: any) {
  return (
    <Link href={href} className="flex items-center gap-4 p-4 border border-hairline bg-surface hover:bg-zinc-50 transition-colors rounded-sm group">
       <div className="p-2 bg-zinc-100 rounded-sm group-hover:bg-white transition-colors">
         <Icon size={20} className="text-ink-primary" />
       </div>
       <div>
         <div className="text-sm font-medium text-ink-primary">{title}</div>
         <div className="text-xs text-ink-muted">{description}</div>
       </div>
    </Link>
  );
}