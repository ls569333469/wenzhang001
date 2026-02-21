'use client';

import React, { useState, useEffect } from 'react';
import { cn } from "@/lib/utils";
import { Search, TrendingUp, Database } from 'lucide-react';

/**
 * ResearchPanel — 投研模式数据面板
 * 
 * P1: Mock 数据版
 * 显示: 搜索框 + 数据源选择 + 市场概览
 */

const MOCK_DATA_SOURCES = [
    { id: 'coingecko', name: 'CoinGecko', enabled: true },
    { id: 'defillama', name: 'DeFiLlama', enabled: true },
    { id: 'dune', name: 'Dune Analytics', enabled: false },
    { id: 'messari', name: 'Messari', enabled: false },
];

const MOCK_MARKET = [
    { symbol: 'BTC', price: '$97,850', change: '+2.3%', up: true },
    { symbol: 'ETH', price: '$3,245', change: '+1.8%', up: true },
    { symbol: 'SOL', price: '$186', change: '-0.5%', up: false },
    { symbol: 'BNB', price: '$628', change: '+0.9%', up: true },
];

export function ResearchPanel() {
    const [searchQuery, setSearchQuery] = useState('');
    const [dataSources, setDataSources] = useState(MOCK_DATA_SOURCES);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // 模拟选择项目后拉取数据
    useEffect(() => {
        setIsLoading(true);
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 800);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const toggleSource = (id: string) => {
        setDataSources(dataSources.map(s =>
            s.id === id ? { ...s, enabled: !s.enabled } : s
        ));
    };

    return (
        <div className="flex flex-col h-full">
            {/* 标题 */}
            <div className="px-4 pt-4 pb-2">
                <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
                    <span className="text-lg">🔬</span>
                    研究数据
                </h3>
            </div>

            {/* 搜索框 */}
            <div className="px-4 pb-3">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-muted" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="搜索项目名称..."
                        className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-zinc-200 bg-white focus:border-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-200 transition-all"
                    />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
                {isLoading ? (
                    <div className="space-y-6">
                        {/* 骨架屏：数据源 */}
                        <section>
                            <div className="h-3.5 bg-zinc-200 rounded w-20 mb-3 animate-pulse"></div>
                            <div className="flex flex-wrap gap-2">
                                <div className="h-6 bg-zinc-100 rounded-full w-20 animate-pulse"></div>
                                <div className="h-6 bg-zinc-100 rounded-full w-24 animate-pulse"></div>
                                <div className="h-6 bg-zinc-100 rounded-full w-16 animate-pulse"></div>
                            </div>
                        </section>
                        {/* 骨架屏：市场概览 */}
                        <section>
                            <div className="h-3.5 bg-zinc-200 rounded w-20 mb-3 animate-pulse"></div>
                            <div className="bg-white rounded-xl border border-zinc-200 divide-y divide-zinc-100">
                                <div className="h-10 bg-zinc-50 animate-pulse"></div>
                                <div className="h-10 bg-zinc-50 animate-pulse"></div>
                                <div className="h-10 bg-zinc-50 animate-pulse"></div>
                                <div className="h-10 bg-zinc-50 animate-pulse"></div>
                            </div>
                        </section>
                    </div>
                ) : (
                    <>
                        {/* 数据源选择 */}
                        <section>
                            <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                <Database className="w-3.5 h-3.5" />
                                数据源
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                                {dataSources.map(s => (
                                    <button
                                        key={s.id}
                                        onClick={() => toggleSource(s.id)}
                                        className={cn(
                                            "px-3 py-1 text-xs font-medium rounded-full transition-all",
                                            s.enabled
                                                ? "bg-emerald-100 text-emerald-700 border border-emerald-200"
                                                : "bg-white text-ink-muted border border-zinc-200 hover:border-zinc-300"
                                        )}
                                    >
                                        {s.enabled && '✓ '}{s.name}
                                    </button>
                                ))}
                            </div>
                        </section>

                        {/* 市场概览 */}
                        <section>
                            <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                <TrendingUp className="w-3.5 h-3.5" />
                                市场概览
                            </h4>
                            <div className="bg-white rounded-xl border border-zinc-200 divide-y divide-zinc-100">
                                {MOCK_MARKET.map(m => (
                                    <div key={m.symbol} className="flex items-center justify-between px-3 py-2.5">
                                        <span className="text-xs font-semibold text-ink-primary">{m.symbol}</span>
                                        <div className="flex items-center gap-3">
                                            <span className="text-xs text-ink-secondary">{m.price}</span>
                                            <span className={cn(
                                                "text-xs font-medium",
                                                m.up ? "text-emerald-600" : "text-red-500"
                                            )}>
                                                {m.change}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {/* 空状态提示 */}
                        {!searchQuery && (
                            <div className="text-center py-6">
                                <div className="text-3xl mb-3 grayscale opacity-50">🔍</div>
                                <p className="text-xs font-medium text-ink-muted">输入项目名称开始研究全网数据</p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
