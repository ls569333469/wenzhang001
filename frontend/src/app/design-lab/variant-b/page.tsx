import { LayoutGrid, Sidebar, Type, MessageSquare, GitBranch, MoreHorizontal, Settings } from "lucide-react";

/**
 * Variant B: "The Workbench" (Structuring)
 * 核心理念: 高效、紧凑、工具化
 * 适用场景: 专业级生产环境，最大化信息密度
 */
export default function VariantB() {
    return (
        <div className="min-h-screen bg-white text-zinc-900 font-sans flex overflow-hidden">

            {/* 1. Slim Icon Sidebar (Extreme Left) */}
            <div className="w-14 border-r border-zinc-200 flex flex-col items-center py-4 bg-zinc-50/50 z-20">
                <div className="w-8 h-8 bg-zinc-900 rounded-lg mb-6 shadow-sm" />
                <div className="space-y-4 flex-1 w-full flex flex-col items-center">
                    <NavIcon icon={LayoutGrid} active />
                    <NavIcon icon={Type} />
                    <NavIcon icon={GitBranch} />
                </div>
                <NavIcon icon={Settings} />
            </div>

            {/* 2. Structured Config Panel (Drawer) */}
            <div className="w-64 border-r border-zinc-200 bg-white flex flex-col z-10">
                <div className="h-14 border-b border-zinc-100 flex items-center px-4 font-semibold text-sm">
                    Project Settings
                </div>
                <div className="p-4 space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-500 uppercase">Input Mode</label>
                        <select className="w-full h-9 rounded-md border border-zinc-200 text-sm px-2 bg-zinc-50">
                            <option>Deep Research</option>
                        </select>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-500 uppercase">Parameters</label>
                        <div className="space-y-1">
                            <ParamRow label="Creativity" value="0.7" />
                            <ParamRow label="Token Limit" value="4k" />
                            <ParamRow label="Citations" value="On" />
                        </div>
                    </div>
                </div>
            </div>

            {/* 3. Main Editor Area */}
            <main className="flex-1 bg-zinc-50/30 flex flex-col relative">
                {/* Toolbar */}
                <div className="h-14 border-b border-zinc-200 bg-white flex items-center justify-between px-6">
                    <div className="flex items-center gap-2 text-sm text-zinc-500">
                        <span>Drafts</span>
                        <span>/</span>
                        <span className="text-zinc-900 font-medium">Untitled Research</span>
                    </div>
                    <button className="h-8 px-4 bg-zinc-900 text-white rounded text-sm font-medium hover:bg-zinc-800">
                        Run Simulation
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 p-8 overflow-y-auto">
                    <div className="max-w-3xl mx-auto bg-white min-h-[500px] border border-zinc-200 shadow-sm rounded-lg p-10">
                        <h1 className="text-3xl font-bold text-zinc-900 mb-4">Functional Specification</h1>
                        <p className="text-zinc-600 leading-relaxed">
                            This variant prioritizes structure and utility over whitespace. Boundaries are clearly defined by borders rather than shadows.
                            It feels like an IDE or a professional dashboard.
                        </p>
                    </div>
                </div>
            </main>

            {/* 4. Right Utility Panel */}
            <div className="w-72 border-l border-zinc-200 bg-white flex flex-col">
                <div className="h-14 border-b border-zinc-100 flex items-center px-4 font-semibold text-sm justify-between">
                    <span>Inspector</span>
                    <MoreHorizontal className="w-4 h-4 text-zinc-400" />
                </div>
                <div className="p-4">
                    <div className="bg-zinc-50 rounded border border-zinc-100 p-3 text-xs font-mono text-zinc-600">
                        System: Ready<br />
                        Latency: 24ms<br />
                        Tokens: 128
                    </div>
                </div>
            </div>

        </div>
    );
}

function NavIcon({ icon: Icon, active }: any) {
    return (
        <button className={`w-9 h-9 flex items-center justify-center rounded-md transition-colors ${active ? 'bg-zinc-200 text-zinc-900' : 'text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600'}`}>
            <Icon className="w-5 h-5" />
        </button>
    )
}

function ParamRow({ label, value }: any) {
    return (
        <div className="flex items-center justify-between p-2 rounded hover:bg-zinc-50 cursor-pointer">
            <span className="text-sm text-zinc-600">{label}</span>
            <span className="text-xs font-mono bg-zinc-100 px-1.5 py-0.5 rounded text-zinc-700">{value}</span>
        </div>
    )
}
