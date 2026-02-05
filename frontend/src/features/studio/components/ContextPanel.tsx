'use client';

import React from 'react';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { Target, Palette, Database, Sparkles, Clock, AlertTriangle, TrendingUp } from 'lucide-react';
import { cn } from "@/lib/utils";

export function ContextPanel() {
    const { analysisResult } = useAgentStore();

    if (!analysisResult) return null;

    const { info_anchors, style_notes, context_card } = analysisResult;

    // P20: Time context styling
    const timeContextStyle: Record<string, { label: string; color: string; bg: string }> = {
        'Today': { label: '今日热点', color: 'text-red-600', bg: 'bg-red-50 border-red-200' },
        'Recent': { label: '近期事件', color: 'text-amber-600', bg: 'bg-amber-50 border-amber-200' },
        'Historical': { label: '历史回顾', color: 'text-slate-600', bg: 'bg-slate-50 border-slate-200' },
        'Null': { label: '无时效性', color: 'text-zinc-500', bg: 'bg-zinc-50 border-zinc-200' }
    };

    return (
        <div className="w-full max-w-4xl mx-auto mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="bg-white/80 backdrop-blur-sm border border-zinc-200 rounded-xl p-6 shadow-sm space-y-4">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-5 h-5 text-indigo-500" />
                    <h3 className="font-serif font-bold text-lg text-zinc-800">深度分析上下文</h3>
                </div>

                {/* P20: Context Card Display */}
                {context_card && (
                    <div className={cn(
                        "rounded-lg border p-4 space-y-3 mb-4",
                        timeContextStyle[context_card.time_context]?.bg || 'bg-zinc-50 border-zinc-200'
                    )}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Clock className={cn("w-4 h-4", timeContextStyle[context_card.time_context]?.color || 'text-zinc-500')} />
                                <span className={cn("text-sm font-semibold", timeContextStyle[context_card.time_context]?.color || 'text-zinc-500')}>
                                    {timeContextStyle[context_card.time_context]?.label || context_card.time_context}
                                </span>
                            </div>
                            {context_card.has_event && (
                                <span className="flex items-center gap-1 text-xs text-red-500 bg-red-100 px-2 py-0.5 rounded-full">
                                    <AlertTriangle className="w-3 h-3" />
                                    爆发性事件
                                </span>
                            )}
                        </div>

                        <p className="text-sm text-zinc-700 leading-relaxed">
                            📝 {context_card.summary}
                        </p>

                        {context_card.forward_look && (
                            <div className="flex items-start gap-2 text-xs text-zinc-500 pt-2 border-t border-zinc-200/50">
                                <TrendingUp className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                                <span>后续展望: {context_card.forward_look}</span>
                            </div>
                        )}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Column 1: Anchors */}
                    <div className="space-y-4">
                        {/* Must Mention */}
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm font-semibold text-zinc-600">
                                <Target className="w-4 h-4 text-emerald-500" />
                                <span>必须提及要点</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {info_anchors.must_mention.map((item, i) => (
                                    <span key={i} className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-full text-xs font-medium">
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Key Data */}
                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-sm font-semibold text-zinc-600">
                                <Database className="w-4 h-4 text-blue-500" />
                                <span>提取的数据点</span>
                            </div>
                            <ul className="space-y-1">
                                {info_anchors.key_data.slice(0, 3).map((item, i) => (
                                    <li key={i} className="text-xs text-zinc-500 flex items-start gap-1.5">
                                        <div className="w-1 h-1 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                                        {item}
                                    </li>
                                ))}
                                {info_anchors.key_data.length > 3 && (
                                    <li className="text-xs text-zinc-400 italic pl-2.5">
                                        + {info_anchors.key_data.length - 3} 个更多要点...
                                    </li>
                                )}
                            </ul>
                        </div>
                    </div>

                    {/* Column 2: Style Notes */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-600">
                            <Palette className="w-4 h-4 text-purple-500" />
                            <span>风格指南</span>
                        </div>
                        <div className="bg-purple-50/50 border border-purple-100 rounded-lg p-3 relative">
                            {/* Quote Icon Background */}
                            <div className="absolute top-2 right-2 opacity-10">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="text-purple-900">
                                    <path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C19.5693 16 20.017 15.5523 20.017 15V9C20.017 8.44772 19.5693 8 19.017 8H15.017C14.4647 8 14.017 8.44772 14.017 9V11C14.017 11.5523 13.5693 12 13.017 12H12.017V5H22.017V15C22.017 18.3137 19.3307 21 16.017 21H14.017ZM5.0166 21L5.0166 18C5.0166 16.8954 5.91203 16 7.0166 16H10.0166C10.5689 16 11.0166 15.5523 11.0166 15V9C11.0166 8.44772 10.5689 8 10.0166 8H6.0166C5.46432 8 5.0166 8.44772 5.0166 9V11C5.0166 11.5523 4.56889 12 4.0166 12H3.0166V5H13.0166V15C13.0166 18.3137 10.3303 21 7.0166 21H5.0166Z" />
                                </svg>
                            </div>
                            <p className="text-sm text-purple-900/80 leading-relaxed font-medium italic">
                                &quot;{style_notes}&quot;
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

