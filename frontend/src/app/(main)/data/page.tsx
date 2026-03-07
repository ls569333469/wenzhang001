'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Newspaper, FileBarChart, Database, Sparkles, FolderOpen } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ResearchArchive } from '@/features/data/ResearchArchive';
import { MaterialCenter } from '@/features/studio/components/MaterialCenter';
import KnowledgePage from '@/app/(main)/knowledge/page';

/**
 * P31: /data 数据中心
 * 4 Tab: 新闻素材 | 投研存档 | 批量入库 | 数据清洗
 */

const TABS = [
    { id: 'news', label: '新闻素材', icon: Newspaper },
    { id: 'research', label: '投研存档', icon: FileBarChart },
    { id: 'ingest', label: '批量入库', icon: Database },
    { id: 'clean', label: '数据清洗', icon: Sparkles },
] as const;

type TabId = typeof TABS[number]['id'];

export default function DataPage() {
    const searchParams = useSearchParams();
    const initialTab = (searchParams.get('tab') as TabId) || 'news';
    const [activeTab, setActiveTab] = useState<TabId>(initialTab);

    return (
        <div className="min-h-screen bg-paper">
            <div className="max-w-6xl mx-auto px-8 py-8 space-y-6">
                {/* Header */}
                <header className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-zinc-200 flex items-center justify-center">
                        <FolderOpen className="w-5 h-5 text-violet-600" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-serif font-medium text-ink-primary">数据中心</h1>
                        <p className="text-sm text-ink-muted">新闻素材 · 投研报告 · 数据采集</p>
                    </div>
                </header>

                {/* Tab Bar */}
                <div className="flex gap-1 bg-zinc-100 p-1 rounded-xl w-fit">
                    {TABS.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all",
                                activeTab === tab.id
                                    ? "bg-white text-ink-primary shadow-sm"
                                    : "text-ink-muted hover:text-ink-primary"
                            )}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                <div className="min-h-[60vh]">
                    {activeTab === 'news' && <MaterialCenter />}
                    {activeTab === 'research' && <ResearchArchive />}
                    {activeTab === 'ingest' && <KnowledgePage />}
                    {activeTab === 'clean' && (
                        <div className="text-center py-20 space-y-4">
                            <Sparkles className="w-12 h-12 mx-auto text-zinc-300" />
                            <p className="text-sm text-ink-muted">
                                数据清洗功能请访问 <a href="/cleaner" className="text-primary underline">独立页面</a>
                            </p>
                            <p className="text-xs text-ink-muted opacity-60">Phase 2 将迁移到此处</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
