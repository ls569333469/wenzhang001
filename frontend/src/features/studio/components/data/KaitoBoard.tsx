'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from "@/lib/utils";
import { AlertTriangle, Lightbulb, Newspaper } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

/**
 * KaitoBoard — Kaito 嘴撸模式数据面板
 * 
 * P2: 接真实 API，数据来源 Google Sheets 「嘴撸项目」+「嘴撸_{项目名}」Tab
 * 显示: 项目选择 + 推荐角度 + 最新情报 + 重复提醒
 */

interface KaitoProject {
    id: string;
    name: string;
    last_written: string;
}

interface Angle {
    id: string;
    title: string;
    desc: string;
}

interface NewsItem {
    id: string;
    title: string;
    source: string;
    time: string;
}

export function KaitoBoard() {
    const [projects, setProjects] = useState<KaitoProject[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
    const [angles, setAngles] = useState<Angle[]>([]);
    const [selectedAngles, setSelectedAngles] = useState<Set<string>>(new Set());
    const [news, setNews] = useState<NewsItem[]>([]);
    const [lastWritten, setLastWritten] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isLoadingIntel, setIsLoadingIntel] = useState<boolean>(false);

    // 拉取项目列表
    const fetchProjects = useCallback(async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/kaito/projects`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            const list: KaitoProject[] = data.projects || [];
            setProjects(list);
            // 默认选第一个
            if (list.length > 0 && !selectedProjectId) {
                setSelectedProjectId(list[0].id);
            }
        } catch (e) {
            console.error('[KaitoBoard] fetch projects failed:', e);
            setProjects([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // 拉取选中项目的情报
    const fetchIntel = useCallback(async (projectId: string) => {
        setIsLoadingIntel(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/data/kaito/${projectId}/intel`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setAngles(data.angles || []);
            setNews(data.news || []);
            setLastWritten(data.last_written || '');
            // 默认选第一个角度
            if (data.angles?.length > 0) {
                setSelectedAngles(new Set([data.angles[0].id]));
            } else {
                setSelectedAngles(new Set());
            }
        } catch (e) {
            console.error('[KaitoBoard] fetch intel failed:', e);
            setAngles([]);
            setNews([]);
        } finally {
            setIsLoadingIntel(false);
        }
    }, []);

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    useEffect(() => {
        if (selectedProjectId) {
            fetchIntel(selectedProjectId);
        }
    }, [selectedProjectId, fetchIntel]);

    const selectedProject = projects.find(p => p.id === selectedProjectId);

    const toggleAngle = (id: string) => {
        setSelectedAngles(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    return (
        <div className="flex flex-col h-full">
            {/* 标题 */}
            <div className="px-4 pt-4 pb-2">
                <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
                    <span className="text-lg">🎯</span>
                    项目看板
                </h3>
            </div>

            {/* 项目选择芯片 */}
            <div className="px-4 pb-3 flex flex-wrap gap-1.5">
                {isLoading ? (
                    Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="h-6 bg-zinc-100 rounded-full w-16 animate-pulse"></div>
                    ))
                ) : projects.length === 0 ? (
                    <p className="text-xs text-ink-muted">暂无项目数据</p>
                ) : (
                    projects.map(p => (
                        <button
                            key={p.id}
                            onClick={() => setSelectedProjectId(p.id)}
                            className={cn(
                                "px-3 py-1 text-xs font-medium rounded-full transition-all",
                                selectedProjectId === p.id
                                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                                    : "bg-white text-ink-muted border border-zinc-200 hover:border-zinc-300"
                            )}
                        >
                            {selectedProjectId === p.id && '✓ '}{p.name}
                        </button>
                    ))
                )}
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
                {isLoadingIntel ? (
                    <div className="space-y-6">
                        {/* 骨架屏：角度 */}
                        <section>
                            <div className="h-3.5 bg-zinc-200 rounded w-20 mb-3 animate-pulse"></div>
                            <div className="grid grid-cols-2 gap-2">
                                <div className="h-12 bg-zinc-100 rounded-lg animate-pulse"></div>
                                <div className="h-12 bg-zinc-100 rounded-lg animate-pulse"></div>
                                <div className="h-12 bg-zinc-100 rounded-lg animate-pulse"></div>
                                <div className="h-12 bg-zinc-100 rounded-lg animate-pulse"></div>
                            </div>
                        </section>
                        {/* 骨架屏：新闻 */}
                        <section>
                            <div className="h-3.5 bg-zinc-200 rounded w-20 mb-3 animate-pulse"></div>
                            <div className="space-y-2">
                                <div className="h-14 bg-zinc-100 rounded-lg animate-pulse"></div>
                                <div className="h-14 bg-zinc-100 rounded-lg animate-pulse"></div>
                                <div className="h-14 bg-zinc-100 rounded-lg animate-pulse"></div>
                            </div>
                        </section>
                    </div>
                ) : angles.length === 0 && news.length === 0 && !isLoading ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center text-ink-muted">
                        <span className="text-3xl mb-3 grayscale opacity-50">📭</span>
                        <p className="text-xs font-medium">该项目暂无数据源</p>
                        <p className="text-[10px] opacity-70 mt-1">请尝试切换其他项目</p>
                    </div>
                ) : (
                    <>
                        {/* 推荐角度 */}
                        {angles.length > 0 && (
                            <section>
                                <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                    <Lightbulb className="w-3.5 h-3.5" />
                                    推荐角度
                                </h4>
                                <div className="grid grid-cols-2 gap-2">
                                    {angles.map(a => (
                                        <button
                                            key={a.id}
                                            onClick={() => toggleAngle(a.id)}
                                            className={cn(
                                                "text-left px-3 py-2 rounded-lg border transition-all text-xs",
                                                selectedAngles.has(a.id)
                                                    ? "bg-blue-50 border-blue-200 text-blue-700"
                                                    : "bg-white border-zinc-200 text-ink-secondary hover:border-zinc-300"
                                            )}
                                        >
                                            <div className="font-medium">{selectedAngles.has(a.id) && '✓ '}{a.title}</div>
                                            <div className="text-[10px] text-ink-muted mt-0.5 leading-tight">{a.desc}</div>
                                        </button>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* 最新情报 */}
                        {news.length > 0 && (
                            <section>
                                <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                    <Newspaper className="w-3.5 h-3.5" />
                                    最新情报
                                </h4>
                                <div className="space-y-2">
                                    {news.map(n => (
                                        <div
                                            key={n.id}
                                            className="bg-white rounded-lg border border-zinc-200 p-2.5 hover:border-blue-300 transition-all cursor-pointer"
                                        >
                                            <p className="text-xs text-ink-primary leading-relaxed line-clamp-2">{n.title}</p>
                                            <div className="flex items-center gap-2 mt-1.5">
                                                <span className="text-[10px] text-ink-muted">{n.source}</span>
                                                <span className="text-[10px] text-ink-muted">· {n.time}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}

                        {/* 重复提醒 */}
                        {lastWritten && (
                            <section className="bg-amber-50 border border-amber-200 rounded-xl p-3">
                                <div className="flex items-start gap-2">
                                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                                    <div>
                                        <div className="text-xs font-medium text-amber-800">重复提醒</div>
                                        <div className="text-[10px] text-amber-600 mt-0.5 leading-relaxed">
                                            上次写 {selectedProject?.name || '该项目'} 是 {lastWritten}，注意避免内容重复
                                        </div>
                                    </div>
                                </div>
                            </section>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
