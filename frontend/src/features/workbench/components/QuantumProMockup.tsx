import React from 'react';
import {
    Zap, Command, Search, Settings,
    LayoutTemplate, FileText, Sparkles,
    Brain, PenTool, Gavel, CheckCircle2,
    Terminal, ChevronRight, MORE_HORIZONTAL,
    Play, Pause, RotateCcw, Share2,
    MoreHorizontal, CornerDownLeft, Maximize2
} from 'lucide-react';

/**
 * Quantum Studio Pro (v5.1) - Design Vision Mockup
 * Theme: "Dark Glass" / Linear-inspired
 * Tech: Tailwind CSS v3 (compatible with current stack)
 */
export default function QuantumProMockup() {
    return (
        <div className="min-h-screen bg-black text-zinc-300 font-sans selection:bg-white selection:text-black overflow-hidden flex flex-col font-mono">

            {/* --- HEADER --- */}
            <header className="h-10 border-b border-white/10 bg-black flex items-center justify-between px-4 z-20 shrink-0">
                <div className="flex items-center gap-4">
                    <span className="text-sm font-bold text-white tracking-tight uppercase">Quantum Studio</span>
                    <div className="h-3 w-px bg-white/20" />
                    <span className="text-[10px] text-zinc-500 font-mono">v5.1.0-RC1</span>
                </div>

                <div className="flex items-center gap-6">
                    <span className="text-[10px] text-zinc-600 font-medium cursor-pointer hover:text-zinc-300 transition-colors">DOCS</span>
                    <span className="text-[10px] text-zinc-600 font-medium cursor-pointer hover:text-zinc-300 transition-colors">SETTINGS</span>
                    <div className="w-5 h-5 bg-white text-black text-[10px] font-bold flex items-center justify-center">
                        QS
                    </div>
                </div>
            </header>

            {/* --- MAIN LAYOUT --- */}
            <main className="flex-1 flex overflow-hidden z-10">

                {/* 1. SIDEBAR (CONTEXT) */}
                <aside className="w-64 border-r border-white/10 bg-black flex flex-col pt-4">
                    <div className="px-4 mb-8">
                        <SectionHeader title="Projects" />
                        <div className="flex flex-col gap-1 mt-2">
                            <NavItem label="Manifesto.md" active />
                            <NavItem label="Protocol_Specs.md" />
                            <NavItem label="Deployment_Guide.md" />
                        </div>
                    </div>

                    <div className="px-4">
                        <SectionHeader title="Configuration" />
                        <div className="flex flex-col gap-1 mt-2">
                            <ConfigRow label="Model" value="GPT-4o" />
                            <ConfigRow label="Output" value="Standard" />
                            <ConfigRow label="Tone" value="Academic" />
                        </div>
                    </div>

                    <div className="mt-auto p-4 border-t border-white/10">
                        <div className="flex justify-between items-center text-[10px] font-mono text-zinc-500">
                            <span>TOKENS</span>
                            <span>4,230 / 10,000</span>
                        </div>
                    </div>
                </aside>

                {/* 2. CENTER CANVAS (STAGE) */}
                <section className="flex-1 flex flex-col bg-black relative border-r border-white/10">

                    {/* Toolbar */}
                    <div className="h-10 border-b border-white/10 flex items-center justify-between px-6 bg-black sticky top-0 z-10">
                        <div className="flex items-center gap-4 text-[10px] font-mono text-zinc-500">
                            <span>Last edited: 2m ago</span>
                            <span>|</span>
                            <span>1,245 words</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <button className="text-[10px] font-bold text-white hover:underline uppercase">Export</button>
                            <button className="text-[10px] font-bold text-white hover:underline uppercase">Publish</button>
                        </div>
                    </div>

                    {/* Editor Area */}
                    <div className="flex-1 overflow-y-auto px-12 py-12">
                        <div className="max-w-2xl mx-auto space-y-8">
                            <h1 className="text-3xl font-bold tracking-tight text-white mb-8 border-b border-white/10 pb-4">
                                On Decentralized Publishing
                            </h1>
                            <div className="prose prose-invert prose-zinc max-w-none text-sm font-serif leading-relaxed text-zinc-300">
                                <p>
                                    The architecture of decentralized systems requires a fundamental rethink of content ownership.
                                    Traditional platforms act as gatekeepers, whereas Web3 protocols introduce permanence and direct attribution.
                                </p>
                                <p className="mt-4">
                                    We are moving towards a model where the text itself is an asset, immutable and sovereign.
                                    The implications for censorship resistance and economic models are profound.
                                </p>
                                <blockquote className="pl-4 border-l-2 border-white text-zinc-400 italic font-sans my-6 text-xs">
                                    "Code is law, but content is culture."
                                </blockquote>
                                <p>
                                    By utilizing distributed ledgers, a writer can establish a verifiable proof of existence...
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Minimal Input */}
                    <div className="absolute bottom-0 w-full border-t border-white/10 bg-black p-4">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-white animate-pulse" />
                            <input
                                className="bg-transparent border-none outline-none text-xs font-mono text-white w-full placeholder:text-zinc-700"
                                placeholder="COMMAND: Optimize for clarity..."
                            />
                        </div>
                    </div>

                </section>

                {/* 3. INSPECTOR (LOGS) */}
                <aside className="w-72 bg-black flex flex-col">
                    <div className="h-10 border-b border-white/10 flex items-center px-4 bg-black">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">System Activity</span>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 font-mono text-[10px] space-y-4">
                        <LogItem time="10:42:01" source="SYSTEM" msg="Context initialized." />
                        <LogItem time="10:42:05" source="ARCHITECT" msg="Analyzing structure..." />
                        <LogItem time="10:42:06" source="ARCHITECT" msg="Detected 3 key arguments." highlight />
                        <LogItem time="10:42:12" source="WRITER" msg="Drafting paragraph 2." />
                    </div>
                </aside>

            </main>
        </div>
    );
}

/* --- SUB COMPONENTS FOR MOCKUP --- */

function SectionHeader({ title }: { title: string }) {
    return (
        <div className="mb-2">
            <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">{title}</span>
        </div>
    )
}

function NavItem({ label, active }: { label: string, active?: boolean }) {
    return (
        <div className={`
           px-2 py-1 text-xs cursor-pointer border-l-2 transition-colors
           ${active ? 'border-white text-white' : 'border-transparent text-zinc-500 hover:text-zinc-300'}
        `}>
            {label}
        </div>
    )
}

function ConfigRow({ label, value }: { label: string, value: string }) {
    return (
        <div className="flex justify-between items-center py-1 px-2 text-xs text-zinc-400 border-b border-white/5 last:border-0">
            <span>{label}</span>
            <span className="text-zinc-200">{value}</span>
        </div>
    )
}

function LogItem({ time, source, msg, highlight }: any) {
    return (
        <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-2 opacity-50">
                <span>{time}</span>
                <span>[{source}]</span>
            </div>
            <span className={highlight ? 'text-white' : 'text-zinc-500'}>{msg}</span>
        </div>
    )
}
