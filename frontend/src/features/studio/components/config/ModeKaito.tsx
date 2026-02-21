'use client';

import React from 'react';
import { type LengthType } from '../../schema';
import { Clock, Target } from 'lucide-react';
import { cn } from "@/lib/utils";

/**
 * ModeKaito — Kaito 嘴撸模式配置
 * 
 * 风格锁定为嘴撸体，只显示篇幅控制
 */

interface ModeKaitoProps {
    lengthType: LengthType;
    setLengthType: (v: LengthType) => void;
    customLength: number;
    setCustomLength: (v: number) => void;
}

export function ModeKaito({ lengthType, setLengthType, customLength, setCustomLength }: ModeKaitoProps) {
    return (
        <>
            {/* 风格提示 — 锁定嘴撸体 */}
            <section className="space-y-2">
                <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
                    <Target className="w-3.5 h-3.5" />
                    写作风格
                </label>
                <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">🎯</span>
                        <div>
                            <div className="text-sm font-semibold text-blue-700">嘴撸体</div>
                            <div className="text-xs text-blue-500">项目解读 · Mindshare 提升</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 篇幅长度 */}
            <section className="space-y-3">
                <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
                    <Clock className="w-3.5 h-3.5" />
                    篇幅长度
                </label>
                <div className="flex items-center gap-2">
                    <div className="grid grid-cols-2 gap-2 flex-1">
                        <button
                            onClick={() => setLengthType('auto')}
                            className={cn(
                                "py-2 px-3 text-xs font-medium rounded-xl border transition-all",
                                lengthType === 'auto'
                                    ? "bg-zinc-900 text-white border-zinc-900 shadow-sm"
                                    : "bg-white text-ink-muted border-zinc-200 hover:border-zinc-300"
                            )}
                        >
                            默认 (50-500字)
                        </button>
                        <button
                            onClick={() => setLengthType('custom')}
                            className={cn(
                                "py-2 px-3 text-xs font-medium rounded-xl border transition-all",
                                lengthType === 'custom'
                                    ? "bg-zinc-900 text-white border-zinc-900 shadow-sm"
                                    : "bg-white text-ink-muted border-zinc-200 hover:border-zinc-300"
                            )}
                        >
                            自定义
                        </button>
                    </div>
                    {lengthType === 'custom' && (
                        <div className="flex items-center gap-1">
                            <input
                                type="number"
                                min={50}
                                max={500}
                                value={customLength || ''}
                                onChange={(e) => setCustomLength(parseInt(e.target.value) || 0)}
                                placeholder="200"
                                className="w-20 py-2 px-2 text-xs font-medium rounded-xl border border-zinc-200 focus:border-zinc-400 focus:outline-none text-center"
                            />
                            <span className="text-xs text-ink-muted">字</span>
                        </div>
                    )}
                </div>
            </section>
        </>
    );
}
