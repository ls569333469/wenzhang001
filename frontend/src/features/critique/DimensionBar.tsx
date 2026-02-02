/**
 * DimensionBar - 维度评分条组件
 * P14: CritiquePanel 评分展示
 */
import React from 'react';

interface Dimension {
    id: string;
    name: string;
    score: number;
    weight: number;
    reason?: string;
}

interface DimensionBarProps {
    dimensions: Dimension[];
}

const getBarColor = (score: number): string => {
    if (score >= 9) return 'bg-emerald-500';
    if (score >= 7) return 'bg-green-500';
    if (score >= 5) return 'bg-yellow-500';
    if (score >= 3) return 'bg-orange-500';
    return 'bg-red-500';
};

export const DimensionBar: React.FC<DimensionBarProps> = ({ dimensions }) => {
    return (
        <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-300">📊 维度评分</h4>
            {dimensions.map((dim) => (
                <div key={dim.id} className="space-y-1">
                    <div className="flex justify-between text-xs">
                        <span className="text-gray-400">{dim.name}</span>
                        <span className="text-gray-300 font-mono">
                            {dim.score}/10 ({dim.weight}%)
                        </span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${getBarColor(dim.score)} transition-all duration-300`}
                            style={{ width: `${dim.score * 10}%` }}
                        />
                    </div>
                    {dim.reason && (
                        <p className="text-xs text-gray-500 italic pl-2">
                            {dim.reason}
                        </p>
                    )}
                </div>
            ))}
        </div>
    );
};

export default DimensionBar;
