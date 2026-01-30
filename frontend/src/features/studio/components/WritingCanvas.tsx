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
import { marked } from 'marked';

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

    const handleExportMD = () => {
        const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        link.download = `article_${timestamp}.md`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        toast.success('已导出 Markdown 文件');
    };

    const handleExportHTML = () => {
        // Basic HTML wrapper with GitHub-like style
        const htmlContent = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Generated Article</title>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #24292e; max-width: 800px; margin: 0 auto; padding: 2rem; }
    h1, h2, h3 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
    h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
    p { margin-top: 0; margin-bottom: 16px; }
    code { font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; }
    pre { background-color: #f6f8fa; padding: 16px; overflow: auto; border-radius: 3px; }
    pre code { background-color: transparent; padding: 0; }
    blockquote { border-left: 0.25em solid #dfe2e5; color: #6a737d; padding: 0 1em; margin: 0; }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
</head>
<body>
<div id="content">
${marked.parse(content)}
</div>
</body>
</html>`;

        const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        link.download = `article_${timestamp}.html`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        toast.success('已导出 HTML 文件');
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
                            {/* Export Group */}
                            <div className="flex items-center bg-zinc-50 rounded-lg border border-zinc-200 p-1 mr-2">
                                <button
                                    onClick={handleExportMD}
                                    disabled={isGenerating}
                                    className="px-2 py-1 text-xs font-medium text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200 rounded transition-colors"
                                    title="导出 Markdown"
                                >
                                    MD
                                </button>
                                <div className="w-px h-3 bg-zinc-300 mx-1"></div>
                                <button
                                    onClick={handleExportHTML}
                                    disabled={isGenerating}
                                    className="px-2 py-1 text-xs font-medium text-zinc-600 hover:text-zinc-900 hover:bg-zinc-200 rounded transition-colors"
                                    title="导出 HTML"
                                >
                                    HTML
                                </button>
                            </div>

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

