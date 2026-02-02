/**
 * P14-C: 模式专属 Writer 配置组件
 * 
 * 为每个创作模式配置专用的 Writer 模型
 */

import React from 'react';
import { useModeWriterStore } from '../agent/stores/useModeWriterStore';
import { PROVIDER_IDS, ModeWriterConfig as ModeWriterConfigType } from '../studio/schema';
import { Zap, FileText, BookOpen, GraduationCap, RefreshCcw, PenTool, AlertTriangle } from 'lucide-react';

// P14-C: 模式定义
const MODE_DEFINITIONS: { id: keyof ModeWriterConfigType; name: string; icon: React.ReactNode; desc: string }[] = [
    { id: 'hot_take', name: '锐评', icon: <Zap className="w-4 h-4" />, desc: '快速锐评，生成3条候选 (50-150字)' },
    { id: 'deep_analysis', name: '深度分析', icon: <BookOpen className="w-4 h-4" />, desc: '全面深度分析 (1200字左右)' },
    { id: 'quick_summary', name: '快讯速评', icon: <FileText className="w-4 h-4" />, desc: '快速产出要点 (500字左右)' },
    { id: 'tutorial', name: '教程指南', icon: <GraduationCap className="w-4 h-4" />, desc: '结构化教程，步骤清晰' },
    { id: 'rewrite', name: '改写润色', icon: <RefreshCcw className="w-4 h-4" />, desc: '基于原文改写润色' },
];

// 复用 AgentModelConfig 的模型列表
const PROVIDER_MODELS = {
    [PROVIDER_IDS.VOLCENGINE]: [
        { id: 'doubao-seed-1-8-251228', name: '豆包 Seed 1.8', description: '快速/创意强' },
        { id: 'deepseek-v3-2-251201', name: 'DeepSeek V3.2', description: '深度推理/联网' },
        { id: 'doubao-1.5-pro-32k-250115', name: '豆包 1.5 Pro 32K', description: '长文本' },
    ],
    [PROVIDER_IDS.GOOGLE]: [
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: '快速' },
        { id: 'gemini-3-pro-preview', name: 'Gemini 3 Pro', description: '专业' },
    ]
};

const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
    [PROVIDER_IDS.VOLCENGINE]: '火山引擎',
    [PROVIDER_IDS.GOOGLE]: 'Google',
};

interface ModeWriterConfigProps {
    apiKeys: Record<string, string>;
}

export const ModeWriterConfig: React.FC<ModeWriterConfigProps> = ({ apiKeys }) => {
    const { writers, updateWriter } = useModeWriterStore();

    return (
        <div className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
            <div className="flex items-start gap-3">
                <div className="p-2 bg-orange-50 rounded-lg text-orange-600">
                    <PenTool className="w-5 h-5" />
                </div>
                <div>
                    <h2 className="text-lg font-medium text-ink-primary">模式专属 Writer 配置</h2>
                    <p className="text-sm text-ink-muted">为每个创作模式配置最合适的 Writer 模型。</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {MODE_DEFINITIONS.map((mode) => {
                    const currentSetting = writers[mode.id];
                    const validProviders = Object.values(PROVIDER_IDS);
                    const selectedProvider = validProviders.includes(currentSetting.provider as any)
                        ? currentSetting.provider
                        : PROVIDER_IDS.VOLCENGINE;

                    const models = PROVIDER_MODELS[selectedProvider as keyof typeof PROVIDER_MODELS] || [];
                    const hasKey = !!apiKeys[selectedProvider];

                    return (
                        <div
                            key={mode.id}
                            className="bg-zinc-50 rounded-xl p-4 border border-zinc-100 hover:border-zinc-200 transition-colors"
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-orange-500">{mode.icon}</span>
                                <span className="font-medium text-ink-primary">{mode.name}</span>
                                {!hasKey && (
                                    <span title="未配置 API Key">
                                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 ml-auto" />
                                    </span>
                                )}
                            </div>
                            <p className="text-xs text-ink-muted mb-3">{mode.desc}</p>

                            <div className="space-y-2">
                                {/* Provider 选择 */}
                                <select
                                    value={selectedProvider}
                                    onChange={(e) => {
                                        const newProvider = e.target.value as 'volcengine' | 'google';
                                        const newModels = PROVIDER_MODELS[newProvider] || [];
                                        updateWriter(mode.id, {
                                            provider: newProvider,
                                            model: newModels[0]?.id || ''
                                        });
                                    }}
                                    className="w-full px-3 py-1.5 text-sm bg-white border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                                >
                                    {validProviders.map((p) => (
                                        <option key={p} value={p}>
                                            {PROVIDER_DISPLAY_NAMES[p] || p}
                                        </option>
                                    ))}
                                </select>

                                {/* Model 选择 */}
                                <select
                                    value={currentSetting.model}
                                    onChange={(e) => updateWriter(mode.id, { model: e.target.value })}
                                    className="w-full px-3 py-1.5 text-sm bg-white border border-zinc-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                                >
                                    {models.map((m) => (
                                        <option key={m.id} value={m.id}>
                                            {m.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="text-xs text-ink-muted bg-zinc-50 rounded-lg p-3">
                <strong>💡 推荐配置:</strong> 锐评/改写 → 豆包 Seed (创意强)，深度分析/教程 → DeepSeek V3.2 (推理强)
            </div>
        </div>
    );
};
