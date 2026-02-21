'use client';

import React, { useState, useEffect } from 'react';
import { cn } from "@/lib/utils";
import { AlertTriangle, Lightbulb, Newspaper } from 'lucide-react';

/**
 * KaitoBoard — Kaito 嘴撸模式数据面板
 * 
 * P1: Mock 数据版
 * 显示: 项目选择 + 推荐角度 + 最新情报 + 重复提醒
 */

const MOCK_PROJECTS = [
    { id: 'bera', name: 'Berachain', selected: true },
    { id: 'monad', name: 'Monad', selected: false },
    { id: 'sui', name: 'Sui', selected: false },
    { id: 'sei', name: 'Sei', selected: false },
    { id: 'celestia', name: 'Celestia', selected: false },
];

const MOCK_ANGLES = [
    { id: 'a1', title: '生态扩展', desc: 'DeFi 协议迁移趋势', selected: true },
    { id: 'a2', title: 'PoL 机制', desc: '流动性证明的创新', selected: false },
    { id: 'a3', title: '社区治理', desc: 'BGT 持有者权益', selected: false },
    { id: 'a4', title: 'TVL 增长', desc: '链上数据分析', selected: false },
];

const MOCK_NEWS = [
    { id: 'n1', title: 'Berachain 主网上线第一周 TVL 突破 $2B', time: '3h', source: 'DeFiLlama' },
    { id: 'n2', title: 'Infrared Finance 成为 Bera 最大 DeFi 协议', time: '6h', source: 'DeBank' },
    { id: 'n3', title: 'BGT 质押率达到 45%，远超预期', time: '12h', source: 'Dune' },
];

export function KaitoBoard() {
    const [projects, setProjects] = useState(MOCK_PROJECTS);
    const [angles, setAngles] = useState(MOCK_ANGLES);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const selectedProject = projects.find(p => p.selected);

    // 模拟选择项目后拉取数据
    useEffect(() => {
        setIsLoading(true);
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1000);
        return () => clearTimeout(timer);
    }, [selectedProject?.id]);

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
                {projects.map(p => (
                    <button
                        key={p.id}
                        onClick={() => setProjects(projects.map(pp => ({ ...pp, selected: pp.id === p.id })))}
                        className={cn(
                            "px-3 py-1 text-xs font-medium rounded-full transition-all",
                            p.selected
                                ? "bg-blue-100 text-blue-700 border border-blue-200"
                                : "bg-white text-ink-muted border border-zinc-200 hover:border-zinc-300"
                        )}
                    >
                        {p.selected && '✓ '}{p.name}
                    </button>
                ))}
            </div>

            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-4">
                {isLoading ? (
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
                ) : angles.length === 0 && MOCK_NEWS.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-48 text-center text-ink-muted">
                        <span className="text-3xl mb-3 grayscale opacity-50">📭</span>
                        <p className="text-xs font-medium">该项目暂无数据源</p>
                        <p className="text-[10px] opacity-70 mt-1">请尝试切换其他项目</p>
                    </div>
                ) : (
                    <>
                        {/* 推荐角度 */}
                        <section>
                            <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                <Lightbulb className="w-3.5 h-3.5" />
                                推荐角度
                            </h4>
                            <div className="grid grid-cols-2 gap-2">
                                {angles.map(a => (
                                    <button
                                        key={a.id}
                                        onClick={() => setAngles(angles.map(aa => aa.id === a.id ? { ...aa, selected: !aa.selected } : aa))}
                                        className={cn(
                                            "text-left px-3 py-2 rounded-lg border transition-all text-xs",
                                            a.selected
                                                ? "bg-blue-50 border-blue-200 text-blue-700"
                                                : "bg-white border-zinc-200 text-ink-secondary hover:border-zinc-300"
                                        )}
                                    >
                                        <div className="font-medium">{a.selected && '✓ '}{a.title}</div>
                                        <div className="text-[10px] text-ink-muted mt-0.5 leading-tight">{a.desc}</div>
                                    </button>
                                ))}
                            </div>
                        </section>

                        {/* 最新情报 */}
                        <section>
                            <h4 className="text-xs font-semibold text-ink-muted flex items-center gap-1.5 mb-2">
                                <Newspaper className="w-3.5 h-3.5" />
                                最新情报
                            </h4>
                            <div className="space-y-2">
                                {MOCK_NEWS.map(n => (
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

                        {/* 重复提醒 */}
                        <section className="bg-amber-50 border border-amber-200 rounded-xl p-3">
                            <div className="flex items-start gap-2">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                                <div>
                                    <div className="text-xs font-medium text-amber-800">重复提醒</div>
                                    <div className="text-[10px] text-amber-600 mt-0.5 leading-relaxed">
                                        上次写 {selectedProject?.name || '该项目'} 是 3 天前，注意避免内容重复
                                    </div>
                                </div>
                            </div>
                        </section>
                    </>
                )}
            </div>
        </div>
    );
}
