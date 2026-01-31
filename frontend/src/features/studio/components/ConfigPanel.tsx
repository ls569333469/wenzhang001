'use client';

import React from 'react';
import { useQueryState, parseAsString, parseAsFloat } from 'nuqs';
import {
    CreationModeSchema,
    WritingStyleSchema,
    ArticleLengthSchema,
    defaultConfig,
    type ArticleLength,
    type CreationMode,
    type WritingStyle
} from '../schema';
import { cn } from "@/lib/utils";
import { Settings2, Zap, BookOpen, Clock, Activity, Play, Loader2, Square, Database, Check, Sliders, ChevronDown } from 'lucide-react';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';
import { Button } from "@/components/ui/button";
import { type LucideIcon } from 'lucide-react';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import { Slider } from "@/components/ui/slider";
import { ALL_STYLES, getStyleById } from '@/lib/styles';
import { CREATION_MODES, ARTICLE_LENGTHS, HOOK_INTENSITIES, WEB3_KNOWLEDGE_BASES, UI_TEXT } from '@/config/constants';

/**
 * ConfigPanel - 创作配置面板
 * 
 * State: nuqs (URL 状态优先)
 * Schema: features/studio/schema.ts
 * Config: config/constants.ts (Localization)
 */

export function ConfigPanel() {
    // 1. URL State Binding
    const [mode, setMode] = useQueryState('mode', {
        defaultValue: defaultConfig.mode,
        parse: (v) => CreationModeSchema.safeParse(v).success ? v : defaultConfig.mode
    });

    const [style, setStyle] = useQueryState('style', {
        defaultValue: defaultConfig.style,
        parse: (v) => WritingStyleSchema.safeParse(v).success ? v : defaultConfig.style
    });

    const [length, setLength] = useQueryState('length', {
        defaultValue: defaultConfig.length,
        parse: (v) => ArticleLengthSchema.safeParse(v).success ? v : defaultConfig.length
    });

    const [temp, setTemp] = useQueryState('temp', parseAsFloat.withDefault(defaultConfig.temperature));

    // 2. Advanced Params URL Binding
    const [topP, setTopP] = useQueryState('topP', parseAsFloat.withDefault(0.9));
    const [maxTokens, setMaxTokens] = useQueryState('maxTokens', parseAsFloat.withDefault(4096));

    // Knowledge Sources - Encoded as comma separated string
    const [knowledgeIds, setKnowledgeIds] = useQueryState('knowledge', {
        defaultValue: ['auto'], // Default to auto
        parse: (v) => v ? v.split(',') : ['auto'],
        serialize: (v) => v.join(',')
    });

    // P10-3: Hook Intensity
    const [hookIntensity, setHookIntensity] = useQueryState('hook', {
        defaultValue: 'standard',
        parse: (v) => ['gentle', 'standard', 'strong', 'explosive'].includes(v) ? v : 'standard'
    });

    // P10-6: Retention Level (保留度等级 1-5)
    const [retentionLevel, setRetentionLevel] = useQueryState('retention', {
        defaultValue: 3,
        parse: (v) => {
            const n = parseInt(v);
            return n >= 1 && n <= 5 ? n : 3;
        },
        serialize: (v) => v.toString()
    });

    return (
        <div className="flex flex-col h-full bg-white">
            {/* Header */}
            <div className="p-6 pb-4">
                <div className="flex items-center gap-2 mb-1">
                    <Settings2 className="w-4 h-4 text-ink-primary" />
                    <h2 className="font-serif font-semibold text-lg text-ink-primary">
                        {UI_TEXT.panelTitle}
                    </h2>
                </div>
                <p className="text-sm text-ink-muted">
                    {UI_TEXT.panelDesc}
                </p>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto px-6 pb-6 scrollbar-hide">
                <Accordion type="multiple" defaultValue={["basic"]} className="w-full space-y-4">

                    {/* === 1. Basic Settings (Mode & Style) === */}
                    <AccordionItem value="basic" className="border-none">
                        <AccordionTrigger className="text-sm font-semibold text-ink-primary hover:no-underline py-2 sticky top-0 bg-white z-10">
                            {UI_TEXT.coreSettings}
                        </AccordionTrigger>
                        <AccordionContent className="space-y-6 pt-2">
                            {/* Mode Selection */}
                            <section className="space-y-3">
                                <Label icon={Zap} title={UI_TEXT.labels.mode} />
                                <div className="grid grid-cols-1 gap-2">
                                    {CREATION_MODES.filter(m => !m.compact).map(m => (
                                        <SelectionCard
                                            key={m.id}
                                            active={mode === m.id}
                                            onClick={() => setMode(m.id)}
                                            title={m.title}
                                            desc={m.desc}
                                        />
                                    ))}
                                    <div className="grid grid-cols-2 gap-2">
                                        {CREATION_MODES.filter(m => m.compact).map(m => (
                                            <SelectionCard
                                                key={m.id}
                                                active={mode === m.id}
                                                onClick={() => setMode(m.id)}
                                                title={m.title}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </section>

                            {/* Length Selection */}
                            <section className="space-y-3">
                                <Label icon={Clock} title={UI_TEXT.labels.length} />
                                <div className="grid grid-cols-3 gap-2">
                                    {ARTICLE_LENGTHS.map((l) => (
                                        <button
                                            key={l.id}
                                            onClick={() => setLength(l.id)}
                                            className={cn(
                                                "py-2 px-3 text-xs font-medium rounded-xl border transition-all",
                                                length === l.id
                                                    ? "bg-zinc-900 text-white border-zinc-900 shadow-sm"
                                                    : "bg-white text-ink-muted border-zinc-200 hover:border-zinc-300"
                                            )}
                                        >
                                            {l.label}
                                        </button>
                                    ))}
                                </div>
                            </section>

                            {/* P10-3: Hook Intensity Selection */}
                            <section className="space-y-3">
                                <Label icon={Zap} title={UI_TEXT.labels.hookIntensity} />
                                <div className="grid grid-cols-2 gap-2">
                                    {HOOK_INTENSITIES.map((h) => (
                                        <button
                                            key={h.id}
                                            onClick={() => setHookIntensity(h.id)}
                                            className={cn(
                                                "py-2.5 px-3 rounded-xl border transition-all text-left",
                                                hookIntensity === h.id
                                                    ? "bg-gradient-to-br from-amber-500 to-orange-500 text-white border-amber-500 shadow-lg shadow-amber-500/20"
                                                    : "bg-white text-ink-secondary border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
                                            )}
                                        >
                                            <div className="text-xs font-semibold">{h.label}</div>
                                            <div className={cn(
                                                "text-[10px] mt-0.5",
                                                hookIntensity === h.id ? "text-white/80" : "text-zinc-400"
                                            )}>
                                                {h.desc}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </section>

                            {/* Style Selection (Business Content Injection) */}
                            <section className="space-y-3">
                                <Label icon={BookOpen} title={UI_TEXT.labels.style} />
                                <div className="grid grid-cols-2 gap-2">
                                    {ALL_STYLES.map((s) => (
                                        <StyleCard
                                            key={s.id}
                                            icon={s.icon}
                                            title={s.name}
                                            active={style === s.id}
                                            color={s.color}
                                            onClick={() => setStyle(s.id as any)}
                                        />
                                    ))}
                                </div>
                            </section>

                            {/* P10-6: Retention Level (保留度等级) */}
                            <section className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <Label icon={Sliders} title="内容保留度" />
                                    <span className="text-xs font-mono text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded">
                                        L{retentionLevel}
                                    </span>
                                </div>
                                <Slider
                                    value={[retentionLevel]}
                                    min={1}
                                    max={5}
                                    step={1}
                                    onValueChange={([v]) => setRetentionLevel(v)}
                                    className="py-2"
                                />
                                <div className="flex justify-between text-[10px] text-zinc-400">
                                    <span>润色优化</span>
                                    <span>框架保留</span>
                                    <span>观点继承</span>
                                    <span>主题借用</span>
                                    <span>灵感触发</span>
                                </div>
                                <p className="text-[10px] text-zinc-400">
                                    {retentionLevel === 1 && "95% 保留 - 仅语言润色，结构和论点完全保留"}
                                    {retentionLevel === 2 && "75% 保留 - 保留核心框架，允许表达优化"}
                                    {retentionLevel === 3 && "50% 保留 - 继承核心观点，重新组织表达"}
                                    {retentionLevel === 4 && "30% 保留 - 仅借用主题和关键词，大幅再创作"}
                                    {retentionLevel === 5 && "10% 保留 - 仅作为灵感来源，完全重新创作"}
                                </p>
                            </section>
                        </AccordionContent>
                    </AccordionItem>

                    {/* === 2. Knowledge Base (New) === */}
                    <AccordionItem value="knowledge" className="border-none">
                        <AccordionTrigger className="text-sm font-semibold text-ink-primary hover:no-underline py-2 sticky top-0 bg-white z-10">
                            {UI_TEXT.knowledgeBase}
                        </AccordionTrigger>
                        <AccordionContent className="pt-2">
                            <KnowledgeSelector
                                selectedIds={knowledgeIds}
                                onChange={setKnowledgeIds}
                            />
                        </AccordionContent>
                    </AccordionItem>

                    {/* === 3. Advanced Settings (Default Collapsed) === */}
                    <AccordionItem value="advanced" className="border-none">
                        <AccordionTrigger className="text-sm font-semibold text-ink-primary hover:no-underline py-2 sticky top-0 bg-white z-10">
                            {UI_TEXT.advancedSettings}
                        </AccordionTrigger>
                        <AccordionContent className="space-y-6 pt-2 bg-zinc-50/50 p-4 rounded-xl border border-zinc-100/50">
                            {/* Temperature */}
                            <section className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <Label icon={Activity} title={UI_TEXT.labels.temperature} />
                                    <span className="text-xs font-mono text-zinc-500 bg-white px-1.5 py-0.5 rounded border border-zinc-200">{temp}</span>
                                </div>
                                <Slider
                                    value={[temp]}
                                    min={0}
                                    max={1.0}
                                    step={0.1}
                                    onValueChange={([v]) => setTemp(v)}
                                    className="py-2"
                                />
                                <p className="text-[10px] text-zinc-400">
                                    数值越高创意越强，越低越稳定
                                </p>
                            </section>

                            {/* Top P */}
                            <section className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <Label icon={Sliders} title={UI_TEXT.labels.topP} />
                                    <span className="text-xs font-mono text-zinc-500 bg-white px-1.5 py-0.5 rounded border border-zinc-200">{topP}</span>
                                </div>
                                <Slider
                                    value={[topP]}
                                    min={0}
                                    max={1.0}
                                    step={0.05}
                                    onValueChange={([v]) => setTopP(v)}
                                    className="py-2"
                                />
                            </section>

                            {/* Max Tokens */}
                            <section className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <Label icon={Square} title={UI_TEXT.labels.maxTokens} />
                                    <input
                                        type="number"
                                        value={maxTokens}
                                        onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                                        className="w-20 text-right text-xs bg-white border border-zinc-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-zinc-400"
                                    />
                                </div>
                            </section>
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>

                {/* --- Input Area Removed (Moved to HeroInput) --- */}
                {/* 
                <div className="pt-6 border-t border-zinc-100 space-y-4 mt-4">
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-ink-primary uppercase tracking-wide">{UI_TEXT.inputLabel}</label>
                        <textarea ... />
                    </div>
                    <StartButton ... />
                </div> 
                */}
            </div>
        </div>
    );
}

// === Sub Components ===

function Label({ icon: Icon, title }: { icon: LucideIcon, title: string }) {
    return (
        <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
            <Icon className="w-3.5 h-3.5" />
            {title}
        </label>
    );
}

interface SelectionCardProps {
    active: boolean;
    onClick: () => void;
    title: string;
    desc?: string;
}

function SelectionCard({ active, onClick, title, desc }: SelectionCardProps) {
    return (
        <div
            onClick={onClick}
            className={cn(
                "relative group cursor-pointer transition-all duration-200",
                "border rounded-xl px-4 py-3 text-left w-full",
                active
                    ? "bg-zinc-900 border-zinc-900 text-white shadow-md ring-1 ring-zinc-900/10"
                    : "bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
            )}
        >
            <div className="flex items-center justify-between">
                <div>
                    <div className={cn(
                        "font-semibold text-sm transition-colors",
                        active ? "text-white" : "text-ink-primary"
                    )}>
                        {title}
                    </div>
                    {desc && (
                        <div className={cn(
                            "text-xs mt-0.5",
                            active ? "text-zinc-400" : "text-ink-muted"
                        )}>
                            {desc}
                        </div>
                    )}
                </div>
                {active && (
                    <div className="w-2 h-2 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
                )}
            </div>
        </div>
    );
}

// Rich Style Card for Business Injection
interface StyleCardProps {
    icon: string;
    title: string;
    active: boolean;
    color: string;
    onClick: () => void;
}

function StyleCard({ icon, title, active, color, onClick }: StyleCardProps) {
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
            {active && (
                <Check className="w-3.5 h-3.5 text-zinc-900 absolute top-2 right-2" />
            )}
        </button>
    );
}


interface StartButtonProps {
    mode: CreationMode;
    style: WritingStyle;
    length: ArticleLength;
    temp: number;
    topP: number;
    maxTokens: number;
    knowledgeIds: string[];
    input: string;
}

function StartButton({ mode, style, length, temp, topP, maxTokens, knowledgeIds, input }: StartButtonProps) {
    const { startSession, status, stopSession } = useAgentStore();
    const isRunning = status === 'thinking' || status === 'writing' || status === 'connecting';

    const handleStart = () => {
        if (!input || !input.trim()) return;

        // Construct full creation config
        startSession({
            input: input.trim(),
            config: {
                mode,
                style,
                length,
                temperature: temp,
                knowledgeSources: knowledgeIds,
                // These will be ignored by Zod if strict, but passed if schema allows
                // Ensure Store/API supports them (Phase 5.7 Scope)
                topP: topP,
                maxTokens: maxTokens
            } as any // Temporary cast until store types fully sync, though Schema is updated
        });
    };

    if (isRunning) {
        return (
            <button
                onClick={stopSession}
                className="w-full py-3 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl font-medium flex items-center justify-center gap-2 transition-all"
            >
                <div className="relative">
                    <Loader2 className="w-4 h-4 animate-spin opacity-50 absolute" />
                    <Square className="w-4 h-4 fill-current relative z-10" />
                </div>
                {UI_TEXT.stopButton}
            </button>
        );
    }

    return (
        <button
            onClick={handleStart}
            disabled={!input || !input.trim()}
            className={cn(
                "w-full py-3 text-white rounded-xl font-medium shadow-lg transition-all flex items-center justify-center gap-2 group",
                !input || !input.trim()
                    ? "bg-zinc-300 cursor-not-allowed shadow-none"
                    : "bg-zinc-900 hover:bg-zinc-800 hover:shadow-xl hover:-translate-y-0.5"
            )}
        >
            <Play className="w-4 h-4 fill-current group-hover:scale-110 transition-transform" />
            {UI_TEXT.startButton}
        </button>
    );
}

function KnowledgeSelector({ selectedIds, onChange }: { selectedIds: string[], onChange: (ids: string[]) => void }) {
    const toggleId = (id: string) => {
        if (id === 'auto') {
            // Selecting Auto clears everything else
            onChange(['auto']);
            return;
        }

        let newIds = [...selectedIds];

        // If currently Auto, clear it first
        if (newIds.includes('auto')) {
            newIds = [];
        }

        if (newIds.includes(id)) {
            newIds = newIds.filter(i => i !== id);
        } else {
            newIds.push(id);
        }

        // If nothing selected, default back to Auto? Or allow empty?
        // Let's allow empty for now, or maybe default to Auto if empty.
        // User requirement: "Default to Auto". So if empty -> Auto.
        if (newIds.length === 0) {
            onChange(['auto']);
        } else {
            onChange(newIds);
        }
    };

    return (
        <div className="flex flex-col gap-2">
            {WEB3_KNOWLEDGE_BASES.map(kb => {
                const isSelected = selectedIds.includes(kb.id);
                return (
                    <div
                        key={kb.id}
                        onClick={() => toggleId(kb.id)}
                        className={cn(
                            "flex items-center justify-between p-2.5 rounded-xl border text-sm cursor-pointer transition-all hover:scale-[1.01]",
                            isSelected
                                ? "bg-zinc-900 border-zinc-900 text-white shadow-md"
                                : "bg-white border-zinc-200 text-ink-secondary hover:border-zinc-300"
                        )}
                    >
                        <div className="flex items-center gap-3">
                            <div className={cn(
                                "w-6 h-6 rounded flex items-center justify-center transition-colors text-xs font-mono",
                                isSelected ? "bg-white/20 text-white" : "bg-zinc-100 text-zinc-500"
                            )}>
                                {kb.id.includes('-') ? kb.id.split('-')[1].slice(0, 2).toUpperCase() : kb.id.slice(0, 2).toUpperCase()}
                            </div>
                            <span className="font-medium">{kb.name}</span>
                        </div>

                        {isSelected ? (
                            <Check className="w-4 h-4 text-white" />
                        ) : (
                            <span className="text-[10px] text-zinc-400 font-mono bg-zinc-50 px-1.5 py-0.5 rounded">
                                {kb.count}
                            </span>
                        )}
                    </div>
                )
            })}
        </div>
    );
}
