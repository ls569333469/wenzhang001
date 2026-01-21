'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Check, Edit2, Sparkles } from 'lucide-react';

export interface TitleCandidate {
    title: string;
    formula_tags: string[];
    hook_score: number;
    rationale?: string;
}

interface TitleSelectorProps {
    candidates: TitleCandidate[];
    selectedTitle: string;
    onSelectTitle: (title: string) => void;
    className?: string;
}

// 公式标签颜色映射
const formulaColors: Record<string, string> = {
    '数字法则': 'bg-blue-100 text-blue-700',
    '悬念法则': 'bg-purple-100 text-purple-700',
    '痛点共鸣': 'bg-red-100 text-red-700',
    'FOMO情绪': 'bg-orange-100 text-orange-700',
    '争议性': 'bg-amber-100 text-amber-700',
};

/**
 * TitleSelector - 标题AB测试选择组件
 * 
 * P10-1: 显示3-5个备选标题，每个附带爆款公式分析
 */
export function TitleSelector({
    candidates,
    selectedTitle,
    onSelectTitle,
    className
}: TitleSelectorProps) {
    const [editingIndex, setEditingIndex] = useState<number | null>(null);
    const [editValue, setEditValue] = useState('');

    if (!candidates || candidates.length === 0) {
        return null;
    }

    const handleEditStart = (index: number, title: string) => {
        setEditingIndex(index);
        setEditValue(title);
    };

    const handleEditConfirm = () => {
        if (editValue.trim() && editingIndex !== null) {
            onSelectTitle(editValue.trim());
        }
        setEditingIndex(null);
        setEditValue('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleEditConfirm();
        } else if (e.key === 'Escape') {
            setEditingIndex(null);
            setEditValue('');
        }
    };

    return (
        <div className={cn("space-y-3", className)}>
            {/* 标题 */}
            <div className="flex items-center gap-2 text-sm font-medium text-ink-secondary">
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span>选择标题 (爆款公式分析)</span>
            </div>

            {/* 标题卡片列表 */}
            <div className="space-y-2">
                {candidates.map((candidate, index) => {
                    const isSelected = selectedTitle === candidate.title;
                    const isEditing = editingIndex === index;

                    return (
                        <div
                            key={index}
                            className={cn(
                                "relative p-3 rounded-xl border transition-all cursor-pointer",
                                isSelected
                                    ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                                    : "border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
                            )}
                            onClick={() => !isEditing && onSelectTitle(candidate.title)}
                        >
                            {/* 标题文本 / 编辑框 */}
                            {isEditing ? (
                                <input
                                    type="text"
                                    value={editValue}
                                    onChange={(e) => setEditValue(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    onBlur={handleEditConfirm}
                                    className="w-full px-2 py-1 text-sm font-medium border border-primary rounded focus:outline-none focus:ring-2 focus:ring-primary/20"
                                    autoFocus
                                    onClick={(e) => e.stopPropagation()}
                                />
                            ) : (
                                <div className="flex items-start justify-between gap-2">
                                    <p className="text-sm font-medium text-ink-primary leading-relaxed">
                                        {candidate.title}
                                    </p>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleEditStart(index, candidate.title);
                                        }}
                                        className="p-1 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded transition-colors"
                                        title="编辑标题"
                                    >
                                        <Edit2 className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            )}

                            {/* 公式标签 + 评分 */}
                            <div className="flex items-center gap-2 mt-2 flex-wrap">
                                {candidate.formula_tags.map((tag, tagIndex) => (
                                    <span
                                        key={tagIndex}
                                        className={cn(
                                            "px-2 py-0.5 text-xs font-medium rounded-full",
                                            formulaColors[tag] || "bg-zinc-100 text-zinc-600"
                                        )}
                                    >
                                        {tag}
                                    </span>
                                ))}

                                {/* Hook 评分 */}
                                <div className="flex items-center gap-1 ml-auto">
                                    <span className="text-xs text-zinc-400">Hook强度</span>
                                    <div className="w-16 h-1.5 bg-zinc-200 rounded-full overflow-hidden">
                                        <div
                                            className={cn(
                                                "h-full rounded-full transition-all",
                                                candidate.hook_score >= 80
                                                    ? "bg-green-500"
                                                    : candidate.hook_score >= 60
                                                        ? "bg-amber-500"
                                                        : "bg-red-500"
                                            )}
                                            style={{ width: `${candidate.hook_score}%` }}
                                        />
                                    </div>
                                    <span className="text-xs font-medium text-zinc-600">
                                        {candidate.hook_score}
                                    </span>
                                </div>
                            </div>

                            {/* 分析理由 */}
                            {candidate.rationale && (
                                <p className="mt-1.5 text-xs text-zinc-500">
                                    💡 {candidate.rationale}
                                </p>
                            )}

                            {/* 选中标记 */}
                            {isSelected && (
                                <div className="absolute -top-1 -right-1 w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                                    <Check className="w-3 h-3 text-white" />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
