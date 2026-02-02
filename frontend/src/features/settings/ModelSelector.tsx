/**
 * ModelSelector - 模型选择器组件
 * P14: Settings 多 Provider 重构
 */
import React from 'react';

interface Model {
    id: string;
    name: string;
    description?: string;
    tokensPerSec?: number;
}

interface ModelSelectorProps {
    models: Model[];
    selectedId: string;
    onSelect: (id: string) => void;
    loadingModels?: boolean;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
    models,
    selectedId,
    onSelect,
    loadingModels = false,
}) => {
    if (loadingModels) {
        return (
            <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">模型</label>
                <div className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-500 animate-pulse">
                    加载模型列表...
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">模型</label>
            <select
                value={selectedId}
                onChange={(e) => onSelect(e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
                {models.map((model) => (
                    <option key={model.id} value={model.id}>
                        {model.name}
                        {model.tokensPerSec ? ` (${model.tokensPerSec} t/s)` : ''}
                    </option>
                ))}
            </select>
            {models.find(m => m.id === selectedId)?.description && (
                <p className="text-xs text-gray-500">
                    {models.find(m => m.id === selectedId)?.description}
                </p>
            )}
        </div>
    );
};

export default ModelSelector;
