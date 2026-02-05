'use client';

import { diffChars } from 'diff';
import { useMemo } from 'react';
import { cn } from "@/lib/utils";

interface DiffViewerProps {
    oldText: string;
    newText: string;
    className?: string;
}

/**
 * DiffViewer - Enhanced visualization of text differences
 * 
 * P19: Upgraded to word-level diff with prominent highlighting
 * - Added text: 明亮绿色背景 + 加粗 + 蓝色边框
 * - Removed text: 明亮红色背景 + 删除线
 * - Unchanged text: 继承父容器颜色
 */
export function DiffViewer({ oldText, newText, className }: DiffViewerProps) {
    const diff = useMemo(() => {
        // P19: 对中文更友好的字符级对比 (Character-level diff)
        // diffWords 在中文语境下容易把整句标红，造成 visual noise
        return diffChars(oldText || '', newText || '');
    }, [oldText, newText]);

    return (
        <div className={cn("whitespace-pre-wrap", className)}>
            {diff.map((part, index) => {
                if (part.added) {
                    // 新增内容: 明亮绿色背景 + 加粗
                    return (
                        <span
                            key={index}
                            className="bg-green-100 text-green-800 rounded-sm"
                        >
                            {part.value}
                        </span>
                    );
                }

                if (part.removed) {
                    // 删除内容: 明亮红色背景 + 删除线
                    return (
                        <span
                            key={index}
                            className="bg-red-50 text-red-500 line-through decoration-red-300 rounded-sm"
                        >
                            {part.value}
                        </span>
                    );
                }

                // 未改变内容: 保持原样
                return (
                    <span key={index}>
                        {part.value}
                    </span>
                );
            })}
        </div>
    );
}
