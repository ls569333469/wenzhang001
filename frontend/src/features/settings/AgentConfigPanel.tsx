/**
 * AgentConfigPanel - Agent 配置面板
 * P14: Settings 多 Provider 重构
 */
import React from 'react';
import { ProviderTab } from './ProviderTab';
import { ModelSelector } from './ModelSelector';

interface AgentConfig {
    provider: string;
    model_id: string;
}

interface AgentConfigPanelProps {
    agentName: string;
    agentLabel: string;
    agentIcon: string;
    config: AgentConfig;
    providers: { id: string; name: string; icon: string; available: boolean }[];
    models: Record<string, { id: string; name: string; description?: string }[]>;
    onChange: (config: AgentConfig) => void;
    useGlobal: boolean;
    onToggleGlobal: (use: boolean) => void;
}

export const AgentConfigPanel: React.FC<AgentConfigPanelProps> = ({
    agentName,
    agentLabel,
    agentIcon,
    config,
    providers,
    models,
    onChange,
    useGlobal,
    onToggleGlobal,
}) => {
    const currentModels = models[config.provider] || [];

    return (
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 space-y-4">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-lg">{agentIcon}</span>
                    <span className="font-medium text-gray-200">{agentLabel}</span>
                </div>
                <label className="flex items-center gap-2 text-sm text-gray-400">
                    <input
                        type="checkbox"
                        checked={useGlobal}
                        onChange={(e) => onToggleGlobal(e.target.checked)}
                        className="rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500"
                    />
                    使用全局配置
                </label>
            </div>

            {/* Config Fields */}
            {!useGlobal && (
                <div className="space-y-4 pt-2">
                    <ProviderTab
                        providers={providers}
                        selectedId={config.provider}
                        onSelect={(id) => onChange({ ...config, provider: id })}
                    />

                    <ModelSelector
                        models={currentModels}
                        selectedId={config.model_id}
                        onSelect={(id) => onChange({ ...config, model_id: id })}
                    />
                </div>
            )}
        </div>
    );
};

export default AgentConfigPanel;
