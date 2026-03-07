'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from "@/lib/utils";
import { Search, Telescope, Loader2, FileBarChart } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';
import { useResearchStore } from '@/features/research/useResearchStore';

/**
 * ResearchPanel — 投研模式 DataPanel
 * 
 * P31 v4: 侦察官搜索 + 项目卡片（可勾选）+ 生成日报
 */

interface ResearchProject {
    id: string;
    name: string;
    category: string;
    summary: string;
    // P32-B: 投研记录 Tab 字段
    twitter?: string;
    last_analyzed?: string;
    catalyst?: string;
    rating?: string;
    status?: string;
    scout_count?: number;
    // P31: 侦察官额外字段
    kol_24h?: number;
    buzz?: string;
    source?: 'sheets' | 'scout';
}

export function ResearchPanel() {
    const [searchQuery, setSearchQuery] = useState('');
    const [projects, setProjects] = useState<ResearchProject[]>([]);
    const [scoutProjects, setScoutProjects] = useState<ResearchProject[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isScoutLoading, setIsScoutLoading] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

    // 加载 Google Sheets 项目（已有）
    const fetchProjects = useCallback(async (query: string) => {
        setIsLoading(true);
        try {
            const params = new URLSearchParams();
            if (query) params.set('q', query);
            const res = await fetch(`${API_BASE_URL}/api/data/research?${params}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setProjects((data.projects || []).map((p: any) => ({ ...p, source: 'sheets' })));
        } catch (e) {
            console.error('[ResearchPanel] fetch failed:', e);
            setProjects([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 初始加载 + 搜索防抖
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchProjects(searchQuery);
        }, searchQuery ? 400 : 0);
        return () => clearTimeout(timer);
    }, [searchQuery, fetchProjects]);

    // P31: 侦察官搜索
    const handleScoutSearch = async () => {
        setIsScoutLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/research/scout`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            const scouts = (data.projects || []).map((p: any, i: number) => ({
                id: `scout_${i}_${p.name}`,
                name: p.name || '',
                twitter: p.twitter || '',
                category: p.category || '',
                kol_24h: p.kol_24h || 0,
                buzz: p.buzz || '',
                summary: p.buzz || '',
                source: 'scout' as const,
            }));
            setScoutProjects(scouts);
            // 默认全选侦察官项目
            setSelectedIds(new Set(scouts.map((p: ResearchProject) => p.id)));
        } catch (e) {
            console.error('[ResearchPanel] scout failed:', e);
        } finally {
            setIsScoutLoading(false);
        }
    };

    // P31: 勾选/取消项目
    const toggleSelect = (id: string) => {
        setSelectedIds(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    // P31: 生成日报
    const handleGenerateDaily = async () => {
        setIsGenerating(true);
        const { setGenerating, triggerRefresh } = useResearchStore.getState();
        setGenerating(true, '正在生成日报...');
        try {
            // 获取用户勾选的项目
            const allProjects = [...scoutProjects, ...projects];
            const selectedList = allProjects.filter(p => selectedIds.has(p.id));
            const selectedNames = selectedList.map(p => p.name);

            // 构建侦察官项目数据（传给后端避免重新搜索）
            const scoutData = selectedList
                .filter(p => p.source === 'scout')
                .map(p => ({
                    name: p.name,
                    twitter: p.twitter || '',
                    category: p.category || '',
                    kol_24h: p.kol_24h || 0,
                    buzz: p.buzz || '',
                }));

            const res = await fetch(`${API_BASE_URL}/api/research/daily-report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider: 'volcengine',
                    concurrency: 3,
                    selected_projects: selectedNames.length > 0 ? selectedNames : undefined,
                    scout_projects: scoutData.length > 0 ? scoutData : undefined,
                }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            console.log('[ResearchPanel] daily report:', data);
            // P31 P0: 触发 ResearchView 刷新
            setGenerating(false, '日报生成完成！');
            triggerRefresh();
        } catch (e) {
            console.error('[ResearchPanel] generate failed:', e);
            setGenerating(false, '生成失败，请重试');
        } finally {
            setIsGenerating(false);
        }
    };

    const allProjects = [...scoutProjects, ...projects];
    const selectedCount = selectedIds.size;

    return (
        <div className="flex flex-col h-full">
            {/* 标题 */}
            <div className="px-4 pt-4 pb-2">
                <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
                    <span className="text-lg">🔬</span>
                    投研项目
                </h3>
            </div>

            {/* P31: 侦察官搜索按钮 */}
            <div className="px-4 pb-2">
                <button
                    onClick={handleScoutSearch}
                    disabled={isScoutLoading}
                    className={cn(
                        "w-full flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all",
                        isScoutLoading
                            ? "bg-zinc-100 text-zinc-400 cursor-wait"
                            : "bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:shadow-lg hover:shadow-violet-600/20 hover:-translate-y-[1px]"
                    )}
                >
                    {isScoutLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Telescope className="w-4 h-4" />
                    )}
                    {isScoutLoading ? '搜索中...' : '🔭 侦察官搜索'}
                    <span className="ml-auto text-[10px] font-normal opacity-80">
                        {isScoutLoading ? '约 45 秒' : '搜索热门项目'}
                    </span>
                </button>
            </div>

            {/* 搜索框 */}
            <div className="px-4 pb-3">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-ink-muted" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="搜索项目名称、赛道..."
                        className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-zinc-200 bg-white focus:border-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-200 transition-all"
                    />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
                {/* 侦察官发现的项目 */}
                {scoutProjects.length > 0 && (
                    <>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-[10px] text-ink-muted uppercase tracking-wider">今日发现</span>
                            <span className="text-[10px] px-1.5 py-0.5 bg-violet-50 text-violet-600 rounded font-medium">
                                侦察官
                            </span>
                        </div>
                        {scoutProjects.map(project => (
                            <div
                                key={project.id}
                                onClick={() => toggleSelect(project.id)}
                                className={cn(
                                    "group bg-white rounded-xl border-[1.5px] p-3 cursor-pointer transition-all relative",
                                    selectedIds.has(project.id)
                                        ? "border-violet-400 bg-violet-50/50"
                                        : "border-zinc-200 hover:border-violet-300"
                                )}
                            >
                                {/* 勾选框 */}
                                <div className={cn(
                                    "absolute top-2.5 right-2.5 w-[18px] h-[18px] rounded-[5px] border-2 flex items-center justify-center text-[10px]",
                                    selectedIds.has(project.id)
                                        ? "bg-violet-600 border-violet-600 text-white"
                                        : "border-zinc-300"
                                )}>
                                    {selectedIds.has(project.id) && '✓'}
                                </div>

                                <div className="text-xs font-semibold text-ink-primary">{project.name}</div>
                                {project.twitter && (
                                    <div className="text-[11px] text-violet-600 mt-0.5">{project.twitter}</div>
                                )}
                                <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                                    {project.category && (
                                        <span className="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded">
                                            {project.category}
                                        </span>
                                    )}
                                    {project.kol_24h && project.kol_24h > 0 && (
                                        <span className="text-[10px] px-1.5 py-0.5 bg-amber-50 text-amber-600 rounded">
                                            KOL +{project.kol_24h}
                                        </span>
                                    )}
                                </div>
                                {project.buzz && (
                                    <p className="text-[11px] text-ink-secondary leading-relaxed mt-1.5 line-clamp-2">
                                        {project.buzz}
                                    </p>
                                )}
                            </div>
                        ))}
                    </>
                )}

                {/* Google Sheets 项目（历史/已有） */}
                {isLoading ? (
                    <div className="space-y-3">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="bg-white rounded-xl border border-zinc-200 p-3 animate-pulse">
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="w-8 h-8 bg-zinc-200 rounded-lg"></div>
                                    <div className="flex-1">
                                        <div className="h-3.5 bg-zinc-200 rounded w-24 mb-1"></div>
                                        <div className="h-2.5 bg-zinc-100 rounded w-16"></div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : projects.length > 0 ? (
                    <>
                        {scoutProjects.length > 0 && (
                            <div className="text-[10px] text-ink-muted uppercase tracking-wider mt-3 mb-1">
                                项目库
                            </div>
                        )}
                        {projects.map(project => (
                            <div
                                key={project.id}
                                onClick={() => toggleSelect(project.id)}
                                className={cn(
                                    "group bg-white rounded-xl border-[1.5px] p-3 cursor-pointer transition-all relative",
                                    selectedIds.has(project.id)
                                        ? "border-emerald-400 bg-emerald-50/50"
                                        : "border-zinc-200 hover:border-emerald-300"
                                )}
                            >
                                {/* 勾选指示器 */}
                                <div className={cn(
                                    "absolute top-2 right-2 w-4 h-4 rounded-full flex items-center justify-center text-[10px] transition-all",
                                    selectedIds.has(project.id)
                                        ? "bg-emerald-500 text-white"
                                        : "bg-zinc-200 text-transparent"
                                )}>
                                    ✓
                                </div>
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
                                            {project.rating && (
                                                <span className="text-[10px] px-1.5 py-0.5 bg-amber-50 text-amber-600 rounded font-medium">
                                                    ⭐ {project.rating}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                {project.catalyst && (
                                    <div className="flex items-center gap-1.5 mb-1.5 overflow-hidden">
                                        <span className="text-[10px] px-1.5 py-0.5 bg-red-50 text-red-600 rounded font-medium truncate max-w-full block">
                                            🔥 {project.catalyst}
                                        </span>
                                    </div>
                                )}
                                {project.summary && (
                                    <p className="text-[11px] text-ink-secondary leading-relaxed line-clamp-2 mt-1">
                                        {project.summary}
                                    </p>
                                )}
                                {project.last_analyzed && (
                                    <div className="text-[10px] text-ink-muted mt-1.5">
                                        📅 {project.last_analyzed}
                                    </div>
                                )}
                            </div>
                        ))}
                    </>
                ) : !scoutProjects.length ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center text-ink-muted">
                        <span className="text-3xl mb-3 grayscale opacity-50">🔍</span>
                        <p className="text-xs font-medium">
                            {searchQuery ? '未找到匹配项目' : '点击「🔭 侦察官搜索」发现热门项目'}
                        </p>
                        <p className="text-[10px] opacity-70 mt-1">
                            {searchQuery ? '试试换个关键词' : '或在 Google Sheets 中添加项目'}
                        </p>
                    </div>
                ) : null}
            </div>

            {/* P31: 底部操作栏 */}
            {(selectedCount > 0 || scoutProjects.length > 0) && (
                <div className="px-4 py-3 border-t border-zinc-100 flex items-center gap-3">
                    <span className="text-[11px] text-ink-muted whitespace-nowrap">
                        已选 {selectedCount} 个
                    </span>
                    <button
                        onClick={handleGenerateDaily}
                        disabled={selectedCount === 0 || isGenerating}
                        className={cn(
                            "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all",
                            selectedCount > 0 && !isGenerating
                                ? "bg-violet-600 text-white hover:bg-violet-700"
                                : "bg-zinc-100 text-zinc-400 cursor-not-allowed"
                        )}
                    >
                        {isGenerating ? (
                            <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                生成中...
                            </>
                        ) : (
                            <>
                                <FileBarChart className="w-4 h-4" />
                                📊 生成日报
                            </>
                        )}
                    </button>
                </div>
            )}

            {/* 数据来源 */}
            <div className="px-4 py-2 border-t border-zinc-100">
                <p className="text-[10px] text-ink-muted text-center">
                    📡 数据来源: {scoutProjects.length > 0 ? 'leak.me + ' : ''}Google Sheets
                </p>
            </div>
        </div>
    );
}
