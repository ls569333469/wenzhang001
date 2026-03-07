import React, { useState } from 'react';
import { usePromptStore } from '../stores/usePromptStore';
import { WriterPromptEditor } from './WriterPromptEditor';
import { StrategistPromptEditor } from './StrategistPromptEditor';
import { CriticPromptEditor } from './CriticPromptEditor';
import { PolisherPromptEditor } from './PolisherPromptEditor';
import { ScoutPromptEditor } from './ScoutPromptEditor';

import { Sparkles, PenTool, MessageSquare, Wand2, Telescope } from 'lucide-react';

const AGENTS = [
    { id: 'strategist', label: '策略师 (Strategist)', icon: Sparkles },
    { id: 'writer', label: '写手 (Writer)', icon: PenTool },
    { id: 'critic', label: '评论家 (Critic)', icon: MessageSquare },
    { id: 'polisher', label: '润色师 (Polisher)', icon: Wand2 },
    { id: 'scout', label: '侦察官 (Scout)', icon: Telescope },
] as const;

export function PromptManager() {
    const [activeAgent, setActiveAgent] = useState<typeof AGENTS[number]['id']>('writer');
    const enabled = usePromptStore((state) => state.customPrompts.enabled);
    const toggleEnabled = usePromptStore((state) => state.toggleEnabled);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between p-4 bg-zinc-50 rounded-xl border border-zinc-200">
                <div>
                    <h3 className="font-medium text-zinc-900">启用自定义提示词</h3>
                    <p className="text-sm text-zinc-500">开启后，系统将优先使用您配置的提示词。关闭则使用官方默认模板。</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${enabled ? 'text-primary' : 'text-zinc-500'}`}>
                        {enabled ? '已启用' : '已禁用'}
                    </span>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input
                            type="checkbox"
                            className="sr-only peer"
                            checked={enabled}
                            onChange={(e) => toggleEnabled(e.target.checked)}
                        />
                        <div className="w-11 h-6 bg-zinc-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                </div>
            </div>

            {/* Main Agent Tabs */}
            <div className="flex overflow-x-auto gap-2 border-b border-zinc-200 pb-1">
                {AGENTS.map((agent) => (
                    <button
                        key={agent.id}
                        onClick={() => setActiveAgent(agent.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors border-b-2 -mb-[5px] ${activeAgent === agent.id
                            ? 'border-primary text-primary bg-zinc-50/50'
                            : 'border-transparent text-zinc-500 hover:text-zinc-700 hover:bg-zinc-50'
                            }`}
                    >
                        <agent.icon className="w-4 h-4" />
                        {agent.label}
                    </button>
                ))}
            </div>

            <div className="bg-white rounded-xl min-h-[400px]">
                {activeAgent === 'writer' && <WriterPromptEditor />}
                {activeAgent === 'strategist' && <StrategistPromptEditor />}
                {activeAgent === 'critic' && <CriticPromptEditor />}
                {activeAgent === 'polisher' && <PolisherPromptEditor />}
                {activeAgent === 'scout' && <ScoutPromptEditor />}
            </div>
        </div>
    );
}
