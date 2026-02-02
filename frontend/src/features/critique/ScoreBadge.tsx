/**
 * ScoreBadge - 评分徽章组件
 * P14: CritiquePanel 评分展示
 */
import React from 'react';

interface ScoreBadgeProps {
    score: number;
    label?: string;
    size?: 'sm' | 'md' | 'lg';
}

const getScoreColor = (score: number): string => {
    if (score >= 90) return 'bg-emerald-500';
    if (score >= 85) return 'bg-green-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
};

const getScoreLabel = (score: number): string => {
    if (score >= 90) return 'PASS';
    if (score >= 70) return 'REFINE';
    return 'REWRITE';
};

export const ScoreBadge: React.FC<ScoreBadgeProps> = ({
    score,
    label,
    size = 'md'
}) => {
    const sizeClasses = {
        sm: 'w-12 h-12 text-lg',
        md: 'w-16 h-16 text-xl',
        lg: 'w-20 h-20 text-2xl'
    };

    return (
        <div className="flex flex-col items-center gap-1">
            <div
                className={`${sizeClasses[size]} ${getScoreColor(score)} rounded-full flex items-center justify-center text-white font-bold shadow-lg`}
            >
                {score}
            </div>
            <span className="text-xs text-gray-400 uppercase tracking-wide">
                {label || getScoreLabel(score)}
            </span>
        </div>
    );
};

export default ScoreBadge;
