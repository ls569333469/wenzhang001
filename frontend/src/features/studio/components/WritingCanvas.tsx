'use client';

import { HeroInput } from "./HeroInput";
import { StrategySelector } from "./StrategySelector";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';

export function WritingCanvas() {
    const { content, isWaitingForSelection } = useAgentStore();

    return (
        <div className="w-full max-w-3xl mx-auto space-y-8 animate-in fade-in zoom-in duration-500">
            {/* Paper Sheet (拟物化容器) */}
            <div className={cn(
                "min-h-[800px] rounded-xl shadow-sm transition-all duration-500",
                content ? "bg-white border border-zinc-100 p-16 prose prose-zinc max-w-none shadow-island" : "bg-transparent border-none p-0"
            )}>
                {content ? (
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
