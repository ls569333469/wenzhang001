import React from 'react';
import { X, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface PromptPreviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    content: string;
    title?: string;
}

export function PromptPreviewModal({
    isOpen,
    onClose,
    content,
    title = "完整提示词预览"
}: PromptPreviewModalProps) {
    const [copied, setCopied] = React.useState(false);

    if (!isOpen) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col animate-in fade-in zoom-in duration-200">
                <div className="flex items-center justify-between p-4 border-b border-zinc-100">
                    <h3 className="font-semibold text-zinc-900">{title}</h3>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleCopy}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-600 bg-zinc-100 hover:bg-zinc-200 rounded-md transition-colors"
                        >
                            {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                            {copied ? '已复制' : '复制全文'}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-1.5 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-full transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6 bg-zinc-50">
                    <div className="bg-white border border-zinc-200 rounded-lg p-6 shadow-sm">
                        <pre className="whitespace-pre-wrap font-mono text-sm text-zinc-700 leading-relaxed">
                            {content}
                        </pre>
                    </div>

                    <div className="mt-4 p-4 bg-blue-50/50 border border-blue-100 rounded-lg text-xs text-blue-600">
                        <p className="font-medium mb-1">💡 说明</p>
                        <p>这是最终发送给 LLM 的完整提示词。包含了您编辑的各个区块以及系统自动注入的输出格式控制。</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
