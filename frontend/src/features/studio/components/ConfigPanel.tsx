'use client';

import { useQueryState, parseAsString, parseAsFloat } from 'nuqs';
import {
    CreationModeSchema,
    WritingStyleSchema,
    ArticleLengthSchema,
    defaultConfig
} from '../schema';
import { cn } from "@/lib/utils";
import { Settings2, Zap, BookOpen, Clock, Activity } from 'lucide-react';

/**
 * ConfigPanel - 创作配置面板 (Component Generation)
 * 
 * State: nuqs (URL 状态优先)
 * Schema: features/studio/schema.ts
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

    return (
        <div className="flex flex-col h-full bg-white">
            {/* Header */}
            <div className="p-6 pb-4">
                <div className="flex items-center gap-2 mb-1">
                    <Settings2 className="w-4 h-4 text-ink-primary" />
                    <h2 className="font-serif font-semibold text-lg text-ink-primary">
                        创作配置
                    </h2>
                </div>
                <p className="text-sm text-ink-muted">
                    定义 AI 的思考模式与输出风格
                </p>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-8 scrollbar-hide">

                {/* 1. Creation Mode */}
                <section className="space-y-3">
                    <Label icon={Zap} title="创作模式" />
                    <div className="grid grid-cols-1 gap-2">
                        <SelectionCard
                            active={mode === 'deep_analysis'}
                            onClick={() => setMode('deep_analysis')}
                            title="深度分析"
                            desc="全面调研，逻辑严密，适合研报"
                        />
                        <SelectionCard
                            active={mode === 'quick_summary'}
                            onClick={() => setMode('quick_summary')}
                            title="快速摘要"
                            desc="提炼核心观点，适合早报"
                        />
                        <div className="grid grid-cols-2 gap-2">
                            <SelectionCard
                                active={mode === 'rewrite'}
                                onClick={() => setMode('rewrite')}
                                title="改写润色"
                                compact
                            />
                            <SelectionCard
                                active={mode === 'translate'}
                                onClick={() => setMode('translate')}
                                title="专业翻译"
                                compact
                            />
                        </div>
                    </div>
                </section>

                {/* 2. Writing Style */}
                <section className="space-y-3">
                    <Label icon={BookOpen} title="写作风格" />
                    <div className="grid grid-cols-2 gap-2">
                        <StyleChip
                            label="专业投研"
                            active={style === 'professional'}
                            onClick={() => setStyle('professional')}
                        />
                        <StyleChip
                            label="KOL 观点"
                            active={style === 'kol'}
                            onClick={() => setStyle('kol')}
                        />
                        <StyleChip
                            label="学术严谨"
                            active={style === 'academic'}
                            onClick={() => setStyle('academic')}
                        />
                        <StyleChip
                            label="轻松随意"
                            active={style === 'casual'}
                            onClick={() => setStyle('casual')}
                        />
                    </div>
                </section>

                {/* 3. Length & Temp */}
                <section className="space-y-3">
                    <div className="flex items-center justify-between">
                        <Label icon={Clock} title="篇幅长度" />
                        <span className="text-xs text-ink-muted font-mono bg-zinc-50 px-2 py-0.5 rounded">
                            {length === 'short' ? '~500字' : length === 'medium' ? '~1500字' : '~3000字'}
                        </span>
                    </div>
                    <div className="flex bg-zinc-50 p-1 rounded-xl border border-zinc-100">
                        {(['short', 'medium', 'long'] as const).map((l) => (
                            <button
                                key={l}
                                onClick={() => setLength(l)}
                                className={cn(
                                    "flex-1 py-1.5 text-xs font-medium rounded-lg transition-all",
                                    length === l
                                        ? "bg-white text-ink-primary shadow-sm ring-1 ring-zinc-200"
                                        : "text-ink-muted hover:text-ink-secondary"
                                )}
                            >
                                {l === 'short' ? '短篇' : l === 'medium' ? '中篇' : '长文'}
                            </button>
                        ))}
                    </div>
                </section>

                <section className="space-y-3">
                    <div className="flex items-center justify-between">
                        <Label icon={Activity} title="随机性 (Temperature)" />
                        <span className="text-xs text-ink-primary font-mono">{temp}</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={temp}
                        onChange={(e) => setTemp(parseFloat(e.target.value))}
                        className="w-full accent-primary h-1.5 bg-zinc-100 rounded-lg appearance-none cursor-pointer"
                    />
                </section>

            </div>
        </div>
    );
}

// === Sub Components ===

function Label({ icon: Icon, title }: { icon: any, title: string }) {
    return (
        <label className="flex items-center gap-2 text-xs font-medium text-ink-muted uppercase tracking-wider">
            <Icon className="w-3.5 h-3.5" />
            {title}
        </label>
    );
}

function SelectionCard({ active, onClick, title, desc, compact }: any) {
    return (
        <div
            onClick={onClick}
            className={cn(
                "relative group cursor-pointer transition-all duration-200",
                "border rounded-xl px-4 py-3 text-left w-full",
                active
                    ? "bg-primary/5 border-primary/20 ring-1 ring-primary/10"
                    : "bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50/50"
            )}
        >
            <div className="flex items-center justify-between">
                <div>
                    <div className={cn(
                        "font-medium transition-colors",
                        active ? "text-ink-primary" : "text-ink-secondary"
                    )}>
                        {title}
                    </div>
                    {!compact && (
                        <div className="text-xs text-ink-muted mt-0.5">
                            {desc}
                        </div>
                    )}
                </div>
                {active && (
                    <div className="w-2 h-2 rounded-full bg-primary" />
                )}
            </div>
        </div>
    );
}

function StyleChip({ label, active, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "py-2.5 px-3 text-sm rounded-xl border transition-all text-center",
                active
                    ? "bg-primary text-white border-primary shadow-sm"
                    : "bg-white text-ink-secondary border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
            )}
        >
            {label}
        </button>
    );
}
