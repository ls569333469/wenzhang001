import { Bell, Search, PanelLeft, PanelRight, Home, Settings, PenTool, Sparkles, Plus, Command } from "lucide-react";

/**
 * Variant A: "Floating Islands" (The Athenaeum)
 * 核心理念: 悬浮、留白、层级
 * 适用场景: 强调思考和创作的高级感界面
 */
export default function VariantA() {
    return (
        <div className="min-h-screen bg-[#FAFAFA] text-zinc-900 font-sans selection:bg-zinc-900 selection:text-white relative overflow-hidden">

            {/* Background Grid Pattern (Subtle) */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }} />

            {/* 1. Floating Navbar */}
            <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50">
                <div className="flex items-center gap-1 p-1.5 bg-white rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.04)] border border-zinc-100 ring-1 ring-zinc-50">
                    <div className="px-4 py-2 bg-zinc-900 text-white rounded-full text-sm font-medium flex items-center gap-2 shadow-sm">
                        <Sparkles className="w-4 h-4" />
                        Studio
                    </div>
                    <button className="px-4 py-2 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 rounded-full text-sm font-medium transition-colors">
                        Knowledge
                    </button>
                    <button className="px-4 py-2 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50 rounded-full text-sm font-medium transition-colors">
                        Agents
                    </button>
                    <div className="w-px h-4 bg-zinc-200 mx-1" />
                    <button className="p-2 text-zinc-400 hover:text-zinc-900 rounded-full hover:bg-zinc-50 transition-colors">
                        <Search className="w-4 h-4" />
                    </button>
                </div>
            </nav>

            {/* 2. Floating Left Config (Island) */}
            <aside className="fixed left-6 top-24 bottom-6 w-80 bg-white rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-zinc-100 p-6 flex flex-col z-40">
                <h3 className="text-zinc-400 text-xs font-semibold uppercase tracking-wider mb-6">Configuration</h3>

                <div className="space-y-6">
                    <div className="space-y-3">
                        <label className="text-sm font-medium text-zinc-900">Mode</label>
                        <div className="p-1 bg-zinc-50 rounded-xl border border-zinc-100 flex">
                            <button className="flex-1 py-2 text-sm font-medium text-zinc-900 bg-white rounded-lg shadow-sm border border-zinc-200">Deep</button>
                            <button className="flex-1 py-2 text-sm font-medium text-zinc-500 hover:text-zinc-900">Summary</button>
                            <button className="flex-1 py-2 text-sm font-medium text-zinc-500 hover:text-zinc-900">Edit</button>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="text-sm font-medium text-zinc-900">Perspective</label>
                        <div className="space-y-2">
                            {['Professional', 'Academic', 'Opinionated'].map(item => (
                                <div key={item} className="flex items-center justify-between p-3 rounded-xl border border-zinc-100 hover:border-zinc-200 hover:bg-zinc-50 cursor-pointer group transition-all">
                                    <span className="text-sm text-zinc-600 group-hover:text-zinc-900">{item}</span>
                                    <div className="w-4 h-4 rounded-full border border-zinc-300 group-hover:border-zinc-900" />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </aside>

            {/* 3. Main Center Canvas */}
            <main className="absolute top-24 bottom-6 left-[23rem] right-[21rem] flex flex-col items-center">
                {/* Paper Sheet */}
                <div className="w-full max-w-2xl h-full bg-white rounded-xl shadow-sm border border-zinc-100/50 p-12 overflow-y-auto">
                    <h1 className="font-serif text-4xl font-medium text-zinc-900 mb-8 leading-tight">
                        The Future of Decentralized Intelligence
                    </h1>
                    <div className="space-y-4">
                        <div className="h-4 bg-zinc-100 rounded w-full" />
                        <div className="h-4 bg-zinc-100 rounded w-[90%]" />
                        <div className="h-4 bg-zinc-100 rounded w-[95%]" />
                        <div className="h-4 bg-zinc-100 rounded w-[80%]" />
                    </div>
                    <div className="mt-8 space-y-4">
                        <div className="h-4 bg-zinc-100 rounded w-full" />
                        <div className="h-4 bg-zinc-100 rounded w-full" />
                        <div className="h-4 bg-zinc-100 rounded w-[85%]" />
                    </div>
                </div>
            </main>

            {/* 4. Floating Right Agent (Island) */}
            <aside className="fixed right-6 top-24 bottom-6 w-72 bg-white rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-zinc-100 flex flex-col overflow-hidden z-40">
                <div className="p-4 border-b border-zinc-50 bg-zinc-50/30 backdrop-blur pb-3">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-zinc-900">Agent Flow</h3>
                        <span className="px-2 py-0.5 bg-green-100 text-green-700 text-[10px] font-bold uppercase rounded-full">Live</span>
                    </div>
                </div>
                <div className="flex-1 p-0 overflow-y-auto">
                    {['Understanding Intent', 'Retrieving Knowledge', 'Drafting Structure', 'Refining Style'].map((step, i) => (
                        <div key={i} className={`p-4 border-b border-zinc-50 flex gap-3 ${i === 1 ? 'bg-blue-50/50' : ''}`}>
                            <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${i === 1 ? 'bg-blue-500 animate-pulse' : i < 1 ? 'bg-zinc-900' : 'bg-zinc-200'}`} />
                            <div>
                                <div className="text-xs font-medium text-zinc-900">{step}</div>
                                <div className="text-[10px] text-zinc-400 mt-1">Agent-{101 + i}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </aside>

        </div>
    );
}
