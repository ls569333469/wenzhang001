'use client';

import React, { useState } from 'react';
import { ChevronDown, RotateCcw, Info, Sparkles, Copy, Check } from 'lucide-react';
import { cn } from "@/lib/utils";

/**
 * P10-6: Enhanced Prompt Editor Component
 * 
 * Features:
 * - Variable hints tooltip
 * - Preset templates
 * - Character count
 * - Reset to default
 */

interface PromptEditorProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    defaultValue: string;
    agent: 'strategist' | 'writer' | 'critic';
    presets?: PromptPreset[];
}

interface PromptPreset {
    id: string;
    name: string;
    content: string;
}

// Variable hints for each agent type
const VARIABLE_HINTS: Record<string, string[]> = {
    strategist: [
        '{{ input }} - 用户输入的原始素材',
        '{{ narrative_type }} - 叙事类型 (深度分析/快速摘要)',
        '{{ style }} - 写作风格 (咪蒙体/半佛体等)',
    ],
    writer: [
        '{{ selected_option }} - 用户选择的策略方案',
        '{{ info_anchors }} - 必须包含的关键信息',
        '{{ style_notes }} - 风格参考笔记',
    ],
    critic: [
        '{{ draft }} - 初稿内容',
        '{{ style }} - 目标风格',
        '{{ quality_criteria }} - 质量评判标准',
    ],
};

// Default presets for quick selection
const DEFAULT_PRESETS: Record<string, PromptPreset[]> = {
    strategist: [
        { id: 'viral', name: '🔥 爆款优先', content: '专注于识别最具传播潜力的角度，强调情绪触发点和社交货币价值。优先选择能引发读者共鸣和分享欲望的切入点。' },
        { id: 'insight', name: '💡 深度洞察', content: '挖掘事件背后的深层逻辑，提供独特的分析视角。避免表面化解读，突出专业见解。' },
        { id: 'data', name: '📊 数据驱动', content: '围绕核心数据展开分析，用数字说话。强调数据的来源可靠性和对比分析。' },
    ],
    writer: [
        { id: 'mimeng', name: '🎭 咪蒙风格', content: '使用短句爆发、情绪递进的写法。每段以金句收尾，注重读者代入感。适当使用反问和感叹。' },
        { id: 'banfo', name: '🎩 半佛风格', content: '用轻松幽默的语气讲严肃话题。善用比喻和类比，把复杂概念讲得通俗易懂。偶尔自嘲。' },
        { id: 'professional', name: '📰 专业严谨', content: '保持客观中立的立场，逻辑清晰。适当引用数据和来源，避免过度情绪化表达。' },
    ],
    critic: [
        { id: 'strict', name: '🔍 严格审核', content: '逐段检查逻辑漏洞、事实错误和表达问题。对争议性观点标注风险。' },
        { id: 'flow', name: '✨ 流畅优先', content: '关注阅读体验和节奏感。优化过渡语和段落衔接，提升可读性。' },
        { id: 'seo', name: '🎯 传播优化', content: '优化标题和开头的吸引力。检查关键词密度和分享点设置。' },
    ],
};

export function PromptEditor({
    label,
    value,
    onChange,
    defaultValue,
    agent,
    presets = DEFAULT_PRESETS[agent] || [],
}: PromptEditorProps) {
    const [showPresets, setShowPresets] = useState(false);
    const [showVariables, setShowVariables] = useState(false);
    const [copied, setCopied] = useState(false);

    const charCount = value.length;
    const variables = VARIABLE_HINTS[agent] || [];

    const handleReset = () => {
        onChange(defaultValue);
    };

    const handlePresetSelect = (preset: PromptPreset) => {
        // Append preset to existing content
        const newValue = value.trim() ? `${value}\n\n${preset.content}` : preset.content;
        onChange(newValue);
        setShowPresets(false);
    };

    const handleCopy = async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="space-y-2">
            {/* Header */}
            <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-ink-primary uppercase tracking-wide flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                    {label}
                </label>
                <div className="flex items-center gap-2">
                    {/* Variable Hints */}
                    <div className="relative">
                        <button
                            onClick={() => setShowVariables(!showVariables)}
                            className={cn(
                                "p-1.5 rounded-lg transition-colors",
                                showVariables ? "bg-blue-50 text-blue-600" : "text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100"
                            )}
                            title="变量参考"
                        >
                            <Info className="w-3.5 h-3.5" />
                        </button>
                        {showVariables && (
                            <div className="absolute right-0 top-8 z-20 w-72 bg-white rounded-xl shadow-xl border border-zinc-200 p-3 animate-in fade-in slide-in-from-top-2">
                                <p className="text-xs font-semibold text-zinc-600 mb-2">可用变量</p>
                                <div className="space-y-1.5">
                                    {variables.map((v, i) => (
                                        <div key={i} className="text-[11px] font-mono text-zinc-500 bg-zinc-50 rounded-lg px-2 py-1">
                                            {v}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Preset Selector */}
                    <div className="relative">
                        <button
                            onClick={() => setShowPresets(!showPresets)}
                            className={cn(
                                "flex items-center gap-1 px-2 py-1 text-xs rounded-lg transition-colors",
                                showPresets ? "bg-purple-50 text-purple-600" : "text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100"
                            )}
                        >
                            预设模板
                            <ChevronDown className={cn("w-3 h-3 transition-transform", showPresets && "rotate-180")} />
                        </button>
                        {showPresets && (
                            <div className="absolute right-0 top-8 z-20 w-56 bg-white rounded-xl shadow-xl border border-zinc-200 p-2 animate-in fade-in slide-in-from-top-2">
                                {presets.map((preset) => (
                                    <button
                                        key={preset.id}
                                        onClick={() => handlePresetSelect(preset)}
                                        className="w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-zinc-50 transition-colors"
                                    >
                                        {preset.name}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Copy */}
                    <button
                        onClick={handleCopy}
                        className="p-1.5 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-lg transition-colors"
                        title="复制"
                    >
                        {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>

                    {/* Reset */}
                    <button
                        onClick={handleReset}
                        className="p-1.5 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-lg transition-colors"
                        title="重置为默认"
                    >
                        <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                </div>
            </div>

            {/* Textarea */}
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className={cn(
                    "w-full min-h-[140px] p-3 text-sm bg-zinc-50 border border-zinc-200 rounded-xl",
                    "focus:ring-2 focus:ring-primary/20 focus:border-primary focus:bg-white",
                    "font-mono leading-relaxed resize-y transition-colors"
                )}
                placeholder="输入提示词..."
            />

            {/* Footer */}
            <div className="flex items-center justify-between text-[10px] text-zinc-400">
                <span>{charCount} 字符</span>
                <span className="text-zinc-300">Tip: 使用 {'{{ variable }}'} 语法引用变量</span>
            </div>
        </div>
    );
}
