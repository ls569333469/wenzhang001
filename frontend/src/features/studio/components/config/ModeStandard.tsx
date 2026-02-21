'use client';

import React from 'react';
import { type LengthType, type WritingStyle } from '../../schema';
import { Clock, BookOpen } from 'lucide-react';
import { cn } from "@/lib/utils";
import { ALL_STYLES } from '@/lib/styles';
import { UI_TEXT } from '@/config/constants';

/**
 * ModeStandard — 普通模式配置（锐评/短篇/中篇/长篇/教程）
 * 
 * 显示: 写作风格选择 + 篇幅长度选择
 */

interface ModeStandardProps {
    style: string;
    setStyle: (v: string) => void;
    lengthType: LengthType;
    setLengthType: (v: LengthType) => void;
    customLength: number;
    setCustomLength: (v: number) => void;
}

export function ModeStandard({ style, setStyle, lengthType, setLengthType, customLength, setCustomLength }: ModeStandardProps) {
    return (
        <>
            {/* 篇幅长度 */}
            <section className="space-y-3">
                <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
                    <Clock className="w-3.5 h-3.5" />
                    {UI_TEXT.labels.length}
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
                            默认
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
                                max={5000}
                                value={customLength || ''}
                                onChange={(e) => setCustomLength(parseInt(e.target.value) || 0)}
                                placeholder="500"
                                className="w-20 py-2 px-2 text-xs font-medium rounded-xl border border-zinc-200 focus:border-zinc-400 focus:outline-none text-center"
                            />
                            <span className="text-xs text-ink-muted">字</span>
                        </div>
                    )}
                </div>
            </section>

            {/* 写作风格 */}
            <section className="space-y-3">
                <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
                    <BookOpen className="w-3.5 h-3.5" />
                    {UI_TEXT.labels.style}
                </label>
                <div className="grid grid-cols-2 gap-2">
                    {ALL_STYLES.map((s) => (
                        <StyleCard
                            key={s.id}
                            icon={s.icon}
                            title={s.name}
                            active={style === s.id}
                            color={s.color}
                            onClick={() => setStyle(s.id)}
                        />
                    ))}
                </div>
            </section>
        </>
    );
}

// StyleCard — 风格选择卡片
function StyleCard({ icon, title, active, color, onClick }: {
    icon: string; title: string; active: boolean; color: string; onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "relative flex items-center gap-3 p-3 rounded-xl border transition-all text-left group",
                active
                    ? "bg-white border-zinc-900 shadow-md ring-1 ring-zinc-100"
                    : "bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50/50"
            )}
        >
            <div className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center text-lg shadow-sm transition-transform group-hover:scale-105",
                active ? "bg-zinc-100" : "bg-zinc-50"
            )}>
                {icon}
            </div>
            <div className="flex-1">
                <div className={cn(
                    "text-xs font-semibold leading-tight",
                    active ? "text-ink-primary" : "text-ink-secondary"
                )}>
                    {title}
                </div>
                {active && (
                    <div className="h-0.5 w-6 mt-1 rounded-full" style={{ backgroundColor: color }} />
                )}
            </div>
        </button>
    );
}
