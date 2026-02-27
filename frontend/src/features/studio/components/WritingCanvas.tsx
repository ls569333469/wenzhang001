'use client';

import { HeroInput } from "./HeroInput";
import { StrategySelector } from "./StrategySelector";
import { useAgentStore } from "@/features/agent/stores/useAgentStore";
import { cn } from "@/lib/utils";
import { RefreshCw, Copy, Check, FilePlus, Save } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import { UI_TEXT } from '@/config/constants';
import { marked } from 'marked';
import { RichEditor } from "./editor/RichEditor";
import { API_BASE_URL } from '@/config/api';
import { ResearchView } from "@/features/research/ResearchView";

export function WritingCanvas() {
    const { content, isWaitingForSelection, regenerate, status, updateContent, saveVersion, resetSession,
        lastRequestPayload, selectedTitle, critiqueResult, materialPrefill, saveToServer } = useAgentStore();
    const [copied, setCopied] = useState(false);
    const [showResetConfirm, setShowResetConfirm] = useState(false);
    const [savedToServer, setSavedToServer] = useState(false);
    const lastSavedContent = useRef<string>('');
    const isGenerating = status === 'writing' || status === 'thinking';

    // P31: 投研模式检测
    const searchParams = useSearchParams();
    const currentMode = searchParams.get('mode') || 'mid_article';

    // Reset saved state when content changes after save
    useEffect(() => {
        if (savedToServer && content !== lastSavedContent.current) {
            setSavedToServer(false);
        }
    }, [content, savedToServer]);

    // Auto-save (Every 60s)
    useEffect(() => {
        const timer = setInterval(() => {
            if (content && !isGenerating && !isWaitingForSelection) {
                saveVersion('user', 'Auto-save');
            }
        }, 60000);

        return () => clearInterval(timer);
    }, [content, isGenerating, isWaitingForSelection, saveVersion]);

    // P31: 投研模式 — 所有 hooks 之后才能 early return
    if (currentMode === 'project_research') {
        return <ResearchView />;
    }

    // P27: Save to server (local file)
    const handleSaveToServer = async () => {
        if (!content || isGenerating) return;
        const success = await saveToServer();
        if (success) {
            setSavedToServer(true);
            lastSavedContent.current = content;
            toast.success('已保存到本地');
        } else {
            toast.error('保存失败');
        }
    };

    // P24-C: New creation handler
    const handleNewCreation = () => {
        setShowResetConfirm(true);
    };

    const confirmNewCreation = () => {
        resetSession();
        setShowResetConfirm(false);
        toast.success('已重置，可以开始新创作');
    };

    // Manual Save (Ctrl+S)
    const handleManualSave = () => {
        if (!content || isGenerating) return;
        saveVersion('user', 'Manual Save');
    };

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
        <div className="flex flex-col h-full w-full relative">

            {/* Fixed Canvas Area */}
            <div className="flex-1 flex flex-col overflow-hidden px-12 pt-24 pb-12 bg-white">
                <div className="w-full h-full flex flex-col space-y-8">
                    {/* Paper Sheet (拟物化容器) */}
                    <div className={cn(
                        "flex-1 w-full flex flex-col rounded-xl transition-all duration-500 relative min-h-0",
                        content ? "bg-transparent" : "bg-transparent border-none p-0"
                    )}>
                        {content ? (
                            <>
                                {/* P24-C: Reset Confirmation Dialog */}
                                {showResetConfirm && (
                                    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" onClick={() => setShowResetConfirm(false)}>
                                        <div className="bg-white rounded-2xl p-6 shadow-xl max-w-sm mx-4 space-y-4" onClick={(e) => e.stopPropagation()}>
                                            <h3 className="text-lg font-semibold text-zinc-900">确认新建创作？</h3>
                                            <p className="text-sm text-zinc-600">
                                                当前内容将被清空，包括草稿历史和评审记录。此操作无法撤销。
                                            </p>
                                            <div className="flex gap-3 justify-end">
                                                <button
                                                    onClick={() => setShowResetConfirm(false)}
                                                    className="px-4 py-2 text-sm font-medium text-zinc-600 bg-zinc-100 hover:bg-zinc-200 rounded-lg transition-colors"
                                                >
                                                    取消
                                                </button>
                                                <button
                                                    onClick={confirmNewCreation}
                                                    className="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
                                                >
                                                    确认清空
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="animate-in fade-in duration-500 flex-1 flex flex-col min-h-0 relative h-full">
                                    <RichEditor
                                        content={content}
                                        isStreaming={status === 'writing'}
                                        onUpdate={updateContent}
                                        onSave={handleManualSave}
                                        className="flex-1 min-h-0 h-full"
                                        toolbarActions={
                                            <>
                                                {/* Export Group */}
                                                <div className="flex items-center bg-zinc-50 rounded-lg border border-zinc-200 p-1 shadow-sm">
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
                                                    className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-ink-muted bg-white hover:bg-zinc-100 rounded-md transition-colors disabled:opacity-50 border border-zinc-200 shadow-sm leading-none"
                                                >
                                                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                                    {copied ? '已复制' : UI_TEXT.actions.copyContent}
                                                </button>

                                                <button
                                                    onClick={handleSaveToServer}
                                                    disabled={isGenerating || savedToServer}
                                                    className={cn(
                                                        "flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium rounded-md transition-colors shadow-sm border leading-none",
                                                        savedToServer
                                                            ? "text-emerald-600 bg-emerald-50 border-emerald-200 cursor-default"
                                                            : "text-blue-600 bg-blue-50 hover:bg-blue-100 border-blue-200 disabled:opacity-50"
                                                    )}
                                                    title="保存到本地文件"
                                                >
                                                    {savedToServer ? <Check className="w-3 h-3" /> : <Save className="w-3 h-3" />}
                                                    {savedToServer ? '已保存' : '保存'}
                                                </button>

                                                <button
                                                    onClick={handleRegenerate}
                                                    disabled={isGenerating}
                                                    className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-white bg-zinc-800 hover:bg-zinc-700 rounded-md transition-colors disabled:opacity-50 shadow-sm leading-none"
                                                >
                                                    <RefreshCw className={cn("w-3 h-3", isGenerating && "animate-spin")} />
                                                    {UI_TEXT.actions.regenerate}
                                                </button>

                                                <button
                                                    onClick={handleNewCreation}
                                                    disabled={isGenerating}
                                                    className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors disabled:opacity-50 border border-red-200 shadow-sm leading-none"
                                                    title="清空当前内容，开始新创作"
                                                >
                                                    <FilePlus className="w-3 h-3" />
                                                    新建
                                                </button>
                                            </>
                                        }
                                    />
                                </div>
                            </>
                        ) : isWaitingForSelection ? (
                            <div className="flex flex-col items-center justify-center min-h-[60vh] bg-white border border-zinc-100 p-16 rounded-xl shadow-island">
                                <StrategySelector />
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center flex-1 w-full max-w-[820px] mx-auto pt-20 pb-32">
                                <HeroInput />
                            </div>
                        )}
                    </div>
                </div>
            </div>

        </div >
    );
}
