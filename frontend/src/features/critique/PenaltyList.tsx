/**
 * PenaltyList - 惩罚项列表组件
 * P14: CritiquePanel 评分展示
 */
import React from 'react';

interface Penalty {
    item: string;
    points: number;
    detail?: string;
}

interface PenaltyListProps {
    penalties: Penalty[];
    penaltyTotal: number;
}

export const PenaltyList: React.FC<PenaltyListProps> = ({ penalties, penaltyTotal }) => {
    if (penalties.length === 0) {
        return (
            <div className="text-sm text-gray-500 italic">
                ✅ 无惩罚项
            </div>
        );
    }

    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium text-gray-300">⚠️ 惩罚项</h4>
                <span className="text-sm font-mono text-red-400">
                    {penaltyTotal > 0 ? '+' : ''}{penaltyTotal}分
                </span>
            </div>
            <ul className="space-y-1">
                {penalties.map((penalty, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                        <span className="text-red-400 font-mono shrink-0">
                            {penalty.points}分
                        </span>
                        <div className="flex-1">
                            <span className="text-gray-300">{penalty.item}</span>
                            {penalty.detail && (
                                <p className="text-xs text-gray-500 mt-0.5">{penalty.detail}</p>
                            )}
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default PenaltyList;
