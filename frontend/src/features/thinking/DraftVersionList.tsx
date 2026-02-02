/**
 * DraftVersionList - 草稿版本列表
 * P14: 思维链详情展示
 */
import React from 'react';

interface DraftVersion {
    id: string;
    version: number;
    content: string;
    wordCount: number;
    score?: number;
    verdict?: 'PASS' | 'REFINE' | 'REWRITE';
    createdAt: string;
}

interface DraftVersionListProps {
    drafts: DraftVersion[];
    selectedId?: string;
    onSelect: (id: string) => void;
}

const getVerdictColor = (verdict?: string) => {
    if (verdict === 'PASS') return 'text-green-400';
    if (verdict === 'REFINE') return 'text-yellow-400';
    if (verdict === 'REWRITE') return 'text-red-400';
    return 'text-gray-400';
};

export const DraftVersionList: React.FC<DraftVersionListProps> = ({
    drafts,
    selectedId,
    onSelect,
}) => {
    if (drafts.length === 0) {
        return (
            <div className="text-sm text-gray-500 italic p-2">
                暂无草稿版本
            </div>
        );
    }

    return (
        <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-300 px-2">📝 草稿迭代</h4>
            <div className="space-y-1">
                {drafts.map((draft) => (
                    <button
                        key={draft.id}
                        onClick={() => onSelect(draft.id)}
                        className={`w-full p-2 rounded text-left transition-colors ${selectedId === draft.id
                                ? 'bg-blue-600/30 border border-blue-500'
                                : 'bg-gray-800 hover:bg-gray-700 border border-transparent'
                            }`}
                    >
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-200">
                                v{draft.version}
                            </span>
                            {draft.verdict && (
                                <span className={`text-xs font-mono ${getVerdictColor(draft.verdict)}`}>
                                    {draft.score} {draft.verdict}
                                </span>
                            )}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                            {draft.wordCount}字 · {new Date(draft.createdAt).toLocaleTimeString()}
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default DraftVersionList;
