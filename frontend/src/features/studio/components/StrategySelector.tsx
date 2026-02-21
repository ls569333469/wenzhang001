
'use client';

import React from 'react';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { ArrowRight, Target, Lightbulb, Users } from 'lucide-react';
import { cn } from "@/lib/utils";
import { ContextPanel } from "./ContextPanel";
import { TitleSelector } from "./TitleSelector";
import { ViralScoreDisplay } from "./ViralScoreDisplay";

export function StrategySelector() {
    const {
        strategyOptions,
        confirmStrategy,
        // P10-1: Title AB Testing
        titleCandidates,
        selectedTitle,
        setSelectedTitle
    } = useAgentStore();

    if (!strategyOptions || strategyOptions.length === 0) return null;

    const handleConfirmStrategy = (option: any) => {
        // Pass selected title to confirmStrategy
        confirmStrategy(option, selectedTitle);
    };

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-500">
            <div className="text-center space-y-2">
                <h2 className="text-2xl font-serif font-bold text-ink-primary">
                    选择您的角度
                </h2>
                <p className="text-ink-muted">
                    策略师已识别出三个叙事方向，请选择标题和角度继续。
                </p>
            </div>

            {/* P10-1: Title Selector */}
            {titleCandidates && titleCandidates.length > 0 && (
                <div className="bg-white rounded-xl border border-zinc-200 p-4">
                    <TitleSelector
                        candidates={titleCandidates}
                        selectedTitle={selectedTitle}
                        onSelectTitle={setSelectedTitle}
                    />
                </div>
            )}

            {/* Context Panel (Data & Style) */}
            <ContextPanel />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {strategyOptions.map((option: any, idx: number) => (
                    <div
                        key={option.id || idx}
                        onClick={() => handleConfirmStrategy(option)}
                        className={cn(
                            "group relative overflow-hidden bg-white hover:bg-zinc-50 border-2 border-zinc-100 hover:border-zinc-900 rounded-xl p-6 cursor-pointer transition-all duration-300",
                            "hover:shadow-xl hover:-translate-y-1"
                        )}
                    >
                        {/* Header */}
                        <div className="mb-4 space-y-2">
                            <div className="flex items-center gap-2">
                                <span className="bg-zinc-100 text-zinc-600 text-xs font-mono px-2 py-0.5 rounded uppercase tracking-wider">
                                    方案 {idx + 1}
                                </span>
                            </div>
                            <h3 className="font-serif font-bold text-lg leading-tight text-ink-primary group-hover:text-black">
                                {option.title}
                            </h3>
                        </div>

                        {/* Details */}
                        <div className="space-y-3 text-sm text-ink-secondary">
                            <div className="flex items-start gap-2">
                                <Target className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                                <span>{option.pain_point}</span>
                            </div>
                            <div className="flex items-start gap-2">
                                <Users className="w-4 h-4 text-blue-500 shrink-0 mt-0.5" />
                                <span>{option.target_audience}</span>
                            </div>
                        </div>

                        {/* Outline Preview */}
                        <div className="mt-4 pt-4 border-t border-zinc-100">
                            <p className="text-xs font-semibold text-zinc-400 mb-2 uppercase">大纲预览</p>
                            <ul className="space-y-1">
                                {option.outline?.slice(0, 3).map((point: string, i: number) => (
                                    <li key={i} className="text-xs text-zinc-500 truncate flex items-center gap-1.5">
                                        <div className="w-1 h-1 rounded-full bg-zinc-300" />
                                        {point}
                                    </li>
                                ))}
                                {(option.outline?.length || 0) > 3 && (
                                    <li className="text-xs text-zinc-400 italic pl-2.5">
                                        + {(option.outline?.length || 0) - 3} 个更多...
                                    </li>
                                )}
                            </ul>
                        </div>

                        {/* P10-2: Viral Score Display */}
                        {option.viral_score && (
                            <div className="mt-4 pt-4 border-t border-zinc-100">
                                <ViralScoreDisplay score={option.viral_score} compact={false} />
                            </div>
                        )}

                        {/* Hover Action */}
                        <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0">
                            <div className="bg-zinc-900 text-white p-2 rounded-full shadow-lg">
                                <ArrowRight className="w-4 h-4" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

