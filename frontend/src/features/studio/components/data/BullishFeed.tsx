'use client';

import React, { useState, useEffect } from 'react';
import { cn } from "@/lib/utils";

/**
 * BullishFeed — 吹捧模式数据面板
 * 
 * P1: Mock 数据版
 * 显示 CZ/何一/Binance 动态 Feed
 */

const TABS = [
    { id: 'all', label: '全部' },
    { id: 'cz', label: 'CZ' },
    { id: 'heyi', label: '何一' },
    { id: 'official', label: '官方' },
] as const;

const MOCK_TWEETS = [
    {
        id: '1',
        author: '@cz_binance',
        avatar: 'CZ',
        time: '2h',
        content: 'Binance has processed over $100B in trading volume this month. Thank you for your support!',
        category: 'cz',
    },
    {
        id: '2',
        author: '@haborofficial',
        avatar: '何',
        time: '5h',
        content: 'Web3 education is the key to mass adoption. We are building bridges, not walls.',
        category: 'heyi',
    },
    {
        id: '3',
        author: '@binance',
        avatar: 'BN',
        time: '8h',
        content: 'New listing announcement: $KAITO token is now available on Binance Spot. Trade now!',
        category: 'official',
    },
    {
        id: '4',
        author: '@cz_binance',
        avatar: 'CZ',
        time: '12h',
        content: 'Building in bear market, shipping in bull market. The cycle continues. Stay focused, stay building.',
        category: 'cz',
    },
    {
        id: '5',
        author: '@haborofficial',
        avatar: '何',
        time: '1d',
        content: '刚参加完 Consensus 大会回来。行业的能量前所未有，大量传统金融机构正在积极布局。',
        category: 'heyi',
    },
];

export function BullishFeed() {
    const [activeTab, setActiveTab] = useState<string>('all');
    const [isLoading, setIsLoading] = useState<boolean>(true);

    // 模拟数据加载
    useEffect(() => {
        setIsLoading(true);
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1200);
        return () => clearTimeout(timer);
    }, [activeTab]);

    const filteredTweets = activeTab === 'all'
        ? MOCK_TWEETS
        : MOCK_TWEETS.filter(t => t.category === activeTab);

    return (
        <div className="flex flex-col h-full">
            {/* 标题 */}
            <div className="px-4 pt-4 pb-2">
                <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
                    <span className="text-lg">🌸</span>
                    币安动态
                </h3>
            </div>

            {/* Tab 筛选 */}
            <div className="px-4 pb-3 flex gap-1.5">
                {TABS.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={cn(
                            "px-3 py-1 text-xs font-medium rounded-full transition-all",
                            activeTab === tab.id
                                ? "bg-pink-100 text-pink-700 border border-pink-200"
                                : "bg-white text-ink-muted border border-zinc-200 hover:border-zinc-300"
                        )}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* 推文列表或骨架屏 */}
            <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3">
                {isLoading ? (
                    // 骨架屏 Skeleton
                    Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="bg-white rounded-xl border border-zinc-200 p-3 animate-pulse">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="w-7 h-7 bg-zinc-200 rounded-full"></div>
                                <div className="h-3 bg-zinc-200 rounded w-20"></div>
                            </div>
                            <div className="space-y-2">
                                <div className="h-3 bg-zinc-200 rounded w-full"></div>
                                <div className="h-3 bg-zinc-200 rounded w-5/6"></div>
                            </div>
                        </div>
                    ))
                ) : filteredTweets.length === 0 ? (
                    // 空状态 Empty State
                    <div className="flex flex-col items-center justify-center h-48 text-center text-ink-muted">
                        <span className="text-3xl mb-3 grayscale opacity-50">📭</span>
                        <p className="text-xs font-medium">暂无相关动态内容</p>
                        <p className="text-[10px] opacity-70 mt-1">请尝试切换分类或稍后再来看看</p>
                    </div>
                ) : (
                    filteredTweets.map(tweet => (
                        <div
                            key={tweet.id}
                            className="group bg-white rounded-xl border border-zinc-200 p-3 hover:border-pink-300 hover:shadow-sm transition-all cursor-pointer"
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-7 h-7 bg-zinc-200 rounded-full flex items-center justify-center text-[10px] font-bold text-ink-muted">
                                    {tweet.avatar}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <span className="text-xs font-medium text-ink-primary">{tweet.author}</span>
                                    <span className="text-xs text-ink-muted ml-2">{tweet.time}</span>
                                </div>
                            </div>
                            <p className="text-xs text-ink-secondary leading-relaxed line-clamp-3">
                                {tweet.content}
                            </p>
                            <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                <span className="text-[10px] text-pink-600 font-medium">点击选用 →</span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* 数据来源 */}
            <div className="px-4 py-2 border-t border-zinc-100">
                <p className="text-[10px] text-ink-muted text-center">
                    📡 数据来源: Grok → binance_daily
                </p>
            </div>
        </div>
    );
}
