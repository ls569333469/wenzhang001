'use client';

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@radix-ui/react-tabs";
import { Activity, History, ScrollText, Download } from "lucide-react";
import { ProgressTab } from "./ProgressTab";
import { VersionTab } from "./VersionTab";
import { LogsTab } from "./LogsTab";
import { ExportTab } from "./ExportTab";
import { IslandContainer } from "../layout/IslandContainer";

/**
 * UnifiedSidebar - P19 Phase 2 (Reverted)
 * 
 * Consolidates floating panels into a unified tabbed interface.
 * Reverted to Icon+Text style, removed ThinkingTab.
 */
export function UnifiedSidebar() {
    return (
        <IslandContainer position="right">
            <div className="h-full flex flex-col bg-white/80 backdrop-blur-sm">
                <Tabs defaultValue="progress" className="flex-1 flex flex-col h-full">
                    {/* Tab Header */}
                    <div className="px-2 pt-2 border-b border-zinc-100">
                        <TabsList className="flex w-full">
                            <TabsTrigger
                                value="progress"
                                className="flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-zinc-500 data-[state=active]:text-zinc-900 data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 transition-colors"
                            >
                                <Activity className="w-3.5 h-3.5" />
                                进度
                            </TabsTrigger>
                            <TabsTrigger
                                value="version"
                                className="flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-zinc-500 data-[state=active]:text-zinc-900 data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 transition-colors"
                            >
                                <History className="w-3.5 h-3.5" />
                                版本
                            </TabsTrigger>
                            <TabsTrigger
                                value="logs"
                                className="flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-zinc-500 data-[state=active]:text-zinc-900 data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 transition-colors"
                            >
                                <ScrollText className="w-3.5 h-3.5" />
                                日志
                            </TabsTrigger>
                            <TabsTrigger
                                value="export"
                                className="flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-zinc-500 data-[state=active]:text-zinc-900 data-[state=active]:border-b-2 data-[state=active]:border-zinc-900 transition-colors"
                            >
                                <Download className="w-3.5 h-3.5" />
                                导出
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    {/* Tab Content Areas */}
                    <div className="flex-1 overflow-hidden relative">
                        <div className="absolute inset-0 overflow-y-auto custom-scrollbar">
                            <TabsContent value="progress" className="h-full p-4 outline-none">
                                <ProgressTab />
                            </TabsContent>

                            <TabsContent value="version" className="h-full p-4 outline-none">
                                <VersionTab />
                            </TabsContent>

                            <TabsContent value="logs" className="h-full p-4 outline-none">
                                <LogsTab />
                            </TabsContent>

                            <TabsContent value="export" className="h-full p-4 outline-none">
                                <ExportTab />
                            </TabsContent>
                        </div>
                    </div>
                </Tabs>
            </div>
        </IslandContainer>
    );
}
