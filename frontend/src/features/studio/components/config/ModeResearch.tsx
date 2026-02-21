'use client';

import React, { useState } from 'react';
import { FileText, Zap } from 'lucide-react';
import { cn } from "@/lib/utils";

/**
 * ModeResearch — 投研模式配置
 * 
 * 显示: 输出格式选择（Alpha速报 / 完整报告）
 */

const OUTPUT_FORMATS = [
    { id: 'alpha', icon: '⚡', title: 'Alpha 速报', desc: '快速要点，适合推文分享' },
    { id: 'full_report', icon: '📊', title: '完整报告', desc: '深度分析，多维度数据' },
] as const;

type OutputFormat = typeof OUTPUT_FORMATS[number]['id'];

export function ModeResearch() {
    const [outputFormat, setOutputFormat] = useState<OutputFormat>('alpha');

    return (
        <>
            {/* 输出格式 */}
            <section className="space-y-3">
                <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
                    <FileText className="w-3.5 h-3.5" />
                    输出格式
                </label>
                <div className="grid grid-cols-1 gap-2">
                    {OUTPUT_FORMATS.map((f) => (
                        <button
                            key={f.id}
                            onClick={() => setOutputFormat(f.id)}
                            className={cn(
                                "relative text-left px-4 py-3 rounded-xl border transition-all",
                                outputFormat === f.id
                                    ? "bg-zinc-900 border-zinc-900 text-white shadow-md ring-1 ring-zinc-900/10"
                                    : "bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
                            )}
                        >
                            <div className="flex items-center gap-3">
                                <span className="text-lg">{f.icon}</span>
                                <div>
                                    <div className={cn(
                                        "font-semibold text-sm",
                                        outputFormat === f.id ? "text-white" : "text-ink-primary"
                                    )}>
                                        {f.title}
                                    </div>
                                    <div className={cn(
                                        "text-xs mt-0.5",
                                        outputFormat === f.id ? "text-zinc-400" : "text-ink-muted"
                                    )}>
                                        {f.desc}
                                    </div>
                                </div>
                            </div>
                            {outputFormat === f.id && (
                                <div className="absolute top-3 right-3 w-2 h-2 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                            )}
                        </button>
                    ))}
                </div>
            </section>
        </>
    );
}
