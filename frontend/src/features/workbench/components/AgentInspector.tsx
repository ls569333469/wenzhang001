'use client';

import * as React from 'react';
import {
    Brain,
    Search,
    PenTool,
    Gavel,
    Terminal,
    ChevronRight,
    MoreHorizontal,
    Sparkles,
    CheckCircle2
} from 'lucide-react';
import { cn } from "@/lib/utils";

/**
 * AgentInspector: The "Right Brain" of the Quantum Trinity Layout.
 * Visualizes the AI's thought process (LangGraph State) and provides granular control.
 */
export function AgentInspector() {
    const [isCollapsed, setIsCollapsed] = React.useState(false);

    if (isCollapsed) {
        return (
            <aside className="w-[50px] border-l border-border bg-white flex flex-col items-center py-4">
                <button
                    onClick={() => setIsCollapsed(false)}
                    className="w-8 h-8 flex items-center justify-center rounded-sm hover:bg-zinc-100 text-zinc-400 hover:text-zinc-600 transition-colors"
                >
                    <Brain className="w-5 h-5 stroke-[1.5]" />
                </button>
            </aside>
        )
    }

    return (
        <aside className="w-full border-l border-zinc-200 bg-white/50 backdrop-blur-sm flex flex-col h-full flex-shrink-0 relative">

            {/* Header - Minimal */}
            <div className="h-10 border-b border-zinc-100 flex items-center justify-between px-4">
                <span className="text-[10px] font-medium text-zinc-400 uppercase tracking-widest">智能体</span>
                <div className="flex items-center gap-2">
                    <span className="relative flex h-1.5 w-1.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                    </span>
                    <button
                        onClick={() => setIsCollapsed(true)}
                        className="w-5 h-5 flex items-center justify-center rounded-sm hover:bg-zinc-100 text-zinc-300 hover:text-zinc-500 transition-colors"
                    >
                        <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            {/* Timeline Stream */}
            <div className="flex-1 overflow-y-auto p-5 space-y-8 scroll-smooth bg-white">
                <TimelineItem
                    agent="策略师"
                    status="completed"
                    time="2s"
                    desc="分析用户意图: '撰写一篇关于以太坊 L2 碎片化的深度分析'。"
                    icon={Brain}
                />
                <TimelineItem
                    agent="研究员"
                    status="completed"
                    time="4s"
                    desc="已检索上下文: 'optimism_superchain.md', 'arbitrum_orbit.md'。"
                    icon={Search}
                />
                <TimelineItem
                    agent="写作者"
                    status="active"
                    time="处理中..."
                    desc="正在起草第二部分: '互操作性的幻觉'。"
                    logs={[
                        "重点分析 '隔离性' 问题...",
                        "应用深度分析模式 (等级 0.8)..."
                    ]}
                    icon={PenTool}
                />

                {/* 待执行步骤 */}
                <div className="relative pl-5 opacity-40">
                    <div className="absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full border-2 border-white bg-zinc-200" />
                    <div className="flex items-center gap-2 mb-1 -mt-1">
                        <span className="text-xs font-bold text-zinc-400 font-serif">评审员</span>
                    </div>
                    <p className="text-[11px] text-zinc-400 font-serif italic">等待草稿完成...</p>
                </div>
            </div>

            {/* 终端 / 调试日志 */}
            <div className="h-1/3 min-h-[150px] border-t border-border bg-zinc-50/50 p-4 font-mono text-[10px] overflow-hidden flex flex-col">
                <div className="flex items-center justify-between text-zinc-400 mb-2 shrink-0">
                    <div className="flex items-center gap-2">
                        <Terminal className="w-3 h-3" />
                        <span className="uppercase tracking-wider font-semibold">系统日志</span>
                    </div>
                    <MoreHorizontal className="w-3 h-3 cursor-pointer hover:text-zinc-600 transition-colors" />
                </div>
                <div className="space-y-2 overflow-y-auto text-zinc-500 flex-1 no-scrollbar">
                    <p className="flex gap-2"><span className="text-zinc-400">➜</span> <span>[系统] 工作流已初始化: 72cb1a...</span></p>
                    <p className="flex gap-2"><span className="text-zinc-800 font-bold">✓</span> <span>[记忆] 已连接 3 个节点。</span></p>
                    <p className="flex gap-2"><span className="text-zinc-400">ℹ</span> <span>[配置] 写作者温度参数设为 0.7。</span></p>
                    <p className="flex gap-2 animate-pulse text-zinc-600"><span className="text-zinc-800">➜</span> <span>[流式] 正在接收 tokens...</span></p>
                </div>
            </div>

        </aside>
    );
}

function TimelineItem({ agent, status, time, desc, logs, icon: Icon }: any) {
    const isCompleted = status === 'completed'
    const isActive = status === 'active'

    return (
        <div className="relative pl-5 border-l border-zinc-100 last:border-0 pb-1">
            <div className={cn(
                "absolute -left-[5px] top-0 w-2.5 h-2.5 rounded-full border-2 border-white transition-colors duration-500",
                isCompleted ? 'bg-zinc-800' : isActive ? 'bg-zinc-400 animate-pulse' : 'bg-zinc-200'
            )} />

            <div className="flex items-center justify-between mb-1 -mt-1 group">
                <div className="flex items-center gap-2">
                    <span className={cn("text-xs font-bold tracking-tight transition-colors font-serif", isActive ? 'text-zinc-800' : 'text-zinc-600')}>{agent}</span>
                </div>
                <span className="text-[10px] text-zinc-400 font-mono group-hover:text-zinc-600 transition-colors">{time}</span>
            </div>

            <p className="text-sm text-zinc-600 leading-relaxed mb-3 font-serif">{desc}</p>

            {logs && (
                <div className="bg-zinc-50/80 rounded-sm border border-zinc-100 p-3 space-y-1.5 mt-2">
                    {logs.map((log: string, i: number) => (
                        <div key={i} className="flex items-start gap-2 text-[10px] text-zinc-500 font-mono">
                            <span className="text-zinc-300 mt-px">›</span>
                            <span>{log}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
