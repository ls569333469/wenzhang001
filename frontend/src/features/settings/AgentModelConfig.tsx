import React, { useState } from 'react';
import { useAgentModelStore } from '../agent/stores/useAgentModelStore';
import { useModeWriterStore } from '../agent/stores/useModeWriterStore';
import { useModeStrategistStore } from '../agent/stores/useModeStrategistStore';
import { useModeCriticStore } from '../agent/stores/useModeCriticStore';
import { useModePolisherStore } from '../agent/stores/useModePolisherStore';
import {
    PROVIDER_IDS, AgentModels, ModeWriterConfig as ModeWriterConfigType,
    ModeStrategistConfig, ModeCriticConfig, ModePolisherConfig,
    SKIP_MODES, AgentModelSetting
} from '../studio/schema';
import { Brain, PenTool, Eye, Sparkles, AlertTriangle, Zap, FileText, BookOpen, GraduationCap, RefreshCcw, Check, ChevronRight, Settings2, MessageSquare, SkipForward, Heart, Target, Search } from 'lucide-react';
import { ConfigModal } from '@/components/ui/ConfigModal';

// P14-B: 支持的模型列表
const PROVIDER_MODELS = {
    [PROVIDER_IDS.VOLCENGINE]: [
        { id: 'doubao-seed-2-0-lite-260215', name: '豆包 Seed 2.0 Lite', description: '通用任务/多模态 (推荐)' },
        { id: 'deepseek-v3-2-251201', name: 'DeepSeek V3.2', description: '深度推理/联网搜索' },
        { id: 'doubao-1.5-pro-32k-250115', name: '豆包 1.5 Pro 32K', description: '长文本专用' },
    ],
    [PROVIDER_IDS.GOOGLE]: [
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: '最新快速模型' },
        { id: 'gemini-3-pro-preview', name: 'Gemini 3 Pro Preview', description: '预览版专业模型' },
    ]
};

// P27: 统一 8 模式定义
const MODE_DEFINITIONS: { id: string; name: string; icon: React.ReactNode }[] = [
    { id: 'hot_take', name: '锐评', icon: <Zap className="w-4 h-4" /> },
    { id: 'bullish_take', name: '吹捧', icon: <Heart className="w-4 h-4" /> },
    { id: 'kaito_yap', name: 'Kaito', icon: <Target className="w-4 h-4" /> },
    { id: 'short_article', name: '短篇', icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'mid_article', name: '中篇', icon: <FileText className="w-4 h-4" /> },
    { id: 'long_article', name: '长篇', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'tutorial', name: '教程指南', icon: <GraduationCap className="w-4 h-4" /> },
    { id: 'project_research', name: '投研', icon: <Search className="w-4 h-4" /> },
];

const AGENT_ROLES: { id: keyof AgentModels; label: string; icon: React.ReactNode; desc: string; color: string; accentBg: string; accentText: string; accentIcon: React.ReactNode }[] = [
    { id: 'strategist', label: '策略师', icon: <Brain className="w-5 h-5" />, desc: 'P24-D: 按 8 种模式独立配置', color: 'text-purple-600 bg-purple-50', accentBg: 'bg-purple-50', accentText: 'text-purple-700', accentIcon: <Brain className="w-3.5 h-3.5" /> },
    { id: 'writer', label: '写手', icon: <PenTool className="w-5 h-5" />, desc: 'P24-D: 按 8 种模式独立配置', color: 'text-orange-600 bg-orange-50', accentBg: 'bg-orange-50', accentText: 'text-orange-700', accentIcon: <PenTool className="w-3.5 h-3.5" /> },
    { id: 'critic', label: '评论家', icon: <Eye className="w-5 h-5" />, desc: 'P24-D: 按 8 种模式独立配置', color: 'text-blue-600 bg-blue-50', accentBg: 'bg-blue-50', accentText: 'text-blue-700', accentIcon: <Eye className="w-3.5 h-3.5" /> },
    { id: 'polisher', label: '润色师', icon: <Sparkles className="w-5 h-5" />, desc: 'P24-D: 按 8 种模式独立配置', color: 'text-pink-600 bg-pink-50', accentBg: 'bg-pink-50', accentText: 'text-pink-700', accentIcon: <Sparkles className="w-3.5 h-3.5" /> },
];

const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
    [PROVIDER_IDS.VOLCENGINE]: '火山引擎',
    [PROVIDER_IDS.GOOGLE]: 'Google Gemini',
};

interface AgentModelConfigProps {
    apiKeys: Record<string, string>;
}

export const AgentModelConfig: React.FC<AgentModelConfigProps> = ({ apiKeys }) => {
    const { models } = useAgentModelStore();
    const { writers, updateWriter } = useModeWriterStore();
    const { strategists, updateStrategist } = useModeStrategistStore();
    const { critics, updateCritic } = useModeCriticStore();
    const { polishers, updatePolisher } = useModePolisherStore();

    // State for managing active modal
    const [activeRole, setActiveRole] = useState<keyof AgentModels | null>(null);

    const validProviders = Object.values(PROVIDER_IDS);

    const handleRoleClick = (roleId: keyof AgentModels) => {
        setActiveRole(roleId);
    };

    const closeModal = () => {
        setActiveRole(null);
    };

    // P24-D: 获取指定 agent 的 per-mode 配置和更新函数
    const getAgentModeConfig = (agentId: keyof AgentModels) => {
        switch (agentId) {
            case 'strategist':
                return { configs: strategists, update: updateStrategist as (mode: string, setting: Partial<AgentModelSetting>) => void };
            case 'writer':
                return { configs: writers, update: updateWriter as (mode: string, setting: Partial<AgentModelSetting>) => void };
            case 'critic':
                return { configs: critics, update: updateCritic as (mode: string, setting: Partial<AgentModelSetting>) => void };
            case 'polisher':
                return { configs: polishers, update: updatePolisher as (mode: string, setting: Partial<AgentModelSetting>) => void };
            default:
                return { configs: writers, update: updateWriter as (mode: string, setting: Partial<AgentModelSetting>) => void };
        }
    };

    // P24-D: 统一的 per-mode 配置渲染
    const renderPerModeConfig = (agentId: keyof AgentModels) => {
        const role = AGENT_ROLES.find(r => r.id === agentId)!;
        const { configs, update } = getAgentModeConfig(agentId);
        const skipModes = SKIP_MODES[agentId] || [];

        return (
            <div className="space-y-6">
                <div className={`${role.accentBg} p-4 rounded-xl flex items-start gap-3`}>
                    <div className="p-1 bg-white rounded-full shadow-sm mt-0.5" style={{ color: 'inherit' }}>
                        <div className={role.accentText}>{role.accentIcon}</div>
                    </div>
                    <div>
                        <h4 className={`text-sm font-medium ${role.accentText.replace('text-', 'text-').replace('-700', '-900')}`}>
                            {role.label} — 模式专属模型配置
                        </h4>
                        <p className={`text-xs ${role.accentText} mt-1 leading-relaxed`}>
                            每个创作模式可独立选择模型。
                            {skipModes.length > 0 && (
                                <>标记为 <strong>⏭️ 跳过</strong> 的模式不参与该 agent 流程。</>
                            )}
                        </p>
                    </div>
                </div>

                <div className="space-y-3">
                    <div className="grid grid-cols-12 px-3 text-xs font-medium text-ink-muted uppercase tracking-wider">
                        <div className="col-span-4">创作模式</div>
                        <div className="col-span-8">模型配置</div>
                    </div>

                    <div className="divide-y divide-zinc-100 border border-zinc-200 rounded-xl overflow-hidden">
                        {MODE_DEFINITIONS.map(mode => {
                            const isSkipped = (skipModes as readonly string[]).includes(mode.id);
                            const config = (configs as any)[mode.id] as AgentModelSetting;
                            const currentModels = PROVIDER_MODELS[config?.provider as keyof typeof PROVIDER_MODELS] || [];

                            return (
                                <div
                                    key={mode.id}
                                    className={`p-4 grid grid-cols-1 md:grid-cols-12 gap-4 items-center transition-colors ${isSkipped ? 'bg-zinc-50 opacity-60' : 'bg-white hover:bg-zinc-50'
                                        }`}
                                >
                                    <div className="col-span-1 md:col-span-4 flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${isSkipped ? 'bg-zinc-200 text-zinc-400' : 'bg-zinc-100 text-zinc-600'}`}>
                                            {mode.icon}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className={`font-medium ${isSkipped ? 'text-zinc-400' : 'text-zinc-900'}`}>{mode.name}</span>
                                            {isSkipped && (
                                                <span className="inline-flex items-center gap-1 text-xs text-zinc-400 bg-zinc-100 px-2 py-0.5 rounded-full">
                                                    <SkipForward className="w-3 h-3" />跳过
                                                </span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="col-span-1 md:col-span-8 flex gap-3">
                                        {isSkipped ? (
                                            <div className="w-full px-3 py-2 bg-zinc-100 border border-zinc-200 rounded-lg text-sm text-zinc-400">
                                                该模式不使用{role.label}
                                            </div>
                                        ) : (
                                            <>
                                                <select
                                                    value={config?.provider || ''}
                                                    onChange={(e) => {
                                                        const newP = e.target.value as keyof typeof PROVIDER_MODELS;
                                                        const newMs = PROVIDER_MODELS[newP] || [];
                                                        update(mode.id, { provider: newP, model: newMs[0]?.id || '' });
                                                    }}
                                                    className="w-1/3 px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                                                >
                                                    {validProviders.map(p => (
                                                        <option key={p} value={p}>{PROVIDER_DISPLAY_NAMES[p]}</option>
                                                    ))}
                                                </select>
                                                <select
                                                    value={config?.model || ''}
                                                    onChange={(e) => update(mode.id, { model: e.target.value })}
                                                    className="w-2/3 px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                                                >
                                                    {currentModels.map(m => (
                                                        <option key={m.id} value={m.id}>{m.name}</option>
                                                    ))}
                                                </select>
                                            </>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        );
    };

    // Dashboard Cards Render
    return (
        <div className="space-y-6">
            <div className="flex items-start gap-3 px-1">
                <div className="p-2 bg-white shadow-sm border border-zinc-200 rounded-lg text-zinc-700">
                    <Settings2 className="w-5 h-5" />
                </div>
                <div>
                    <h2 className="text-lg font-medium text-ink-primary">智能体模型配置</h2>
                    <p className="text-sm text-ink-muted">点击下方卡片，为每个智能体角色配置专属模型。所有 agent 均按 6 种模式独立配置。</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                {AGENT_ROLES.map(role => {
                    const skipCount = (SKIP_MODES[role.id] || []).length;
                    const activeCount = 8 - skipCount;
                    const currentModelName = `按 ${activeCount} 种模式独立配置${skipCount > 0 ? ` (${skipCount} 种跳过)` : ''}`;

                    return (
                        <div
                            key={role.id}
                            onClick={() => handleRoleClick(role.id)}
                            className="group relative bg-white p-5 rounded-2xl border border-zinc-200 shadow-sm hover:shadow-md hover:border-zinc-300 transition-all cursor-pointer overflow-hidden"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-4">
                                    <div className={`p-3 rounded-xl ${role.color} transition-transform group-hover:scale-110`}>
                                        {role.icon}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-zinc-900">{role.label} ({role.id})</h3>
                                        <p className="text-sm text-zinc-500 mt-0.5 max-w-[200px] truncate">
                                            {currentModelName}
                                        </p>
                                    </div>
                                </div>
                                <div className="p-2 text-zinc-300 group-hover:text-primary transition-colors">
                                    <ChevronRight className="w-5 h-5" />
                                </div>
                            </div>

                            {/* Active Indicator on hover */}
                            <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-transparent via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                    );
                })}
            </div>

            {/* Configuration Modal */}
            <ConfigModal
                isOpen={!!activeRole}
                onClose={closeModal}
                title={activeRole ? AGENT_ROLES.find(r => r.id === activeRole)?.label + ' 配置' || '' : ''}
                description={activeRole ? AGENT_ROLES.find(r => r.id === activeRole)?.desc : ''}
                icon={activeRole ? AGENT_ROLES.find(r => r.id === activeRole)?.icon : null}
            >
                {activeRole && renderPerModeConfig(activeRole)}
            </ConfigModal>
        </div>
    );
};
