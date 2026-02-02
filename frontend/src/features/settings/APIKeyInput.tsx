/**
 * APIKeyInput - API Key 输入组件
 * P14: Settings 多 Provider 重构
 */
import React, { useState } from 'react';

interface APIKeyInputProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    helpText?: string;
}

export const APIKeyInput: React.FC<APIKeyInputProps> = ({
    label,
    value,
    onChange,
    placeholder = 'sk-...',
    helpText,
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    // 显示遮蔽的密钥
    const displayValue = isVisible ? value : value ? '•'.repeat(Math.min(value.length, 32)) : '';

    return (
        <div className="space-y-1">
            <label className="text-sm font-medium text-gray-300">{label}</label>
            <div className="relative">
                <input
                    type={isVisible ? 'text' : 'password'}
                    value={isFocused ? value : displayValue}
                    onChange={(e) => onChange(e.target.value)}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    placeholder={placeholder}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 pr-20"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
                    <button
                        type="button"
                        onClick={() => setIsVisible(!isVisible)}
                        className="px-2 py-1 text-xs text-gray-400 hover:text-white"
                    >
                        {isVisible ? '隐藏' : '显示'}
                    </button>
                    {value && (
                        <button
                            type="button"
                            onClick={() => onChange('')}
                            className="px-2 py-1 text-xs text-red-400 hover:text-red-300"
                        >
                            清除
                        </button>
                    )}
                </div>
            </div>
            {helpText && (
                <p className="text-xs text-gray-500">{helpText}</p>
            )}
        </div>
    );
};

export default APIKeyInput;
