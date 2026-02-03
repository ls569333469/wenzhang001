import React, { useState } from 'react';
import { usePromptStore } from '../stores/usePromptStore';
import { PromptSection } from './PromptSection';
import { PromptPreviewModal } from './PromptPreviewModal';
import { RotateCcw, Eye, FileJson } from 'lucide-react';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';

export function StrategistPromptEditor() {
    const [showPreview, setShowPreview] = useState(false);

    const strategistPrompt = usePromptStore((state) => state.customPrompts.strategist);
    const updateStrategistPrompt = usePromptStore((state) => state.updateStrategistPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    const handleReset = () => {
        if (confirm('确定要恢复默认提示词吗？此操作无法撤销。')) {
            updateStrategistPrompt(DEFAULT_PROMPTS.strategist);
        }
    };

    return (
        <div className="space-y-6">
            <div className="space-y-4 animate-in fade-in duration-300">
                <PromptSection
                    label="📝 角色设定 (Role)"
                    value={strategistPrompt.role}
                    onChange={(val) => updateStrategistPrompt({ role: val })}
                    description="定义策略师的宏观视角和分析能力。"
                />

                <PromptSection
                    label="🎯 任务描述 (Task)"
                    value={strategistPrompt.task}
                    onChange={(val) => updateStrategistPrompt({ task: val })}
                    description="具体需要执行的分析步骤（提取锚点、生成策略、评分等）。"
                />

                <PromptSection
                    label="✍️ 风格要求 (Style)"
                    value={strategistPrompt.style}
                    onChange={(val) => updateStrategistPrompt({ style: val })}
                    description="分析报告的语调和专业度要求。"
                    optional
                />

                <PromptSection
                    label="🚫 禁止事项 (Forbidden)"
                    value={strategistPrompt.forbidden}
                    onChange={(val) => updateStrategistPrompt({ forbidden: val })}
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
                content={getAssembledPrompt('strategist')}
                title="完整提示词预览 - 策略师"
            />
        </div>
    );
}
