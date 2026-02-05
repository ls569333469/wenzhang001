'use client';

import { useAgentStore, DraftVersion } from "@/features/agent/stores/useAgentStore";
import { format } from "date-fns";
import { zhCN } from "date-fns/locale";
import { History, Bot, User, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useState, useMemo } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DiffViewer } from "./DiffViewer";
import { marked } from "marked";

export function VersionTab() {
    const { draftHistory, currentVersionId, restoreVersion, content } = useAgentStore();
    const [selectedVersion, setSelectedVersion] = useState<DraftVersion | null>(null);
    const [isDiffOpen, setIsDiffOpen] = useState(false);

    // If history is empty
    if (draftHistory.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-zinc-400 space-y-3">
                <History className="w-10 h-10 text-zinc-200" />
                <div className="text-sm">暂无版本历史</div>
                <div className="text-xs text-zinc-300 px-8 text-center">
                    开始创作或手动保存后<br />这里将显示修改记录
                </div>
            </div>
        );
    }

    const handleRestore = (id: string) => {
        try {
            restoreVersion(id);
            // Close dialog if open
            setIsDiffOpen(false);
        } catch (e) {
            console.error(e);
            toast.error("版本恢复失败");
        }
    };

    // Compare selected version with current content
    const handleCompare = (version: DraftVersion) => {
        // P19: 智能默认选中
        // 如果用户点击的是当前版本，且存在上一个版本，自动选中上一个版本进行对比
        // 避免用户看到 "无高亮" 的情况
        if (version.id === currentVersionId && draftHistory.length > 1) {
            const currentIndex = draftHistory.findIndex(v => v.id === version.id);
            if (currentIndex !== -1 && currentIndex + 1 < draftHistory.length) {
                const prevVersion = draftHistory[currentIndex + 1];
                setSelectedVersion(prevVersion);
                setIsDiffOpen(true);
                toast.info("已自动选择上一版本进行对比", {
                    description: `v${version.version} (当前) vs v${prevVersion.version}`
                });
                return;
            }
        }

        setSelectedVersion(version);
        setIsDiffOpen(true);
    };

    return (
        <div className="space-y-4">
            <div className="text-sm font-semibold text-ink-primary mb-2 flex items-center justify-between">
                <span>版本历史</span>
                <span className="text-xs text-zinc-400 font-normal">{draftHistory.length} 个版本</span>
            </div>

            <Dialog open={isDiffOpen} onOpenChange={setIsDiffOpen}>
                <DialogContent className="max-w-7xl max-h-[85vh] overflow-hidden bg-white">
                    <DialogHeader className="pb-4 border-b border-zinc-100">
                        <DialogTitle className="text-lg font-semibold text-zinc-900">
                            版本对比 (v{selectedVersion?.version} vs 当前)
                        </DialogTitle>
                    </DialogHeader>

                    {selectedVersion && (
                        <div className="grid grid-cols-2 gap-0 mt-0 h-[70vh]">
                            {/* 左侧: 历史版本 */}
                            <div className="flex flex-col border-r border-zinc-100">
                                <div className="px-5 py-3 bg-zinc-50 border-b border-zinc-100 flex items-center justify-between">
                                    <span className="text-sm font-medium text-zinc-700">
                                        历史版本 (v{selectedVersion.version})
                                    </span>
                                    <button
                                        onClick={() => handleRestore(selectedVersion.id)}
                                        className="px-3 py-1 text-sm font-medium text-white bg-zinc-900 rounded-md hover:bg-zinc-800 transition-colors"
                                    >
                                        恢复此版本
                                    </button>
                                </div>
                                <div
                                    className="flex-1 p-5 overflow-y-auto text-base leading-relaxed text-zinc-800 whitespace-pre-wrap"
                                    style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                                >
                                    {selectedVersion.content}
                                </div>
                            </div>

                            {/* 右侧: 差异对比 */}
                            <div className="flex flex-col">
                                <div className="px-5 py-3 bg-zinc-50 border-b border-zinc-100">
                                    <span className="text-sm font-medium text-zinc-700">
                                        差异对比 (当前版本)
                                    </span>
                                </div>
                                <div className="flex-1 p-5 overflow-y-auto text-base leading-relaxed text-zinc-800 whitespace-pre-wrap"
                                    style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
                                    {selectedVersion.content === content ? (
                                        <div className="flex flex-col items-center justify-center h-full text-zinc-400 space-y-2">
                                            <div className="text-sm">⚠️ 内容完全一致</div>
                                            <div className="text-xs text-center px-4">
                                                您选择了当前版本或未修改的历史版本<br />
                                                请尝试选择更早的历史版本进行对比
                                            </div>
                                        </div>
                                    ) : (
                                        <DiffViewer oldText={selectedVersion.content} newText={content} />
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>

            <div className="space-y-3 relative pl-3 before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-px before:bg-zinc-100">
                {draftHistory.map((version) => {
                    const isCurrent = version.id === currentVersionId;
                    const isAi = version.source === 'ai';

                    return (
                        <div
                            key={version.id}
                            className={cn(
                                "relative group flex gap-3 p-3 rounded-lg border transition-all cursor-pointer hover:shadow-md",
                                isCurrent
                                    ? "bg-white border-primary/20 shadow-sm ring-1 ring-primary/5"
                                    : "bg-white border-zinc-100 hover:border-zinc-200"
                            )}
                            onClick={() => handleCompare(version)}
                        >
                            {/* Timeline Dot */}
                            <div className={cn(
                                "absolute -left-[19px] top-6 w-3 h-3 rounded-full border-2 bg-white z-10",
                                isCurrent ? "border-primary" : "border-zinc-200"
                            )} />

                            {/* Icon */}
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                                isAi ? "bg-indigo-50 text-indigo-500" : "bg-zinc-100 text-zinc-500"
                            )}>
                                {isAi ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1">
                                    <span className={cn(
                                        "text-xs font-medium",
                                        isCurrent ? "text-primary" : "text-zinc-700"
                                    )}>
                                        v{version.version}
                                        {isCurrent && <span className="ml-2 px-1.5 py-0.5 bg-primary/10 text-primary text-[10px] rounded">当前</span>}
                                    </span>
                                    <span className="text-[10px] text-zinc-400">
                                        {format(new Date(version.timestamp), 'HH:mm', { locale: zhCN })}
                                    </span>
                                </div>

                                <div className="text-xs text-zinc-500 line-clamp-2 h-8">
                                    {version.summary || (isAi ? "AI 生成内容" : "手动编辑内容")}
                                </div>

                                {version.critique && (
                                    <div className="mt-2 flex items-center gap-2">
                                        <div className={cn(
                                            "text-[10px] px-1.5 py-0.5 rounded font-medium",
                                            version.critique.score >= 80 ? "bg-green-50 text-green-600" :
                                                version.critique.score >= 60 ? "bg-yellow-50 text-yellow-600" :
                                                    "bg-red-50 text-red-600"
                                        )}>
                                            得分 {version.critique.score}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Actions (Hover) */}
                            <div className="absolute right-2 bottom-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleRestore(version.id);
                                    }}
                                    className="p-1.5 hover:bg-zinc-100 rounded text-zinc-500 hover:text-primary transition-colors"
                                    title="直接恢复"
                                >
                                    <RotateCcw className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
