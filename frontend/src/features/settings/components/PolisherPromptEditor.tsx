import React, { useState } from 'react';
import { usePromptStore, WriterPrompts } from '../stores/usePromptStore';
import { PromptSection } from './PromptSection';
import { PromptPreviewModal } from './PromptPreviewModal';
import { RotateCcw, Eye, FileJson, SkipForward } from 'lucide-react';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';
import { SKIP_MODES } from '../../studio/schema';

// P24-D: 6 模式子标签
const MODES: { id: keyof WriterPrompts; label: string }[] = [
    { id: 'hot_take', label: '锐评' },
    { id: 'short_article', label: '短篇' },
    { id: 'mid_article', label: '中篇' },
    { id: 'long_article', label: '长篇' },
    { id: 'tutorial', label: '教程' },

];

export function PolisherPromptEditor() {
    const [activeMode, setActiveMode] = useState<keyof WriterPrompts>('mid_article'); // 默认非跳过模式
    const [showPreview, setShowPreview] = useState(false);

    const polisherPrompts = usePromptStore((state) => state.customPrompts.polisher);
    const updatePolisherPrompt = usePromptStore((state) => state.updatePolisherPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    const isSkipped = SKIP_MODES.polisher.includes(activeMode as any);
    const currentPrompt = polisherPrompts[activeMode] || DEFAULT_PROMPTS.polisher[activeMode];

    const handleReset = () => {
        if (confirm('确定要恢复该模式的默认提示词吗？')) {
            const defaultData = DEFAULT_PROMPTS.polisher[activeMode];
            updatePolisherPrompt(activeMode, defaultData);
        }
    };

    return (
        <div className="space-y-6">
            {/* P24-D: Mode Tabs with skip marking */}
            <div className="flex overflow-x-auto border-b border-zinc-200">
                {MODES.map((mode) => {
                    const skip = SKIP_MODES.polisher.includes(mode.id as any);
                    return (
                        <button
                            key={mode.id}
                            onClick={() => setActiveMode(mode.id)}
                            className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors flex items-center gap-1.5 ${activeMode === mode.id
                                ? 'border-primary text-primary'
                                : skip
                                    ? 'border-transparent text-zinc-300'
                                    : 'border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300'
                                }`}
                        >
                            {mode.label}
                            {skip && <SkipForward className="w-3 h-3" />}
                        </button>
                    );
                })}
            </div>

            {/* Editor Area */}
            <div className="space-y-4 animate-in fade-in duration-300" key={activeMode}>
                {isSkipped ? (
                    <div className="p-8 text-center text-zinc-400 bg-zinc-50 rounded-xl border border-dashed border-zinc-200">
                        <SkipForward className="w-8 h-8 mx-auto mb-3 text-zinc-300" />
                        <p className="font-medium">该模式跳过润色师</p>
                        <p className="text-sm mt-1">「{MODES.find(m => m.id === activeMode)?.label}」模式不使用 Polisher agent。</p>
                    </div>
                ) : (
                    <>
                        <PromptSection
                            label="📝 角色设定 (Role)"
                            value={currentPrompt.role}
                            onChange={(val) => updatePolisherPrompt(activeMode, { role: val })}
                            description="定义润色师的专业水平。"
                        />

                        <PromptSection
                            label="🎯 任务描述 (Task)"
                            value={currentPrompt.task}
                            onChange={(val) => updatePolisherPrompt(activeMode, { task: val })}
                            description="说明润色目标（如保留原意、提升流畅度）。"
                        />

                        <PromptSection
                            label="✍️ 风格要求 (Style)"
                            value={currentPrompt.style}
                            onChange={(val) => updatePolisherPrompt(activeMode, { style: val })}
                            description="润色后的语言风格。"
                            optional
                        />

                        <PromptSection
                            label="🚫 禁止事项 (Forbidden)"
                            value={currentPrompt.forbidden}
                            onChange={(val) => updatePolisherPrompt(activeMode, { forbidden: val })}
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
                    </>
                )}
            </div>

            <PromptPreviewModal
                isOpen={showPreview}
                onClose={() => setShowPreview(false)}
                content={getAssembledPrompt('polisher', activeMode)}
                title={`完整提示词预览 - 润色师 (${MODES.find(m => m.id === activeMode)?.label})`}
            />
        </div>
    );
}
