'use client';

import { useState, createContext, useContext, ReactNode } from 'react';
import { X, Brain, Clock, ImageIcon, Download, Copy, FileDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { toast } from 'sonner';

// --- Context for global panel state ---
interface DetailPanelContextType {
    isOpen: boolean;
    activeTab: DetailTabId;
    openPanel: (tab?: DetailTabId) => void;
    closePanel: () => void;
    switchTab: (tab: DetailTabId) => void;
}

const DetailPanelContext = createContext<DetailPanelContextType | null>(null);

export function useDetailPanel() {
    const ctx = useContext(DetailPanelContext);
    if (!ctx) throw new Error('useDetailPanel must be used within DetailPanelProvider');
    return ctx;
}

// --- Types ---
type DetailTabId = 'thinking' | 'history' | 'image' | 'export';

interface DetailTab {
    id: DetailTabId;
    label: string;
    icon: ReactNode;
}

const DETAIL_TABS: DetailTab[] = [
    { id: 'thinking', label: '思维链', icon: <Brain className="w-4 h-4" /> },
    { id: 'history', label: '历史', icon: <Clock className="w-4 h-4" /> },
    { id: 'image', label: '配图', icon: <ImageIcon className="w-4 h-4" /> },
    { id: 'export', label: '导出', icon: <Download className="w-4 h-4" /> },
];

// --- Provider ---
export function DetailPanelProvider({ children }: { children: ReactNode }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState<DetailTabId>('thinking');

    const openPanel = (tab?: DetailTabId) => {
        if (tab) setActiveTab(tab);
        setIsOpen(true);
    };

    const closePanel = () => setIsOpen(false);
    const switchTab = (tab: DetailTabId) => setActiveTab(tab);

    return (
        <DetailPanelContext.Provider value={{ isOpen, activeTab, openPanel, closePanel, switchTab }}>
            {children}
        </DetailPanelContext.Provider>
    );
}

// --- Main Panel Component ---
export function DetailPanel() {
    const { isOpen, activeTab, closePanel, switchTab } = useDetailPanel();

    if (!isOpen) return null;

    return (
        <div className={cn(
            "fixed top-0 right-0 h-full w-[420px] bg-white shadow-2xl z-50",
            "flex flex-col border-l border-zinc-200",
            "animate-in slide-in-from-right duration-300"
        )}>
            {/* Header with tabs */}
            <div className="flex items-center gap-1 px-3 py-2 border-b border-zinc-100 bg-zinc-50/80">
                {DETAIL_TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => switchTab(tab.id)}
                        className={cn(
                            "flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all",
                            activeTab === tab.id
                                ? "bg-white text-ink-primary shadow-sm border border-zinc-200"
                                : "text-ink-muted hover:text-ink-primary hover:bg-white/50"
                        )}
                    >
                        {tab.icon}
                        <span>{tab.label}</span>
                    </button>
                ))}

                <button
                    onClick={closePanel}
                    className="ml-auto p-2 rounded-lg text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100"
                >
                    <X className="w-4 h-4" />
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto">
                {activeTab === 'thinking' && <ThinkingTab />}
                {activeTab === 'history' && <HistoryTab />}
                {activeTab === 'image' && <ImageTab />}
                {activeTab === 'export' && <ExportTab />}
            </div>

            {/* Footer quick actions */}
            <div className="p-3 border-t border-zinc-100 bg-zinc-50/50">
                <div className="flex gap-2">
                    <button className="flex-1 py-2 px-3 text-xs font-medium text-zinc-600 bg-white border border-zinc-200 rounded-lg hover:bg-zinc-50">
                        📝 继续上次
                    </button>
                    <button className="flex-1 py-2 px-3 text-xs font-medium text-zinc-600 bg-white border border-zinc-200 rounded-lg hover:bg-zinc-50">
                        🔄 重新生成
                    </button>
                </div>
            </div>
        </div>
    );
}

// --- Tab Content Components ---

function ThinkingTab() {
    const { agentLogs } = useAgentStore();

    // Extract thinking content from logs (look for <think> tags)
    const thinkingContent = agentLogs.find(log => log.includes('<think>')) || '';

    return (
        <div className="p-4 space-y-4">
            <div className="text-xs font-semibold text-green-600 uppercase tracking-wider flex items-center gap-2">
                <Brain className="w-3.5 h-3.5" />
                策略师思维链
            </div>

            <div className="bg-zinc-900 rounded-xl p-4 font-mono text-sm leading-relaxed overflow-x-auto">
                {thinkingContent ? (
                    <pre className="text-zinc-300 whitespace-pre-wrap">
                        <span className="text-green-400">&lt;think&gt;</span>
                        {'\n'}
                        {thinkingContent.replace(/<\/?think>/g, '').trim() || '思考过程记录中...'}
                        {'\n'}
                        <span className="text-green-400">&lt;/think&gt;</span>
                    </pre>
                ) : (
                    <div className="text-zinc-500 text-center py-8">
                        开始创作后，将在此显示 AI 的思考过程
                    </div>
                )}
            </div>

            {/* Agent logs preview */}
            {agentLogs.length > 0 && (
                <div className="space-y-2">
                    <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                        执行日志
                    </div>
                    <div className="max-h-40 overflow-y-auto space-y-1 text-xs font-mono text-zinc-500">
                        {agentLogs.slice(-10).map((log, i) => (
                            <div key={i} className="py-1 border-b border-zinc-100 last:border-0">
                                {log}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function HistoryTab() {
    // TODO: Replace with real history from localStorage or API
    const mockHistory = [
        { id: '1', title: 'DeFi 周报 2024-W03', date: '2小时前', status: 'draft' },
        { id: '2', title: 'Layer 2 深度分析', date: '昨天', status: 'completed' },
        { id: '3', title: 'Solana 生态观察', date: '3天前', status: 'completed' },
        { id: '4', title: '比特币 ETF 解读', date: '1周前', status: 'completed' },
    ];

    return (
        <div className="p-4 space-y-3">
            <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                最近创作
            </div>

            {mockHistory.map((item) => (
                <button
                    key={item.id}
                    className="w-full text-left p-3 rounded-xl bg-zinc-50 hover:bg-zinc-100 transition-all hover:translate-x-1 group"
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

            <button className="w-full text-center text-xs text-ink-muted hover:text-primary py-3 border-t border-zinc-100 mt-2">
                查看全部历史 →
            </button>
        </div>
    );
}

function ImageTab() {
    return (
        <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <div className="w-16 h-16 rounded-2xl bg-zinc-100 flex items-center justify-center mb-4">
                <ImageIcon className="w-8 h-8 text-zinc-400" />
            </div>
            <div className="text-base font-medium text-ink-secondary mb-2">
                AI 配图生成
            </div>
            <div className="text-sm text-ink-muted max-w-[250px] mb-6">
                根据文章内容智能生成配图，提升传播力
            </div>
            <button className="px-6 py-2.5 bg-zinc-900 text-white rounded-xl text-sm font-medium hover:bg-zinc-800 transition-colors">
                生成配图
            </button>
        </div>
    );
}

function ExportTab() {
    const { content } = useAgentStore();

    const handleCopy = () => {
        if (content) {
            navigator.clipboard.writeText(content);
            toast.success('已复制到剪贴板');
        }
    };

    const handleExportMarkdown = () => {
        if (!content) {
            toast.error('暂无内容可导出');
            return;
        }
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `article_${Date.now()}.md`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success('已导出 Markdown 文件');
    };

    const handleExportHTML = () => {
        if (!content) {
            toast.error('暂无内容可导出');
            return;
        }
        // Simple markdown to HTML (basic)
        const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Article</title>
<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:20px;line-height:1.6}</style>
</head><body>${content.replace(/\n/g, '<br>')}</body></html>`;
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `article_${Date.now()}.html`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success('已导出 HTML 文件');
    };

    return (
        <div className="p-4 space-y-6">
            <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
                导出选项
            </div>

            <div className="grid gap-3">
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-3 p-4 bg-zinc-50 hover:bg-zinc-100 rounded-xl transition-colors text-left"
                >
                    <div className="w-10 h-10 rounded-lg bg-white border border-zinc-200 flex items-center justify-center">
                        <Copy className="w-5 h-5 text-zinc-600" />
                    </div>
                    <div>
                        <div className="text-sm font-medium text-ink-primary">复制内容</div>
                        <div className="text-xs text-ink-muted">复制到剪贴板</div>
                    </div>
                </button>

                <button
                    onClick={handleExportMarkdown}
                    className="flex items-center gap-3 p-4 bg-zinc-50 hover:bg-zinc-100 rounded-xl transition-colors text-left"
                >
                    <div className="w-10 h-10 rounded-lg bg-white border border-zinc-200 flex items-center justify-center">
                        <FileDown className="w-5 h-5 text-zinc-600" />
                    </div>
                    <div>
                        <div className="text-sm font-medium text-ink-primary">导出 Markdown</div>
                        <div className="text-xs text-ink-muted">下载 .md 文件</div>
                    </div>
                </button>

                <button
                    onClick={handleExportHTML}
                    className="flex items-center gap-3 p-4 bg-zinc-50 hover:bg-zinc-100 rounded-xl transition-colors text-left"
                >
                    <div className="w-10 h-10 rounded-lg bg-white border border-zinc-200 flex items-center justify-center">
                        <FileDown className="w-5 h-5 text-zinc-600" />
                    </div>
                    <div>
                        <div className="text-sm font-medium text-ink-primary">导出 HTML</div>
                        <div className="text-xs text-ink-muted">下载 .html 文件</div>
                    </div>
                </button>
            </div>
        </div>
    );
}
