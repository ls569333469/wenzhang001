
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useQueryState, parseAsFloat } from 'nuqs';
import { Play, Sparkles, Command } from 'lucide-react';
import { cn } from "@/lib/utils";
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { UI_TEXT } from '@/config/constants';
import {
    CreationModeSchema,
    WritingStyleSchema,
    ArticleLengthSchema,
    defaultConfig
} from '@/features/studio/schema';
import { toast } from 'sonner';

export function HeroInput() {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [input, setInput] = useState('');
    const { startSession, status } = useAgentStore();
    const isRunning = status === 'thinking' || status === 'listening'; // Check statuses

    // === Read Config from URL (Source of Truth) ===
    const [mode] = useQueryState('mode', {
        defaultValue: defaultConfig.mode,
        parse: (v) => CreationModeSchema.safeParse(v).success ? v : defaultConfig.mode
    });
    const [style] = useQueryState('style', {
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

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [input]);

    const handleStart = () => {
        if (!input.trim()) return;

        // --- Phase 6: Settings & Prompt Injection ---
        // Need to read from localStorage for custom prompts if any
        // Since we are prefixing, we do it here.
        // But for "Pragmatic Fix", let's keep it simple first and just start session.
        // We will add the injection logic in Step 3 (Settings MVP).

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
        <div className="w-full max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-700">
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
                        placeholder={UI_TEXT?.inputPlaceholder || "Enter your research topic..."} // Fallback just in case
                        className="w-full bg-transparent border-none focus:ring-0 text-lg text-ink-primary placeholder:text-zinc-300 min-h-[60px] max-h-[400px] resize-none py-3 px-4 font-sans leading-relaxed"
                        style={{ height: '60px' }}
                        autoFocus
                    />
                </div>

                {/* Bottom Bar */}
                <div className="flex items-center justify-between px-4 pb-3 pt-1">
                    {/* Left: Hints / Tags */}
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                        <div className="flex items-center gap-1.5 bg-zinc-50 px-2 py-1 rounded-md border border-zinc-100">
                            <Sparkles className="w-3 h-3 text-indigo-500" />
                            <span>AI Enhanced</span>
                        </div>
                        <span>CMD + Enter to send</span>
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
                        {UI_TEXT?.startButton || "Start Creation"}
                        <Play className={cn("w-3.5 h-3.5 fill-current", isRunning && "hidden")} />
                        {isRunning && <span className="animate-spin">⏳</span>}
                    </button>
                </div>

                {/* Decorative Gradient Border Effect */}
                <div className="absolute inset-0 rounded-2xl pointer-events-none ring-1 ring-inset ring-black/5" />
            </div>

            {/* Empty State / Suggestions (Optional Polish) */}
            <div className="mt-8 text-center">
                <p className="text-sm text-zinc-400">
                    尝试输入: "分析以太坊 Layer 2 的竞争格局" 或 "写一篇关于 DAO 治理的深度观察"
                </p>
            </div>
        </div>
    );
}
