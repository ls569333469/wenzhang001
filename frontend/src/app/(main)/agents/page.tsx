'use client';

import { useEffect, useState } from 'react';
import { Users, Brain, Pen, Eye, Sparkles, Settings2 } from 'lucide-react';
import Link from 'next/link';

interface AgentConfig {
    id: string;
    name: string;
    role: string;
    icon: React.ReactNode;
    model: string;
    status: 'active' | 'idle';
    description: string;
}

const AGENTS: AgentConfig[] = [
    {
        id: 'strategist',
        name: '策略师',
        role: 'Strategist',
        icon: <Brain className="w-5 h-5" />,
        model: 'DeepSeek V3',
        status: 'active',
        description: '分析素材，提取关键信息，制定创作策略和角度建议。'
    },
    {
        id: 'writer',
        name: '写手',
        role: 'Writer',
        icon: <Pen className="w-5 h-5" />,
        model: 'DeepSeek V3',
        status: 'active',
        description: '根据选定的策略和风格，撰写初稿内容。'
    },
    {
        id: 'critic',
        name: '评论家',
        role: 'Critic',
        icon: <Eye className="w-5 h-5" />,
        model: 'DeepSeek V3',
        status: 'active',
        description: '审核初稿质量，提出修改建议，确保内容符合要求。'
    },
    {
        id: 'polisher',
        name: '润色师',
        role: 'Polisher',
        icon: <Sparkles className="w-5 h-5" />,
        model: 'DeepSeek V3',
        status: 'idle',
        description: '对终稿进行语言润色，优化表达和可读性。'
    }
];

export default function AgentsPage() {
    const [agents, setAgents] = useState<AgentConfig[]>(AGENTS);
    const [currentModel, setCurrentModel] = useState<string>('');

    useEffect(() => {
        // Load model from localStorage
        const storedModel = localStorage.getItem('qs_model');
        if (storedModel) {
            setCurrentModel(storedModel);
            // Update all agents with the stored model
            setAgents(prev => prev.map(agent => ({
                ...agent,
                model: storedModel === 'deepseek-chat' ? 'DeepSeek V3' : storedModel
            })));
        }
    }, []);

    return (
        <div className="min-h-screen bg-paper">
            <div className="max-w-4xl mx-auto px-8 py-16 space-y-8">
                {/* Header */}
                <header className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-zinc-200 flex items-center justify-center">
                            <Users className="w-5 h-5 text-ink-primary" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-serif font-medium text-ink-primary">智能体团队</h1>
                            <p className="text-sm text-ink-muted">查看和管理 AI 写作团队成员</p>
                        </div>
                    </div>
                    <Link
                        href="/settings"
                        className="flex items-center gap-2 text-sm text-ink-muted hover:text-ink-primary transition-colors"
                    >
                        <Settings2 className="w-4 h-4" />
                        配置模型
                    </Link>
                </header>

                {/* Agent Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {agents.map((agent) => (
                        <div
                            key={agent.id}
                            className="bg-white rounded-2xl border border-zinc-100 p-6 hover:shadow-lg transition-shadow"
                        >
                            {/* Agent Header */}
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${agent.status === 'active'
                                            ? 'bg-emerald-50 text-emerald-600'
                                            : 'bg-zinc-50 text-zinc-400'
                                        }`}>
                                        {agent.icon}
                                    </div>
                                    <div>
                                        <h3 className="font-serif font-bold text-lg text-ink-primary">
                                            {agent.name}
                                        </h3>
                                        <p className="text-xs text-ink-muted font-mono">{agent.role}</p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-[10px] font-semibold uppercase ${agent.status === 'active'
                                        ? 'bg-emerald-100 text-emerald-700'
                                        : 'bg-zinc-100 text-zinc-500'
                                    }`}>
                                    {agent.status === 'active' ? '活跃' : '待命'}
                                </span>
                            </div>

                            {/* Description */}
                            <p className="text-sm text-ink-secondary mb-4 leading-relaxed">
                                {agent.description}
                            </p>

                            {/* Model Badge */}
                            <div className="flex items-center gap-2 pt-4 border-t border-zinc-100">
                                <span className="text-xs text-ink-muted">模型:</span>
                                <span className="px-2 py-1 bg-zinc-50 rounded-lg text-xs font-mono text-ink-primary">
                                    {agent.model}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Team Summary */}
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-6">
                    <h3 className="font-serif font-bold text-ink-primary mb-2">团队协作流程</h3>
                    <p className="text-sm text-ink-secondary">
                        策略师 → 写手 → 评论家 → (修改循环) → 润色师 → 最终稿
                    </p>
                </div>
            </div>
        </div>
    );
}
