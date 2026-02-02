/**
 * SuggestionList - 建议列表组件
 * P14: CritiquePanel 评分展示
 */
import React from 'react';

interface SuggestionListProps {
    suggestions: string[];
}

export const SuggestionList: React.FC<SuggestionListProps> = ({ suggestions }) => {
    if (suggestions.length === 0) {
        return null;
    }

    return (
        <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-300">💡 改进建议</h4>
            <ul className="space-y-1.5">
                {suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-400">
                        <span className="text-blue-400 shrink-0">•</span>
                        <span>{suggestion}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default SuggestionList;
