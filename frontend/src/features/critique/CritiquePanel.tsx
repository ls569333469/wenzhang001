/**
 * CritiquePanel - 评审结果面板
 * P14: 完整的评审结果展示组件
 */
import React from 'react';
import { ScoreBadge } from './ScoreBadge';
import { DimensionBar } from './DimensionBar';
import { PenaltyList } from './PenaltyList';
import { SuggestionList } from './SuggestionList';

interface Dimension {
    id: string;
    name: string;
    score: number;
    weight: number;
    reason?: string;
}

interface Penalty {
    item: string;
    points: number;
    detail?: string;
}

interface CritiqueData {
    dimensions: Record<string, { score: number; reason: string }>;
    penalties: Penalty[];
    raw_score: number;
    penalty_total: number;
    total_score: number;
    verdict: 'PASS' | 'REFINE' | 'REWRITE';
    suggestions: string[];
}

interface CritiquePanelProps {
    data: CritiqueData | null;
    isLoading?: boolean;
}

// 维度配置 (从 mode_configs 同步)
const DIMENSION_CONFIG = [
    { id: 'accuracy', name: '语义保真度', weight: 35 },
    { id: 'depth', name: '信息价值', weight: 25 },
    { id: 'logic', name: '逻辑连贯性', weight: 15 },
    { id: 'tone', name: '语言流畅度', weight: 15 },
    { id: 'originality', name: '原创表观度', weight: 10 },
];

export const CritiquePanel: React.FC<CritiquePanelProps> = ({ data, isLoading }) => {
    if (isLoading) {
        return (
            <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 animate-pulse">
                <div className="h-16 w-16 bg-gray-700 rounded-full mx-auto" />
                <div className="mt-4 space-y-2">
                    <div className="h-4 bg-gray-700 rounded w-3/4 mx-auto" />
                    <div className="h-4 bg-gray-700 rounded w-1/2 mx-auto" />
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 text-center text-gray-500">
                等待评审结果...
            </div>
        );
    }

    // 转换维度数据
    const dimensions: Dimension[] = DIMENSION_CONFIG.map((dim) => ({
        ...dim,
        score: data.dimensions[dim.id]?.score || 0,
        reason: data.dimensions[dim.id]?.reason,
    }));

    return (
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 space-y-4">
            {/* 总分 */}
            <div className="flex justify-center">
                <ScoreBadge score={data.total_score} label={data.verdict} size="lg" />
            </div>

            {/* 分数明细 */}
            <div className="flex justify-center gap-4 text-xs text-gray-500">
                <span>初评: {data.raw_score}</span>
                <span>|</span>
                <span className="text-red-400">惩罚: {data.penalty_total}</span>
                <span>|</span>
                <span className="text-green-400">终评: {data.total_score}</span>
            </div>

            <hr className="border-gray-700" />

            {/* 维度评分 */}
            <DimensionBar dimensions={dimensions} />

            <hr className="border-gray-700" />

            {/* 惩罚项 */}
            <PenaltyList penalties={data.penalties} penaltyTotal={data.penalty_total} />

            {/* 建议 */}
            {data.suggestions.length > 0 && (
                <>
                    <hr className="border-gray-700" />
                    <SuggestionList suggestions={data.suggestions} />
                </>
            )}
        </div>
    );
};

export default CritiquePanel;
