/**
 * ProviderTab - 提供商选项卡组件
 * P14: Settings 多 Provider 重构
 */
import React from 'react';

interface Provider {
    id: string;
    name: string;
    icon: string;
    available: boolean;
}

interface ProviderTabProps {
    providers: Provider[];
    selectedId: string;
    onSelect: (id: string) => void;
}

export const ProviderTab: React.FC<ProviderTabProps> = ({
    providers,
    selectedId,
    onSelect,
}) => {
    return (
        <div className="flex gap-1 p-1 bg-gray-800 rounded-lg">
            {providers.map((provider) => (
                <button
                    key={provider.id}
                    onClick={() => provider.available && onSelect(provider.id)}
                    disabled={!provider.available}
                    className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${selectedId === provider.id
                            ? 'bg-blue-600 text-white'
                            : provider.available
                                ? 'text-gray-400 hover:text-white hover:bg-gray-700'
                                : 'text-gray-600 cursor-not-allowed'
                        }`}
                >
                    <span>{provider.icon}</span>
                    <span>{provider.name}</span>
                </button>
            ))}
        </div>
    );
};

export default ProviderTab;
