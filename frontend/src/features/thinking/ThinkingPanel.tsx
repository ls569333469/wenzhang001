/**
 * ThinkingPanel - 思维链面板
 * P14: 展示完整的思考过程和草稿迭代
 */
import React, { useState } from 'react';
import { DraftVersionList } from './DraftVersionList';
import { DraftDiff } from './DraftDiff';

interface ThinkingStep {
    step: string;
    content: string;
}

interface AgentThinking {
    agent: 'strategist' | 'writer' | 'critic' | 'polisher';
    steps: ThinkingStep[];
    status: 'pending' | 'active' | 'completed' | 'error';
}

interface DraftVersion {
    id: string;
    version: number;
    content: string;
    wordCount: number;
    score?: number;
    verdict?: 'PASS' | 'REFINE' | 'REWRITE';
    createdAt: string;
}

interface ThinkingPanelProps {
    thinkingSteps: AgentThinking[];
    drafts: DraftVersion[];
    isExpanded?: boolean;
}

const AGENT_LABELS: Record<string, { label: string; icon: string }> = {
    strategist: { label: '策略分析', icon: '🧭' },
    writer: { label: '内容创作', icon: '✍️' },
    critic: { label: '质量评审', icon: '🔍' },
    polisher: { label: '润色打磨', icon: '✨' },
};

export const ThinkingPanel: React.FC<ThinkingPanelProps> = ({
    thinkingSteps,
    drafts,
    isExpanded = true,
}) => {
    const [selectedDraftId, setSelectedDraftId] = useState<string | null>(null);
    const [showDiff, setShowDiff] = useState(false);

    // 获取选中草稿和前一版本用于对比
    const selectedDraft = drafts.find((d) => d.id === selectedDraftId);
    const selectedIndex = drafts.findIndex((d) => d.id === selectedDraftId);
    const prevDraft = selectedIndex > 0 ? drafts[selectedIndex - 1] : null;

    if (!isExpanded) {
        return (
            <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700 text-center text-sm text-gray-500">
                点击展开思维链详情
            </div>
        );
    }

    return (
        <div className="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
            {/* Agent 步骤展示 */}
            <div className="p-4 border-b border-gray-700">
                <h3 className="text-sm font-medium text-gray-200 mb-3">🧠 思考过程</h3>
                <div className="space-y-3">
                    {thinkingSteps.map((agent, idx) => {
                        const agentInfo = AGENT_LABELS[agent.agent] || { label: agent.agent, icon: '🤖' };

                        return (
                            <div key={idx} className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <span>{agentInfo.icon}</span>
                                    <span className="text-sm text-gray-300">{agentInfo.label}</span>
                                    <span className={`text-xs px-1.5 py-0.5 rounded ${agent.status === 'completed' ? 'bg-green-600/30 text-green-400' :
                                            agent.status === 'active' ? 'bg-blue-600/30 text-blue-400' :
                                                agent.status === 'error' ? 'bg-red-600/30 text-red-400' :
                                                    'bg-gray-600/30 text-gray-400'
                                        }`}>
                                        {agent.status}
                                    </span>
                                </div>
                                {agent.steps.length > 0 && (
                                    <ul className="ml-6 text-xs text-gray-500 space-y-0.5">
                                        {agent.steps.map((step, sIdx) => (
                                            <li key={sIdx}>• {step.content}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* 草稿版本 */}
            {drafts.length > 0 && (
                <div className="p-4">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-400">共 {drafts.length} 个版本</span>
                        {prevDraft && selectedDraft && (
                            <button
                                onClick={() => setShowDiff(!showDiff)}
                                className="text-xs text-blue-400 hover:text-blue-300"
                            >
                                {showDiff ? '隐藏对比' : '显示对比'}
                            </button>
                        )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <DraftVersionList
                            drafts={drafts}
                            selectedId={selectedDraftId || undefined}
                            onSelect={setSelectedDraftId}
                        />

                        <div className="text-sm text-gray-400">
                            {selectedDraft ? (
                                showDiff && prevDraft ? (
                                    <DraftDiff
                                        oldContent={prevDraft.content}
                                        newContent={selectedDraft.content}
                                        oldVersion={prevDraft.version}
                                        newVersion={selectedDraft.version}
                                    />
                                ) : (
                                    <div className="bg-gray-900 rounded-lg p-3 max-h-64 overflow-auto">
                                        <pre className="whitespace-pre-wrap text-xs">{selectedDraft.content}</pre>
                                    </div>
                                )
                            ) : (
                                <div className="text-center py-8 text-gray-500">
                                    选择版本查看详情
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ThinkingPanel;
