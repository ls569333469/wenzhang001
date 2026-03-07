'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { RotateCcw, Save, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';

/**
 * P32-C: 投研智能体 Prompt 编辑器
 * 
 * 从后端 GET /api/research/prompts 动态加载所有投研智能体，
 * 支持切换 Tab 编辑各个智能体的 Jinja2 模板。
 * POST /api/research/prompts/{agent_name} 保存。
 */

interface AgentPrompt {
    label: string;
    content: string;
}

export function ScoutPromptEditor() {
    const [agents, setAgents] = useState<Record<string, AgentPrompt>>({});
    const [activeAgent, setActiveAgent] = useState<string>('');
    const [content, setContent] = useState('');
    const [originalContents, setOriginalContents] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

    const fetchPrompts = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE_URL}/api/research/prompts`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setAgents(data);

            // 保存原始内容用于检测变更
            const originals: Record<string, string> = {};
            Object.entries(data).forEach(([key, val]: [string, any]) => {
                originals[key] = val.content || '';
            });
            setOriginalContents(originals);

            // 设置默认选中第一个智能体
            const keys = Object.keys(data);
            if (keys.length > 0 && !activeAgent) {
                setActiveAgent(keys[0]);
                setContent(data[keys[0]]?.content || '');
            }
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : '加载失败');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchPrompts(); }, [fetchPrompts]);

    // 切换智能体时更新内容
    const handleAgentSwitch = (agentKey: string) => {
        setActiveAgent(agentKey);
        setContent(agents[agentKey]?.content || '');
        setSaveStatus('idle');
    };

    const handleSave = async () => {
        if (!activeAgent) return;
        setSaving(true);
        setSaveStatus('idle');
        try {
            const res = await fetch(`${API_BASE_URL}/api/research/prompts/${activeAgent}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            // 更新本地状态
            setOriginalContents(prev => ({ ...prev, [activeAgent]: content }));
            setAgents(prev => ({
                ...prev,
                [activeAgent]: { ...prev[activeAgent], content },
            }));
            setSaveStatus('success');
            setTimeout(() => setSaveStatus('idle'), 3000);
        } catch (e: unknown) {
            setSaveStatus('error');
            setTimeout(() => setSaveStatus('idle'), 3000);
        } finally {
            setSaving(false);
        }
    };

    const handleReset = () => {
        if (confirm('确定要恢复到上次保存的版本吗？')) {
            setContent(originalContents[activeAgent] || '');
        }
    };

    const hasChanges = content !== (originalContents[activeAgent] || '');

    if (loading) {
        return (
            <div className="flex items-center justify-center py-16">
                <Loader2 className="w-5 h-5 animate-spin text-zinc-400 mr-2" />
                <span className="text-sm text-zinc-500">加载投研 Prompt...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-16 space-y-3">
                <AlertCircle className="w-8 h-8 mx-auto text-red-400" />
                <p className="text-sm text-red-500">{error}</p>
                <button onClick={fetchPrompts} className="text-sm text-primary underline">重试</button>
            </div>
        );
    }

    const agentKeys = Object.keys(agents);

    return (
        <div className="space-y-4">
            {/* Sub-tabs for research agents */}
            <div className="flex flex-wrap gap-1.5">
                {agentKeys.map((key) => {
                    const agent = agents[key];
                    const isModified = (originalContents[key] || '') !== (agents[key]?.content || '');
                    return (
                        <button
                            key={key}
                            onClick={() => handleAgentSwitch(key)}
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${activeAgent === key
                                    ? 'bg-teal-600 text-white shadow-sm'
                                    : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                                }`}
                        >
                            {agent.label}
                        </button>
                    );
                })}
            </div>

            {/* Info Banner */}
            <div className="bg-teal-50 border border-teal-200 rounded-xl p-3">
                <p className="text-sm text-teal-800">
                    {agents[activeAgent]?.label || ''} — 编辑 Jinja2 模板。
                    支持变量语法（<code className="bg-teal-100 px-1.5 py-0.5 rounded text-xs">{'{{ variable }}'}</code>）。
                    保存后下次管道运行自动生效。
                </p>
            </div>

            {/* Editor */}
            <div className="border border-zinc-200 rounded-xl overflow-hidden">
                <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="w-full h-[400px] p-4 text-sm font-mono leading-relaxed bg-white text-zinc-900 resize-none outline-none focus:ring-2 focus:ring-primary/20"
                    placeholder="输入提示词..."
                    spellCheck={false}
                />
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleReset}
                        disabled={!hasChanges}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-zinc-500 hover:text-zinc-700 hover:bg-zinc-100 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                        <RotateCcw className="w-4 h-4" />
                        撤销修改
                    </button>
                    {saveStatus === 'success' && (
                        <span className="flex items-center gap-1 text-sm text-green-600">
                            <CheckCircle2 className="w-4 h-4" /> 已保存
                        </span>
                    )}
                    {saveStatus === 'error' && (
                        <span className="flex items-center gap-1 text-sm text-red-500">
                            <AlertCircle className="w-4 h-4" /> 保存失败
                        </span>
                    )}
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving || !hasChanges}
                    className="flex items-center gap-2 px-5 py-2 text-sm text-white bg-primary hover:bg-primary/90 rounded-lg shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    保存
                </button>
            </div>

            {/* Stats */}
            <div className="text-xs text-zinc-400 text-right">
                字符数: {content.length} | 行数: {content.split('\n').length}
            </div>
        </div>
    );
}
