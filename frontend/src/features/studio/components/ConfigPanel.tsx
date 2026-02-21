'use client';

import React from 'react';
import { useQueryState, parseAsFloat } from 'nuqs';
import {
    CreationModeSchema,
    WritingStyleSchema,
    LengthTypeSchema,
    defaultConfig,
    type LengthType,
    type CreationMode,
    type WritingStyle
} from '../schema';
import { cn } from "@/lib/utils";
import { Settings2, Zap, Check } from 'lucide-react';
import { type LucideIcon } from 'lucide-react';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import { CREATION_MODES, UI_TEXT } from '@/config/constants';
import { useAgentStore } from '../../agent/stores/useAgentStore';
import { toast } from 'sonner';

// P27: Mode sub-components
import { ModeStandard } from './config/ModeStandard';
import { ModeBullish } from './config/ModeBullish';
import { ModeKaito } from './config/ModeKaito';
import { ModeResearch } from './config/ModeResearch';

/**
 * ConfigPanel - 创作配置面板
 * 
 * P27 重构: switch(mode) 路由到不同配置子组件
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

    const [lengthType, setLengthType] = useQueryState('lengthType', {
        defaultValue: 'auto' as LengthType,
        parse: (v) => LengthTypeSchema.safeParse(v).success ? v as LengthType : 'auto'
    });

    const [customLength, setCustomLength] = useQueryState('customLength', parseAsFloat.withDefault(0));

    // P27: Prevent mode switching if editor is dirty
    const isDirty = useAgentStore(state => state.isDirty);
    const saveToServer = useAgentStore(state => state.saveToServer);

    const handleModeChange = async (newMode: string) => {
        if (newMode === mode) return;
        if (isDirty) {
            await saveToServer();
            toast.info('已为您自动保存当前草稿');
        }
        setMode(newMode);
    };

    // P27: 根据模式渲染不同配置区块
    const renderModeConfig = () => {
        switch (mode) {
            case 'bullish_take':
                return (
                    <ModeBullish
                        lengthType={lengthType}
                        setLengthType={(v) => setLengthType(v)}
                        customLength={customLength}
                        setCustomLength={(v) => setCustomLength(v)}
                    />
                );
            case 'kaito_yap':
                return (
                    <ModeKaito
                        lengthType={lengthType}
                        setLengthType={(v) => setLengthType(v)}
                        customLength={customLength}
                        setCustomLength={(v) => setCustomLength(v)}
                    />
                );
            case 'project_research':
                return <ModeResearch />;
            default:
                // 锐评/短篇/中篇/长篇/教程 → 标准配置
                return (
                    <ModeStandard
                        style={style}
                        setStyle={(v) => setStyle(v)}
                        lengthType={lengthType}
                        setLengthType={(v) => setLengthType(v)}
                        customLength={customLength}
                        setCustomLength={(v) => setCustomLength(v)}
                    />
                );
        }
    };

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

                    {/* === 核心配置 === */}
                    <AccordionItem value="basic" className="border-none">
                        <AccordionTrigger className="text-sm font-semibold text-ink-primary hover:no-underline py-2 sticky top-0 bg-white z-10">
                            {UI_TEXT.coreSettings}
                        </AccordionTrigger>
                        <AccordionContent className="space-y-6 pt-2">
                            {/* Mode Selection — 所有模式共享 */}
                            <section className="space-y-3">
                                <Label icon={Zap} title={UI_TEXT.labels.mode} />
                                <div className="grid grid-cols-1 gap-2">
                                    {CREATION_MODES.filter(m => !m.compact).map(m => (
                                        <SelectionCard
                                            key={m.id}
                                            active={mode === m.id}
                                            onClick={() => handleModeChange(m.id)}
                                            title={m.title}
                                            desc={m.desc}
                                        />
                                    ))}
                                    <div className="grid grid-cols-2 gap-2">
                                        {CREATION_MODES.filter(m => m.compact).map(m => (
                                            <SelectionCard
                                                key={m.id}
                                                active={mode === m.id}
                                                onClick={() => handleModeChange(m.id)}
                                                title={m.title}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </section>

                            {/* P27: 模式专属配置区块 */}
                            {renderModeConfig()}
                        </AccordionContent>
                    </AccordionItem>

                </Accordion>
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
