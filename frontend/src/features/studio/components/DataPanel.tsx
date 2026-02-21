'use client';

import React from 'react';
import { type CreationMode } from '../schema';
import { BullishFeed } from './data/BullishFeed';
import { KaitoBoard } from './data/KaitoBoard';
import { ResearchPanel } from './data/ResearchPanel';

/**
 * DataPanel — P27 数据展示面板
 * 
 * 根据模式 switch 路由到不同数据视图：
 * - bullish_take → BullishFeed (动态 Feed)
 * - kaito_yap → KaitoBoard (项目看板)
 * - project_research → ResearchPanel (搜索+数据源)
 * - 其他模式 → 不渲染 (return null)
 */

export function DataPanel({ mode }: { mode: CreationMode }) {
    const renderContent = () => {
        switch (mode) {
            case 'bullish_take':
                return <BullishFeed />;
            case 'kaito_yap':
                return <KaitoBoard />;
            case 'project_research':
                return <ResearchPanel />;
            default:
                return null;
        }
    };

    const content = renderContent();
    if (!content) return null;

    return (
        <div className="flex-1 w-full h-full overflow-y-auto bg-[#fafafa] scrollbar-hide">
            {content}
        </div>
    );
}

