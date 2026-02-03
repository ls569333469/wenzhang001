import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Info } from 'lucide-react';

interface PromptSectionProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    description?: string;
    optional?: boolean;
    defaultExpanded?: boolean;
}

export function PromptSection({
    label,
    value,
    onChange,
    placeholder,
    description,
    optional,
    defaultExpanded = true
}: PromptSectionProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="border border-zinc-200 rounded-xl overflow-hidden bg-white">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-3 bg-zinc-50 hover:bg-zinc-100 transition-colors text-left"
            >
                <span className="font-medium text-sm text-zinc-700 flex items-center gap-2">
                    {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    {label}
                </span>
                {optional && !value && (
                    <span className="text-xs text-zinc-400 bg-zinc-200/50 px-2 py-0.5 rounded-full">
                        未配置
                    </span>
                )}
            </button>

            {isExpanded && (
                <div className="p-4 space-y-2">
                    {description && (
                        <div className="flex items-start gap-2 text-xs text-zinc-500 mb-2">
                            <Info className="w-3 h-3 mt-0.5 shrink-0" />
                            <p>{description}</p>
                        </div>
                    )}

                    <textarea
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder || (optional ? "留空则不添加此约束..." : "请输入内容...")}
                        className="w-full min-h-[100px] p-3 text-sm border border-zinc-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono resize-y text-zinc-700 placeholder:text-zinc-300"
                    />
                </div>
            )}
        </div>
    );
}
