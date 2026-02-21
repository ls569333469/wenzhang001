'use client';

import { useState, useEffect } from 'react';
import { IslandContainer } from "./IslandContainer";
import { ConfigPanel } from "../ConfigPanel";
import { useDetailPanel } from "../DetailPanel";
import { cn } from "@/lib/utils";
import { Settings2, FileText, Palette, Database, Clock, ImageIcon, Download, ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * ConfigIsland v3.1 - 可展开图标栏
 * 
 * 默认: 48px 图标栏
 * 点击配置图标: 展开为 320px 完整配置面板
 */

const BOTTOM_ICONS = [
    { id: 'history', icon: Clock, label: '历史记录', panelTab: 'history' as const },
    { id: 'image', icon: ImageIcon, label: '配图生成', panelTab: 'image' as const },
    { id: 'export', icon: Download, label: '导出', panelTab: 'export' as const },
];

export function ConfigIsland() {
    const [isExpanded, setIsExpanded] = useState(true); // 默认展开配置

    // P27: 通知 StudioLayout 配置面板的展开/收起状态
    useEffect(() => {
        document.documentElement.setAttribute('data-config-expanded', String(isExpanded));
        return () => document.documentElement.removeAttribute('data-config-expanded');
    }, [isExpanded]);

    // Connect to DetailPanel
    let detailPanel: ReturnType<typeof useDetailPanel> | null = null;
    try {
        detailPanel = useDetailPanel();
    } catch {
        // Context not available
    }

    const handlePanelOpen = (tab: 'thinking' | 'history' | 'image' | 'export') => {
        if (detailPanel) {
            detailPanel.openPanel(tab);
        }
    };

    return (
        <IslandContainer position="left">
            <div className={cn(
                "flex flex-col h-full transition-all duration-300",
                isExpanded ? "w-[320px]" : "w-[48px]"
            )}>
                {isExpanded ? (
                    // 展开模式: 完整配置面板
                    <div className="flex-1 overflow-y-auto">
                        <ConfigPanel />
                    </div>
                ) : (
                    // 收起模式: 图标栏
                    <div className="flex flex-col items-center py-4 gap-2 flex-1 bg-zinc-900">
                        {/* 配置图标 - 点击展开 */}
                        <button
                            onClick={() => setIsExpanded(true)}
                            className={cn(
                                "w-9 h-9 rounded-lg flex items-center justify-center",
                                "text-zinc-400 hover:text-white hover:bg-zinc-800",
                                "transition-colors group relative"
                            )}
                            title="展开配置"
                        >
                            <Settings2 className="w-4 h-4" />
                            <span className="absolute left-full ml-2 px-2 py-1 text-xs font-medium text-white bg-zinc-700 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                                展开配置
                            </span>
                        </button>

                        {/* 分隔线 */}
                        <div className="w-6 h-px bg-zinc-700 my-3" />

                        {/* 底部图标 (触发面板) */}
                        {BOTTOM_ICONS.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => handlePanelOpen(item.panelTab)}
                                className={cn(
                                    "w-9 h-9 rounded-lg flex items-center justify-center",
                                    "text-zinc-400 hover:text-white hover:bg-zinc-800",
                                    "transition-colors group relative",
                                    detailPanel?.activeTab === item.panelTab && detailPanel?.isOpen && "bg-zinc-800 text-green-400"
                                )}
                                title={item.label}
                            >
                                <item.icon className="w-4 h-4" />
                                <span className="absolute left-full ml-2 px-2 py-1 text-xs font-medium text-white bg-zinc-700 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">
                                    {item.label}
                                </span>
                            </button>
                        ))}
                    </div>
                )}

                {/* 收起/展开按钮 */}
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className={cn(
                        "flex items-center justify-center py-2 border-t",
                        isExpanded
                            ? "bg-white border-zinc-200 text-zinc-500 hover:bg-zinc-50"
                            : "bg-zinc-800 border-zinc-700 text-zinc-400 hover:bg-zinc-700"
                    )}
                >
                    {isExpanded ? (
                        <>
                            <ChevronLeft className="w-4 h-4" />
                            <span className="text-xs ml-1">收起</span>
                        </>
                    ) : (
                        <ChevronRight className="w-4 h-4" />
                    )}
                </button>
            </div>
        </IslandContainer>
    );
}
