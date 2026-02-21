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

export function CriticPromptEditor() {
    const [activeMode, setActiveMode] = useState<keyof WriterPrompts>('short_article'); // 默认非跳过模式
    const [showPreview, setShowPreview] = useState(false);

    const criticPrompts = usePromptStore((state) => state.customPrompts.critic);
    const updateCriticPrompt = usePromptStore((state) => state.updateCriticPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    const isSkipped = SKIP_MODES.critic.includes(activeMode as any);
    const currentPrompt = criticPrompts[activeMode] || DEFAULT_PROMPTS.critic[activeMode];

    const handleReset = () => {
        if (confirm('确定要恢复该模式的默认提示词吗？')) {
            const defaultData = DEFAULT_PROMPTS.critic[activeMode];
            updateCriticPrompt(activeMode, defaultData);
        }
    };

    return (
        <div className="space-y-6">
            {/* P24-D: Mode Tabs with skip marking */}
            <div className="flex overflow-x-auto border-b border-zinc-200">
                {MODES.map((mode) => {
                    const skip = SKIP_MODES.critic.includes(mode.id as any);
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
                        <p className="font-medium">该模式跳过评论家</p>
                        <p className="text-sm mt-1">「{MODES.find(m => m.id === activeMode)?.label}」模式不使用 Critic agent。</p>
                    </div>
                ) : (
                    <>
                        <PromptSection
                            label="📝 角色设定 (Role)"
                            value={currentPrompt.role}
                            onChange={(val) => updateCriticPrompt(activeMode, { role: val })}
                            description="定义评论家的审核标准和严厉程度。"
                        />

                        <PromptSection
                            label="🎯 任务描述 (Task)"
                            value={currentPrompt.task}
                            onChange={(val) => updateCriticPrompt(activeMode, { task: val })}
                            description="说明评分维度和点评要求。"
                        />

                        <PromptSection
                            label="✍️ 风格要求 (Style)"
                            value={currentPrompt.style}
                            onChange={(val) => updateCriticPrompt(activeMode, { style: val })}
                            description="点评语言的风格。"
                            optional
                        />

                        <PromptSection
                            label="🚫 禁止事项 (Forbidden)"
                            value={currentPrompt.forbidden}
                            onChange={(val) => updateCriticPrompt(activeMode, { forbidden: val })}
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
                                    Critique Router 逻辑将根据模式自动选择评分维度。
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
                content={getAssembledPrompt('critic', activeMode)}
                title={`完整提示词预览 - 评论家 (${MODES.find(m => m.id === activeMode)?.label})`}
            />
        </div>
    );
}
