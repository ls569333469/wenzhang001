'use client';

import { cn } from '@/lib/utils';
import { Flame } from 'lucide-react';

export interface ViralScore {
    emotion_resonance: number;
    info_density: number;
    call_to_action: number;
    social_currency: number;
    overall: number;
}

interface ViralScoreDisplayProps {
    score: ViralScore;
    compact?: boolean;
    className?: string;
}

// 维度中文映射
const dimensionLabels: Record<string, { label: string; icon: string }> = {
    emotion_resonance: { label: '情绪共鸣', icon: '❤️' },
    info_density: { label: '信息密度', icon: '📊' },
    call_to_action: { label: '行动召唤', icon: '🎯' },
    social_currency: { label: '社交货币', icon: '💎' },
};

// 根据分数获取颜色
function getScoreColor(score: number): string {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-red-400';
}

function getScoreTextColor(score: number): string {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-500';
}

/**
 * ViralScoreDisplay - P10-2 爆款要素评分显示
 * 
 * 显示四维评分：情绪共鸣、信息密度、行动召唤、社交货币
 */
export function ViralScoreDisplay({ score, compact = false, className }: ViralScoreDisplayProps) {
    if (!score) return null;

    // 紧凑模式：只显示总分
    if (compact) {
        return (
            <div className={cn("flex items-center gap-1.5", className)}>
                <Flame className={cn("w-4 h-4", getScoreTextColor(score.overall))} />
                <span className={cn("text-sm font-bold", getScoreTextColor(score.overall))}>
                    {score.overall}
                </span>
                <span className="text-xs text-zinc-400">爆款指数</span>
            </div>
        );
    }

    // 完整模式：显示所有维度
    return (
        <div className={cn("space-y-2", className)}>
            {/* 总分 */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                    <Flame className={cn("w-4 h-4", getScoreTextColor(score.overall))} />
                    <span className="text-xs font-medium text-zinc-500">爆款指数</span>
                </div>
                <span className={cn("text-lg font-bold", getScoreTextColor(score.overall))}>
                    {score.overall}
                </span>
            </div>

            {/* 四维进度条 */}
            <div className="grid grid-cols-2 gap-2">
                {Object.entries(dimensionLabels).map(([key, { label, icon }]) => {
                    const value = score[key as keyof ViralScore] || 0;
                    return (
                        <div key={key} className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-zinc-500">
                                    {icon} {label}
                                </span>
                                <span className="font-medium text-zinc-700">{value}</span>
                            </div>
                            <div className="h-1.5 bg-zinc-100 rounded-full overflow-hidden">
                                <div
                                    className={cn("h-full rounded-full transition-all", getScoreColor(value))}
                                    style={{ width: `${value}%` }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
