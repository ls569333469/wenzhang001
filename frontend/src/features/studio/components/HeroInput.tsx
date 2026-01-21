'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useQueryState, parseAsFloat } from 'nuqs';
import { Play, Sparkles, FileText, Palette, ChevronDown } from 'lucide-react';
import { cn } from "@/lib/utils";
import { useAgentStore, mapStatusToPhase } from '@/features/agent/stores/useAgentStore';
import { UI_TEXT, CREATION_MODES } from '@/config/constants';
import { ALL_STYLES } from '@/lib/styles';
import {
    CreationModeSchema,
    WritingStyleSchema,
    ArticleLengthSchema,
    defaultConfig
} from '@/features/studio/schema';

/**
 * HeroInput - P10-9 Phase-Aware Input Component
 * 
 * Idle Mode: Centered with quick config shortcuts
 * Active Mode: Compact in layout
 */
export function HeroInput() {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [input, setInput] = useState('');
    const { startSession, status } = useAgentStore();
    const phase = mapStatusToPhase(status);
    const isRunning = status === 'thinking' || status === 'listening' || status === 'connecting';
    const isIdle = phase === 'idle';

    // === Read Config from URL (Source of Truth) ===
    const [mode, setMode] = useQueryState('mode', {
        defaultValue: defaultConfig.mode,
        parse: (v) => CreationModeSchema.safeParse(v).success ? v : defaultConfig.mode
    });
    const [style, setStyle] = useQueryState('style', {
        defaultValue: defaultConfig.style,
        parse: (v) => WritingStyleSchema.safeParse(v).success ? v : defaultConfig.style
    });
    const [length] = useQueryState('length', {
        defaultValue: defaultConfig.length,
        parse: (v) => ArticleLengthSchema.safeParse(v).success ? v : defaultConfig.length
    });
    const [temp] = useQueryState('temp', parseAsFloat.withDefault(defaultConfig.temperature));
    const [topP] = useQueryState('topP', parseAsFloat.withDefault(0.9));
    const [maxTokens] = useQueryState('maxTokens', parseAsFloat.withDefault(4096));
    const [knowledgeIds] = useQueryState('knowledge', {
        defaultValue: ['auto'],
        parse: (v) => v ? v.split(',') : ['auto']
    });

    // Get current mode and style display names
    const currentMode = CREATION_MODES.find(m => m.id === mode);
    const currentStyle = ALL_STYLES.find(s => s.id === style);

    // Quick mode options for dropdown
    const quickModes = CREATION_MODES.filter(m => !m.compact).slice(0, 3);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [input]);

    const handleStart = () => {
        if (!input.trim()) return;

        startSession({
            input: input.trim(),
            config: {
                mode,
                style,
                length,
                temperature: temp,
                knowledgeSources: knowledgeIds,
                topP,
                maxTokens
            } as any
        });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            handleStart();
        }
    };

    return (
        <div className={cn(
            "w-full transition-all duration-500",
            isIdle ? "max-w-2xl mx-auto" : "max-w-full"
        )}>
            {/* Main Input Card */}
            <div className={cn(
                "relative group bg-white rounded-2xl shadow-xl shadow-zinc-200/50 border border-zinc-100 transition-all duration-300",
                "focus-within:shadow-2xl focus-within:shadow-primary/5 focus-within:border-primary/20",
                "hover:shadow-2xl hover:shadow-zinc-200/80"
            )}>

                {/* Textarea */}
                <div className="p-2">
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={UI_TEXT?.inputPlaceholder || "输入您的研究主题或指令..."}
                        className="w-full h-[80px] bg-transparent border-none outline-none focus:ring-0 focus:outline-none text-lg text-ink-primary placeholder:text-zinc-300 resize-none py-3 px-4 font-sans leading-relaxed"
                        autoFocus
                    />
                </div>

                {/* P10-9: Quick Config Shortcuts (Only in Idle Mode) */}
                {isIdle && (
                    <div className="flex items-center gap-2 px-4 pb-2">
                        {/* Mode Selector */}
                        <div className="relative group/dropdown">
                            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-50 hover:bg-zinc-100 rounded-lg text-xs font-medium text-zinc-600 transition-colors">
                                <FileText className="w-3.5 h-3.5" />
                                <span>{currentMode?.title || '深度分析'}</span>
                                <ChevronDown className="w-3 h-3 text-zinc-400" />
                            </button>
                            {/* Dropdown */}
                            <div className="absolute top-full left-0 mt-1 py-1 bg-white border border-zinc-200 rounded-lg shadow-lg opacity-0 invisible group-hover/dropdown:opacity-100 group-hover/dropdown:visible transition-all z-50 min-w-[160px]">
                                {quickModes.map(m => (
                                    <button
                                        key={m.id}
                                        onClick={() => setMode(m.id)}
                                        className={cn(
                                            "w-full text-left px-3 py-2 text-xs hover:bg-zinc-50 transition-colors",
                                            mode === m.id ? "bg-zinc-50 font-medium" : ""
                                        )}
                                    >
                                        {m.title}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Style Selector */}
                        <div className="relative group/dropdown">
                            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-50 hover:bg-zinc-100 rounded-lg text-xs font-medium text-zinc-600 transition-colors">
                                <Palette className="w-3.5 h-3.5" />
                                <span>{currentStyle?.icon} {currentStyle?.name || '咪蒙体'}</span>
                                <ChevronDown className="w-3 h-3 text-zinc-400" />
                            </button>
                            {/* Dropdown */}
                            <div className="absolute top-full left-0 mt-1 py-1 bg-white border border-zinc-200 rounded-lg shadow-lg opacity-0 invisible group-hover/dropdown:opacity-100 group-hover/dropdown:visible transition-all z-50 min-w-[140px]">
                                {ALL_STYLES.slice(0, 4).map(s => (
                                    <button
                                        key={s.id}
                                        onClick={() => setStyle(s.id as any)}
                                        className={cn(
                                            "w-full text-left px-3 py-2 text-xs hover:bg-zinc-50 transition-colors",
                                            style === s.id ? "bg-zinc-50 font-medium" : ""
                                        )}
                                    >
                                        {s.icon} {s.name}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Bottom Bar */}
                <div className="flex items-center justify-between px-4 pb-3 pt-1">
                    {/* Left: Hints / Tags */}
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                        <div className="flex items-center gap-1.5 bg-zinc-50 px-2 py-1 rounded-md border border-zinc-100">
                            <Sparkles className="w-3 h-3 text-indigo-500" />
                            <span>{UI_TEXT.heroInput?.aiEnhanced || 'AI 增强'}</span>
                        </div>
                        <span>{UI_TEXT.heroInput?.keyboardHint || '⌘ + Enter 发送'}</span>
                    </div>

                    {/* Right: Action Button */}
                    <button
                        onClick={handleStart}
                        disabled={!input.trim() || isRunning}
                        className={cn(
                            "flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-300",
                            input.trim() && !isRunning
                                ? "bg-zinc-900 text-white shadow-lg shadow-zinc-900/20 hover:scale-105 hover:bg-black"
                                : "bg-zinc-100 text-zinc-400 cursor-not-allowed"
                        )}
                    >
                        {UI_TEXT?.startButton || "开始深度创作"}
                        <Play className={cn("w-3.5 h-3.5 fill-current", isRunning && "hidden")} />
                        {isRunning && <span className="animate-spin">⏳</span>}
                    </button>
                </div>

                {/* Decorative Gradient Border Effect */}
                <div className="absolute inset-0 rounded-2xl pointer-events-none ring-1 ring-inset ring-black/5" />
            </div>

            {/* P10-9: Suggestions (Only in Idle Mode) */}
            {isIdle && (
                <div className="mt-8 text-center">
                    <p className="text-sm text-zinc-400">
                        尝试输入: "分析以太坊 Layer 2 的竞争格局" 或 "写一篇关于 DAO 治理的深度观察"
                    </p>
                </div>
            )}
        </div>
    );
}
