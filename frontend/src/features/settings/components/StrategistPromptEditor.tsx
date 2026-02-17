import React, { useState } from 'react';
import { usePromptStore, WriterPrompts } from '../stores/usePromptStore';
import { PromptSection } from './PromptSection';
import { PromptPreviewModal } from './PromptPreviewModal';
import { RotateCcw, Eye, FileJson } from 'lucide-react';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';

// P24-D: 6 模式子标签
const MODES: { id: keyof WriterPrompts; label: string }[] = [
    { id: 'hot_take', label: '锐评' },
    { id: 'short_article', label: '短篇' },
    { id: 'mid_article', label: '中篇' },
    { id: 'long_article', label: '长篇' },
    { id: 'tutorial', label: '教程' },
    { id: 'rewrite', label: '改写' },
];

export function StrategistPromptEditor() {
    const [activeMode, setActiveMode] = useState<keyof WriterPrompts>('hot_take');
    const [showPreview, setShowPreview] = useState(false);

    const strategistPrompts = usePromptStore((state) => state.customPrompts.strategist);
    const updateStrategistPrompt = usePromptStore((state) => state.updateStrategistPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    const currentPrompt = strategistPrompts[activeMode] || DEFAULT_PROMPTS.strategist[activeMode];

    const handleReset = () => {
        if (confirm('确定要恢复该模式的默认提示词吗？此操作无法撤销。')) {
            const defaultData = DEFAULT_PROMPTS.strategist[activeMode];
            updateStrategistPrompt(activeMode, defaultData);
        }
    };

    return (
        <div className="space-y-6">
            {/* P24-D: Mode Tabs */}
            <div className="flex overflow-x-auto border-b border-zinc-200">
                {MODES.map((mode) => (
                    <button
                        key={mode.id}
                        onClick={() => setActiveMode(mode.id)}
                        className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${activeMode === mode.id
                            ? 'border-primary text-primary'
                            : 'border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300'
                            }`}
                    >
                        {mode.label}
                    </button>
                ))}
            </div>

            {/* Editor Area */}
            <div className="space-y-4 animate-in fade-in duration-300" key={activeMode}>
                <PromptSection
                    label="📝 角色设定 (Role)"
                    value={currentPrompt.role}
                    onChange={(val) => updateStrategistPrompt(activeMode, { role: val })}
                    description="定义策略师的宏观视角和分析能力。"
                />

                <PromptSection
                    label="🎯 任务描述 (Task)"
                    value={currentPrompt.task}
                    onChange={(val) => updateStrategistPrompt(activeMode, { task: val })}
                    description="具体需要执行的分析步骤（提取锚点、生成策略、评分等）。"
                />

                <PromptSection
                    label="✍️ 风格要求 (Style)"
                    value={currentPrompt.style}
                    onChange={(val) => updateStrategistPrompt(activeMode, { style: val })}
                    description="分析报告的语调和专业度要求。"
                    optional
                />

                <PromptSection
                    label="🚫 禁止事项 (Forbidden)"
                    value={currentPrompt.forbidden}
                    onChange={(val) => updateStrategistPrompt(activeMode, { forbidden: val })}
                    description="防止幻觉和错误行为的约束。"
                    optional
                />

                {/* SystemReadOnly Section */}
                <div className="border border-zinc-200 rounded-xl overflow-hidden bg-zinc-50 opacity-90">
                    <div className="p-3 bg-zinc-100 border-b border-zinc-200 flex items-center gap-2 text-zinc-500">
                        <FileJson className="w-4 h-4" />
                        <span className="font-medium text-sm">系统接管区域 (只读)</span>
                    </div>
                    <div className="p-4 space-y-4">
                        <div>
                            <div className="text-xs font-semibold text-zinc-400 mb-1">系统会自动注入以下复杂结构：</div>
                            <ul className="list-disc list-inside text-xs text-zinc-600 space-y-1 font-mono">
                                <li>Info Anchors Extraction Rules</li>
                                <li>Viral Title Generation Matrix</li>
                                <li>Output JSON Schema (Strict)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4">
                    <button
                        onClick={handleReset}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100 rounded-lg transition-colors"
                    >
                        <RotateCcw className="w-4 h-4" />
                        恢复默认
                    </button>
                    <button
                        onClick={() => setShowPreview(true)}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-primary hover:bg-primary/90 rounded-lg shadow-sm transition-colors"
                    >
                        <Eye className="w-4 h-4" />
                        预览完整提示词
                    </button>
                </div>
            </div>

            <PromptPreviewModal
                isOpen={showPreview}
                onClose={() => setShowPreview(false)}
                content={getAssembledPrompt('strategist', activeMode)}
                title={`完整提示词预览 - 策略师 (${MODES.find(m => m.id === activeMode)?.label})`}
            />
        </div>
    );
}
