/**
 * DraftDiff - 草稿对比组件
 * P14: 思维链详情展示
 */
import React from 'react';

interface DraftDiffProps {
    oldContent: string;
    newContent: string;
    oldVersion: number;
    newVersion: number;
}

// 简单差异计算 (按行)
const computeDiff = (oldText: string, newText: string) => {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');

    const result: { type: 'same' | 'add' | 'remove'; content: string }[] = [];

    // 简化版本：逐行对比
    const maxLen = Math.max(oldLines.length, newLines.length);

    for (let i = 0; i < maxLen; i++) {
        const oldLine = oldLines[i] || '';
        const newLine = newLines[i] || '';

        if (oldLine === newLine) {
            result.push({ type: 'same', content: newLine });
        } else {
            if (oldLine) result.push({ type: 'remove', content: oldLine });
            if (newLine) result.push({ type: 'add', content: newLine });
        }
    }

    return result;
};

export const DraftDiff: React.FC<DraftDiffProps> = ({
    oldContent,
    newContent,
    oldVersion,
    newVersion,
}) => {
    const diff = computeDiff(oldContent, newContent);

    return (
        <div className="space-y-2">
            <div className="flex justify-between text-xs text-gray-400 px-2">
                <span>v{oldVersion} → v{newVersion}</span>
                <span className="text-gray-500">行变更对比</span>
            </div>
            <div className="bg-gray-900 rounded-lg p-3 text-sm font-mono overflow-auto max-h-96">
                {diff.map((line, idx) => (
                    <div
                        key={idx}
                        className={`py-0.5 px-2 ${line.type === 'add'
                                ? 'bg-green-900/30 text-green-300'
                                : line.type === 'remove'
                                    ? 'bg-red-900/30 text-red-300 line-through'
                                    : 'text-gray-400'
                            }`}
                    >
                        <span className="text-gray-600 mr-2">
                            {line.type === 'add' ? '+' : line.type === 'remove' ? '-' : ' '}
                        </span>
                        {line.content || <span className="text-gray-600">(空行)</span>}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default DraftDiff;
