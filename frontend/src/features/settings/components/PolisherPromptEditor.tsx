import React, { useState } from 'react';
import { usePromptStore } from '../stores/usePromptStore';
import { PromptSection } from './PromptSection';
import { PromptPreviewModal } from './PromptPreviewModal';
import { RotateCcw, Eye, FileJson } from 'lucide-react';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';

export function PolisherPromptEditor() {
    const [showPreview, setShowPreview] = useState(false);

    const promptData = usePromptStore((state) => state.customPrompts.polisher);
    const updatePrompt = usePromptStore((state) => state.updatePolisherPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    const handleReset = () => {
        if (confirm('确定要恢复默认提示词吗？')) {
            updatePrompt(DEFAULT_PROMPTS.polisher);
        }
    };

    return (
        <div className="space-y-6">
            <div className="space-y-4 animate-in fade-in duration-300">
                <PromptSection
                    label="📝 角色设定 (Role)"
                    value={promptData.role}
                    onChange={(val) => updatePrompt({ role: val })}
                    description="定义润色师的专业水平。"
                />

                <PromptSection
                    label="🎯 任务描述 (Task)"
                    value={promptData.task}
                    onChange={(val) => updatePrompt({ task: val })}
                    description="说明润色目标（如保留原意、提升流畅度）。"
                />

                <PromptSection
                    label="✍️ 风格要求 (Style)"
                    value={promptData.style}
                    onChange={(val) => updatePrompt({ style: val })}
                    description="润色后的语言风格。"
                    optional
                />

                <PromptSection
                    label="🚫 禁止事项 (Forbidden)"
                    value={promptData.forbidden}
                    onChange={(val) => updatePrompt({ forbidden: val })}
                    optional
                />

                {/* SystemReadOnly Section */}
                <div className="border border-zinc-200 rounded-xl overflow-hidden bg-zinc-50 opacity-90">
                    <div className="p-3 bg-zinc-100 border-b border-zinc-200 flex items-center gap-2 text-zinc-500">
                        <FileJson className="w-4 h-4" />
                        <span className="font-medium text-sm">系统接管区域</span>
                    </div>
                    <div className="p-4">
                        <div className="text-xs text-zinc-500">
                            Polisher Router 逻辑将根据用户反馈强度（强润色/中润色）自动调整。
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
                content={getAssembledPrompt('polisher')}
                title="完整提示词预览 - 润色师"
            />
        </div>
    );
}
