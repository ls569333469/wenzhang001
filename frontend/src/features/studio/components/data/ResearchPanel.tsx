'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from "@/lib/utils";
import { Search, Briefcase, Coins } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

/**
 * ResearchPanel — 投研模式数据面板
 * 
 * P2: 接真实 API，数据来源 Google Sheets 「投研项目」Tab
 * 显示: 搜索框 + 有融资的 Web3 项目卡片
 */

interface ResearchProject {
    id: string;
    name: string;
    category: string;       // 赛道
    funding_round: string;  // 融资轮次
    funding_amount: string; // 融资金额
    investors: string;      // 投资方
    chain: string;          // 公链
    summary: string;        // 一句话摘要
}

export function ResearchPanel() {
    const [searchQuery, setSearchQuery] = useState('');
    const [projects, setProjects] = useState<ResearchProject[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const fetchProjects = useCallback(async (query: string) => {
        setIsLoading(true);
        try {
            const params = new URLSearchParams();
            if (query) params.set('q', query);
            const res = await fetch(`${API_BASE_URL}/api/data/research?${params}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setProjects(data.projects || []);
        } catch (e) {
            console.error('[ResearchPanel] fetch failed:', e);
            setProjects([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 初始加载全量 + 搜索防抖
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchProjects(searchQuery);
        }, searchQuery ? 400 : 0);
        return () => clearTimeout(timer);
    }, [searchQuery, fetchProjects]);

    return (
        <div className="flex flex-col h-full">
            {/* 标题 */}
            <div className="px-4 pt-4 pb-2">
                <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
                    <span className="text-lg">🔬</span>
                    投研项目
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
                        placeholder="搜索项目名称、赛道、公链..."
                        className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-zinc-200 bg-white focus:border-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-200 transition-all"
                    />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3">
                {isLoading ? (
                    // 骨架屏
                    <div className="space-y-3">
                        {Array.from({ length: 4 }).map((_, i) => (
                            <div key={i} className="bg-white rounded-xl border border-zinc-200 p-3 animate-pulse">
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="w-8 h-8 bg-zinc-200 rounded-lg"></div>
                                    <div className="flex-1">
                                        <div className="h-3.5 bg-zinc-200 rounded w-24 mb-1"></div>
                                        <div className="h-2.5 bg-zinc-100 rounded w-16"></div>
                                    </div>
                                </div>
                                <div className="h-3 bg-zinc-100 rounded w-full mt-2"></div>
                                <div className="h-3 bg-zinc-100 rounded w-3/4 mt-1"></div>
                            </div>
                        ))}
                    </div>
                ) : projects.length === 0 ? (
                    // 空状态
                    <div className="flex flex-col items-center justify-center h-48 text-center text-ink-muted">
                        <span className="text-3xl mb-3 grayscale opacity-50">🔍</span>
                        <p className="text-xs font-medium">
                            {searchQuery ? '未找到匹配项目' : '投研项目库暂无数据'}
                        </p>
                        <p className="text-[10px] opacity-70 mt-1">
                            {searchQuery ? '试试换个关键词' : '请在 Google Sheets「投研项目」Tab 中添加数据'}
                        </p>
                    </div>
                ) : (
                    // 项目卡片列表
                    projects.map(project => (
                        <div
                            key={project.id}
                            className="group bg-white rounded-xl border border-zinc-200 p-3 hover:border-emerald-300 hover:shadow-sm transition-all cursor-pointer"
                        >
                            {/* 项目头部 */}
                            <div className="flex items-center gap-2.5 mb-2">
                                <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center text-sm">
                                    💎
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-xs font-semibold text-ink-primary truncate">{project.name}</div>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        {project.category && (
                                            <span className="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded">
                                                {project.category}
                                            </span>
                                        )}
                                        {project.chain && (
                                            <span className="text-[10px] px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded">
                                                {project.chain}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* 融资信息 */}
                            {(project.funding_round || project.funding_amount) && (
                                <div className="flex items-center gap-2 mb-2">
                                    <Coins className="w-3 h-3 text-amber-500 shrink-0" />
                                    <span className="text-[11px] text-ink-secondary">
                                        {project.funding_round}{project.funding_round && project.funding_amount ? ' · ' : ''}{project.funding_amount}
                                    </span>
                                </div>
                            )}

                            {/* 投资方 */}
                            {project.investors && (
                                <div className="flex items-center gap-2 mb-2">
                                    <Briefcase className="w-3 h-3 text-zinc-400 shrink-0" />
                                    <span className="text-[10px] text-ink-muted truncate">{project.investors}</span>
                                </div>
                            )}

                            {/* 摘要 */}
                            {project.summary && (
                                <p className="text-[11px] text-ink-secondary leading-relaxed line-clamp-2 mt-1">
                                    {project.summary}
                                </p>
                            )}

                            {/* hover 操作 */}
                            <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <span className="text-[10px] text-emerald-600 font-medium">点击生成投研报告 →</span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* 数据来源 */}
            <div className="px-4 py-2 border-t border-zinc-100">
                <p className="text-[10px] text-ink-muted text-center">
                    📡 数据来源: Google Sheets「投研项目」
                </p>
            </div>
        </div>
    );
}
