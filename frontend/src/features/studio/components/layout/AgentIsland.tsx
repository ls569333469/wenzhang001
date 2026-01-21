'use client';

import { useState } from 'react';
import { IslandContainer } from "./IslandContainer";
import { Activity, Clock, FileText, Database } from "lucide-react";
import { AgentTimeline } from "../timeline/AgentTimeline";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";

type TabId = 'agent' | 'history' | 'outline' | 'materials';

interface Tab {
    id: TabId;
    label: string;
    icon: React.ReactNode;
}

const TABS: Tab[] = [
    { id: 'agent', label: '智能体', icon: <Activity className="w-3.5 h-3.5" /> },
    { id: 'history', label: '历史', icon: <Clock className="w-3.5 h-3.5" /> },
    { id: 'outline', label: '大纲', icon: <FileText className="w-3.5 h-3.5" /> },
    { id: 'materials', label: '素材', icon: <Database className="w-3.5 h-3.5" /> },
];

/**
 * AgentIsland - 右侧多功能工具栏
 * 
 * 标签:
 * 1. 智能体 - Agent 执行流程
 * 2. 历史 - 最近创作记录
 * 3. 大纲 - 当前文章结构 (占位符)
 * 4. 素材 - 知识库片段 (占位符)
 */
export function AgentIsland() {
    const [activeTab, setActiveTab] = useState<TabId>('agent');
    const { steps, status } = useAgentStore();
    const isActive = status === 'thinking' || status === 'writing' || status === 'connecting';

    return (
        <IslandContainer position="right">
            {/* Tab Bar */}
            <div className="flex items-center gap-1 p-2 border-b border-zinc-100 bg-zinc-50/50">
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={cn(
                            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                            activeTab === tab.id
                                ? "bg-white text-ink-primary shadow-sm border border-zinc-200"
                                : "text-ink-muted hover:text-ink-primary hover:bg-zinc-100"
                        )}
                    >
                        {tab.icon}
                        <span>{tab.label}</span>
                        {/* Active indicator for Agent tab */}
                        {tab.id === 'agent' && isActive && (
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                        )}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto">
                {activeTab === 'agent' && (
                    <div className="p-4">
                        <AgentTimeline steps={steps} />
                    </div>
                )}

                {activeTab === 'history' && (
                    <HistoryPanel />
                )}

                {activeTab === 'outline' && (
                    <PlaceholderPanel
                        icon={<FileText className="w-8 h-8" />}
                        title="大纲视图"
                        description="生成内容后，将在此显示文章结构大纲"
                    />
                )}

                {activeTab === 'materials' && (
                    <PlaceholderPanel
                        icon={<Database className="w-8 h-8" />}
                        title="素材面板"
                        description="分析完成后，将在此显示引用的知识库片段"
                    />
                )}
            </div>
        </IslandContainer>
    );
}

/**
 * HistoryPanel - 历史记录面板
 */
function HistoryPanel() {
    // TODO: 从 localStorage 或 API 获取真实历史
    const mockHistory = [
        { id: '1', title: 'DeFi 周报 2024-W03', date: '2小时前', status: 'draft' },
        { id: '2', title: 'Layer 2 深度分析', date: '昨天', status: 'completed' },
        { id: '3', title: 'Solana 生态观察', date: '3天前', status: 'completed' },
    ];

    return (
        <div className="p-4 space-y-3">
            <div className="text-xs font-semibold text-ink-muted uppercase tracking-wider mb-3">
                最近创作
            </div>
            {mockHistory.map((item) => (
                <button
                    key={item.id}
                    className="w-full text-left p-3 rounded-xl bg-zinc-50 hover:bg-zinc-100 transition-colors group"
                >
                    <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-ink-primary truncate group-hover:text-primary">
                                {item.title}
                            </div>
                            <div className="text-xs text-ink-muted mt-1">
                                {item.date}
                            </div>
                        </div>
                        <span className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-medium shrink-0",
                            item.status === 'draft'
                                ? "bg-amber-100 text-amber-700"
                                : "bg-emerald-100 text-emerald-700"
                        )}>
                            {item.status === 'draft' ? '草稿' : '已完成'}
                        </span>
                    </div>
                </button>
            ))}

            <div className="pt-2 border-t border-zinc-100">
                <button className="w-full text-center text-xs text-ink-muted hover:text-primary py-2">
                    查看全部历史 →
                </button>
            </div>
        </div>
    );
}

/**
 * PlaceholderPanel - 占位符面板
 */
function PlaceholderPanel({
    icon,
    title,
    description
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
}) {
    return (
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <div className="text-zinc-300 mb-4">
                {icon}
            </div>
            <div className="text-sm font-medium text-ink-secondary mb-2">
                {title}
            </div>
            <div className="text-xs text-ink-muted max-w-[200px]">
                {description}
            </div>
        </div>
    );
}
