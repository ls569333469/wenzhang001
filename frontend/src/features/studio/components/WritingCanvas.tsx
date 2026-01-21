'use client';

import { HeroInput } from "./HeroInput";
import { StrategySelector } from "./StrategySelector";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';
import { RefreshCw, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { UI_TEXT } from '@/config/constants';

export function WritingCanvas() {
    const { content, isWaitingForSelection, regenerate, status } = useAgentStore();
    const [copied, setCopied] = useState(false);
    const isGenerating = status === 'writing' || status === 'thinking';

    const handleCopy = async () => {
        await navigator.clipboard.writeText(content);
        setCopied(true);
        toast.success('内容已复制到剪贴板');
        setTimeout(() => setCopied(false), 2000);
    };

    const handleRegenerate = () => {
        regenerate();
    };

    return (
        <div className="w-full max-w-3xl mx-auto space-y-8">
            {/* Paper Sheet (拟物化容器) */}
            <div className={cn(
                "min-h-[800px] rounded-xl shadow-sm transition-all duration-500 relative",
                content ? "bg-white border border-zinc-100 p-16 prose prose-zinc max-w-none shadow-island" : "bg-transparent border-none p-0"
            )}>
                {content ? (
                    <>
                        {/* Floating Action Bar */}
                        <div className="absolute top-4 right-4 flex items-center gap-2 z-10">
                            <button
                                onClick={handleCopy}
                                disabled={isGenerating}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-ink-muted bg-zinc-50 hover:bg-zinc-100 rounded-lg transition-colors disabled:opacity-50"
                            >
                                {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                {copied ? '已复制' : UI_TEXT.actions.copyContent}
                            </button>
                            <button
                                onClick={handleRegenerate}
                                disabled={isGenerating}
                                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-zinc-900 hover:bg-zinc-800 rounded-lg transition-colors disabled:opacity-50"
                            >
                                <RefreshCw className={cn("w-3 h-3", isGenerating && "animate-spin")} />
                                {UI_TEXT.actions.regenerate}
                            </button>
                        </div>

                        <div className="animate-in fade-in duration-500">
                            <ReactMarkdown
                                rehypePlugins={[rehypeHighlight]}
                                components={{
                                    h1: ({ node, ...props }) => <h1 className="font-serif text-3xl font-bold mt-8 mb-4" {...props} />,
                                    h2: ({ node, ...props }) => <h2 className="font-serif text-2xl font-bold mt-6 mb-3" {...props} />,
                                    h3: ({ node, ...props }) => <h3 className="font-serif text-xl font-bold mt-4 mb-2" {...props} />,
                                    code: ({ node, className, children, ...props }: any) => {
                                        const match = /language-(\w+)/.exec(className || '')
                                        return match ? (
                                            <code className={className} {...props}>
                                                {children}
                                            </code>
                                        ) : (
                                            <code className="bg-zinc-100 px-1.5 py-0.5 rounded text-sm font-mono text-zinc-900" {...props}>
                                                {children}
                                            </code>
                                        )
                                    },
                                }}
                            >
                                {content}
                            </ReactMarkdown>
                        </div>
                    </>
                ) : isWaitingForSelection ? (
                    <div className="flex flex-col items-center justify-center min-h-[60vh]">
                        <StrategySelector />
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center min-h-[60vh]">
                        <HeroInput />
                    </div>
                )}
            </div>
        </div>
    );
}

