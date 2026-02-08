import React, { useState } from 'react';
import { usePromptStore, WriterPrompts } from '../stores/usePromptStore';
import { PromptSection } from './PromptSection';
import { PromptPreviewModal } from './PromptPreviewModal';
import { RotateCcw, Eye, FileJson } from 'lucide-react';
import { OUTPUT_FORMATS } from '../constants/promptSchemas';
import { DEFAULT_PROMPTS } from '../constants/defaultPrompts';

// Map store keys to display names
const MODES: { id: keyof WriterPrompts; label: string }[] = [
    { id: 'hot_take', label: '锐评 (Hot Take)' },
    { id: 'short_article', label: '短篇 (Short Article)' },
    { id: 'mid_article', label: '中篇 (Mid Article)' },
    { id: 'long_article', label: '长篇 (Long Article)' },
    { id: 'tutorial', label: '教程 (Tutorial)' },
    { id: 'rewrite', label: '改写 (Rewrite)' },
];

export function WriterPromptEditor() {
    const [activeMode, setActiveMode] = useState<keyof WriterPrompts>('hot_take');
    const [showPreview, setShowPreview] = useState(false);

    const writerPrompts = usePromptStore((state) => state.customPrompts.writer);
    const updateWriterPrompt = usePromptStore((state) => state.updateWriterPrompt);
    const getAssembledPrompt = usePromptStore((state) => state.getAssembledPrompt);

    // P22: Defensive fallback - if mode data missing from persisted store, use defaults
    const currentPrompt = writerPrompts[activeMode] || DEFAULT_PROMPTS.writer[activeMode];
    const outputSchema = OUTPUT_FORMATS[activeMode] || '暂无格式定义';

    const handleReset = () => {
        if (confirm('确定要恢复该模式的默认提示词吗？此操作无法撤销。')) {
            const defaultData = DEFAULT_PROMPTS.writer[activeMode];
            updateWriterPrompt(activeMode, defaultData);
        }
    };

    return (
        <div className="space-y-6">
            {/* Mode Tabs */}
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
                    onChange={(val) => updateWriterPrompt(activeMode, { role: val })}
                    description="定义 AI 的身份、语气和专业背景。"
                />

                <PromptSection
                    label="🎯 任务描述 (Task)"
                    value={currentPrompt.task}
                    onChange={(val) => updateWriterPrompt(activeMode, { task: val })}
                    description="具体说明 AI 需要执行的任务步骤。"
                />

                <PromptSection
                    label="✍️ 风格要求 (Style)"
                    value={currentPrompt.style}
                    onChange={(val) => updateWriterPrompt(activeMode, { style: val })}
                    description="规定文风、用词习惯、语气强度等。"
                    optional
                />

                <PromptSection
                    label="🚫 禁止事项 (Forbidden)"
                    value={currentPrompt.forbidden}
                    onChange={(val) => updateWriterPrompt(activeMode, { forbidden: val })}
                    description="明确列出绝对不允许出现的内容或行为。"
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
                            <div className="text-xs font-semibold text-zinc-400 mb-1">📥 素材注入点</div>
                            <div className="font-mono text-xs bg-zinc-200/50 p-2 rounded text-zinc-600">
                                {`{{ raw_input }}`}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs font-semibold text-zinc-400 mb-1">📤 输出格式规范</div>
                            <div className="font-mono text-xs bg-zinc-200/50 p-2 rounded text-zinc-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
                                {outputSchema}
                            </div>
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
                content={getAssembledPrompt('writer', activeMode)}
                title={`完整提示词预览 - ${MODES.find(m => m.id === activeMode)?.label}`}
            />
        </div>
    );
}
