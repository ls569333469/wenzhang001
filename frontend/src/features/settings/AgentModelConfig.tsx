import React, { useState } from 'react';
import { useAgentModelStore } from '../agent/stores/useAgentModelStore';
import { useModeWriterStore } from '../agent/stores/useModeWriterStore';
import { PROVIDER_IDS, AgentModels, ModeWriterConfig as ModeWriterConfigType } from '../studio/schema';
import { Brain, PenTool, Eye, Sparkles, AlertTriangle, Zap, FileText, BookOpen, GraduationCap, RefreshCcw, Check, ChevronRight, Settings2, MessageSquare } from 'lucide-react';
import { ConfigModal } from '@/components/ui/ConfigModal';

// P14-B: 支持的模型列表
const PROVIDER_MODELS = {
    [PROVIDER_IDS.VOLCENGINE]: [
        { id: 'doubao-seed-1-8-251228', name: '豆包 Seed 1.8', description: '通用任务/多模态 (推荐)' },
        { id: 'deepseek-v3-2-251201', name: 'DeepSeek V3.2', description: '深度推理/联网搜索' },
        { id: 'doubao-1.5-pro-32k-250115', name: '豆包 1.5 Pro 32K', description: '长文本专用' },
    ],
    [PROVIDER_IDS.GOOGLE]: [
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', description: '最新快速模型' },
        { id: 'gemini-3-pro-preview', name: 'Gemini 3 Pro Preview', description: '预览版专业模型' },
    ]
};

// P14-C: 模式定义
const MODE_DEFINITIONS: { id: keyof ModeWriterConfigType; name: string; icon: React.ReactNode; recommended: string }[] = [
    { id: 'hot_take', name: '锐评', icon: <Zap className="w-4 h-4" />, recommended: '豆包 Seed' },
    { id: 'short_article', name: '短篇', icon: <MessageSquare className="w-4 h-4" />, recommended: '豆包 Seed' },
    { id: 'mid_article', name: '中篇', icon: <FileText className="w-4 h-4" />, recommended: 'DeepSeek' },
    { id: 'long_article', name: '长篇', icon: <BookOpen className="w-4 h-4" />, recommended: 'DeepSeek' },
    { id: 'tutorial', name: '教程指南', icon: <GraduationCap className="w-4 h-4" />, recommended: 'DeepSeek' },
    { id: 'rewrite', name: '改写润色', icon: <RefreshCcw className="w-4 h-4" />, recommended: '豆包 Seed' },
];

const AGENT_ROLES: { id: keyof AgentModels; label: string; icon: React.ReactNode; desc: string; color: string }[] = [
    { id: 'strategist', label: '策略师', icon: <Brain className="w-5 h-5" />, desc: '负责分析素材、制定大纲。', color: 'text-purple-600 bg-purple-50' },
    { id: 'writer', label: '写手', icon: <PenTool className="w-5 h-5" />, desc: '按模式独立配置', color: 'text-orange-600 bg-orange-50' },
    { id: 'critic', label: '评论家', icon: <Eye className="w-5 h-5" />, desc: '负责评分和提出修改建议。', color: 'text-blue-600 bg-blue-50' },
    { id: 'polisher', label: '润色师', icon: <Sparkles className="w-5 h-5" />, desc: '负责最终润色。', color: 'text-pink-600 bg-pink-50' },
];

const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
    [PROVIDER_IDS.VOLCENGINE]: '火山引擎',
    [PROVIDER_IDS.GOOGLE]: 'Google Gemini',
};

interface AgentModelConfigProps {
    apiKeys: Record<string, string>;
}

export const AgentModelConfig: React.FC<AgentModelConfigProps> = ({ apiKeys }) => {
    const { models, updateModel } = useAgentModelStore();
    const { writers, updateWriter } = useModeWriterStore();

    // State for managing active modal
    const [activeRole, setActiveRole] = useState<keyof AgentModels | null>(null);

    const validProviders = Object.values(PROVIDER_IDS);

    // Helpers
    const getModelName = (provider: string, modelId: string) => {
        const models = PROVIDER_MODELS[provider as keyof typeof PROVIDER_MODELS] || [];
        return models.find(m => m.id === modelId)?.name || modelId || '未选择';
    };

    const handleRoleClick = (roleId: keyof AgentModels) => {
        setActiveRole(roleId);
    };

    const closeModal = () => {
        setActiveRole(null);
    };

    // Modal Content: General Role (Strategist, Critic, Polisher)
    const renderGeneralConfig = (roleId: keyof AgentModels) => {
        if (roleId === 'writer') return null;

        const currentSetting = models[roleId];
        const selectedProvider = validProviders.includes(currentSetting.provider as any)
            ? currentSetting.provider
            : PROVIDER_IDS.VOLCENGINE;
        const availableModels = PROVIDER_MODELS[selectedProvider as keyof typeof PROVIDER_MODELS] || [];

        return (
            <div className="space-y-6">
                <div className="p-4 bg-zinc-50 rounded-xl text-sm text-ink-muted">
                    {AGENT_ROLES.find(r => r.id === roleId)?.desc}
                </div>

                <div className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-ink-primary">模型提供商 (Provider)</label>
                        <div className="grid grid-cols-2 gap-3">
                            {validProviders.map(pid => (
                                <button
                                    key={pid}
                                    onClick={() => updateModel(roleId, { provider: pid as any, model: '' })}
                                    className={`relative p-3 rounded-lg border text-left transition-all ${selectedProvider === pid
                                        ? 'border-primary ring-1 ring-primary bg-primary/5'
                                        : 'border-zinc-200 hover:border-zinc-300 bg-white'
                                        }`}
                                >
                                    <div className="font-medium text-sm">{PROVIDER_DISPLAY_NAMES[pid]}</div>
                                    <div className="text-xs text-ink-muted mt-1">
                                        {PROVIDER_MODELS[pid as keyof typeof PROVIDER_MODELS]?.length} 个模型可用
                                    </div>
                                    {selectedProvider === pid && (
                                        <div className="absolute top-2 right-2 text-primary">
                                            <Check className="w-4 h-4" />
                                        </div>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-ink-primary">选择模型 (Model)</label>
                        <div className="space-y-2">
                            {availableModels.map(m => (
                                <button
                                    key={m.id}
                                    onClick={() => updateModel(roleId, { model: m.id })}
                                    className={`w-full p-3 rounded-lg border text-left flex items-center justify-between transition-all ${currentSetting.model === m.id
                                        ? 'border-primary ring-1 ring-primary bg-primary/5'
                                        : 'border-zinc-200 hover:border-zinc-300 bg-white'
                                        }`}
                                >
                                    <div>
                                        <div className="font-medium text-sm">{m.name}</div>
                                        <div className="text-xs text-ink-muted">{m.description}</div>
                                    </div>
                                    {currentSetting.model === m.id && <Check className="w-4 h-4 text-primary" />}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    // Modal Content: Writer Config (List of Modes)
    const renderWriterConfig = () => {
        return (
            <div className="space-y-6">
                <div className="bg-orange-50 p-4 rounded-xl flex items-start gap-3">
                    <div className="p-1 bg-white rounded-full text-orange-500 shadow-sm mt-0.5">
                        <Zap className="w-3.5 h-3.5" />
                    </div>
                    <div>
                        <h4 className="text-sm font-medium text-orange-900">配置指南</h4>
                        <p className="text-xs text-orange-700 mt-1 leading-relaxed">
                            不同的创作模式需要不同的模型能力。建议为<strong>锐评/润色</strong>选择更有创意的模型（如豆包），
                            为<strong>深度分析/教程</strong>选择逻辑推理更强的模型（如 DeepSeek）。
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
                            const config = writers[mode.id];
                            const currentModels = PROVIDER_MODELS[config.provider as keyof typeof PROVIDER_MODELS] || [];

                            return (
                                <div key={mode.id} className="bg-white p-4 grid grid-cols-1 md:grid-cols-12 gap-4 items-center hover:bg-zinc-50 transition-colors">
                                    <div className="col-span-1 md:col-span-4 flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-zinc-100 text-zinc-600">
                                            {mode.icon}
                                        </div>
                                        <div className="font-medium text-zinc-900">{mode.name}</div>
                                    </div>

                                    <div className="col-span-1 md:col-span-8 flex gap-3">
                                        <select
                                            value={config.provider}
                                            onChange={(e) => {
                                                const newP = e.target.value as keyof typeof PROVIDER_MODELS;
                                                const newMs = PROVIDER_MODELS[newP] || [];
                                                updateWriter(mode.id, { provider: newP, model: newMs[0]?.id || '' });
                                            }}
                                            className="w-1/3 px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                                        >
                                            {validProviders.map(p => (
                                                <option key={p} value={p}>{PROVIDER_DISPLAY_NAMES[p]}</option>
                                            ))}
                                        </select>
                                        <select
                                            value={config.model}
                                            onChange={(e) => updateWriter(mode.id, { model: e.target.value })}
                                            className="w-2/3 px-3 py-2 bg-white border border-zinc-200 rounded-lg text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                                        >
                                            {currentModels.map(m => (
                                                <option key={m.id} value={m.id}>{m.name}</option>
                                            ))}
                                        </select>
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
                    <p className="text-sm text-ink-muted">点击下方卡片，为每个智能体角色配置专属模型。</p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
                {AGENT_ROLES.map(role => {
                    const isWriter = role.id === 'writer';
                    const currentModelName = isWriter
                        ? '按 5 种模式独立配置'
                        : getModelName(models[role.id].provider, models[role.id].model);

                    const provider = isWriter ? 'mixed' : models[role.id].provider;
                    const hasKey = isWriter ? true : !!apiKeys[provider]; // Simplify writer check for dashboard

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

                            {!hasKey && (
                                <div className="absolute top-4 right-12 flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                                    <AlertTriangle className="w-3 h-3" />
                                    <span>未配置 Key</span>
                                </div>
                            )}

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
                {activeRole === 'writer' ? renderWriterConfig() : (activeRole && renderGeneralConfig(activeRole))}
            </ConfigModal>
        </div>
    );
};
