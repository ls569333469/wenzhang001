'use client';

import { Editor } from '@tiptap/react';
import { BubbleMenu } from '@tiptap/react/menus';
import { Sparkles, Scissors, Minimize2, Maximize2, Eraser, Check } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { useAgentStore } from '@/features/agent/stores/useAgentStore';

interface EditorBubbleMenuProps {
    editor: Editor;
}

export function EditorBubbleMenu({ editor }: EditorBubbleMenuProps) {
    const [isGenerating, setIsGenerating] = useState(false);
    const { updateContent, saveVersion } = useAgentStore();

    const handleRewrite = async (instruction: string) => {
        const { from, to, empty } = editor.state.selection;
        if (empty) return;

        const selectedText = editor.state.doc.textBetween(from, to);
        if (!selectedText.trim()) return;

        setIsGenerating(true);
        const toastId = toast.loading("AI 正在重写...");

        try {
            // Include some context (prev/next 200 chars)
            const contextBefore = editor.state.doc.textBetween(Math.max(0, from - 200), from);
            const contextAfter = editor.state.doc.textBetween(to, Math.min(editor.state.doc.content.size, to + 200));

            const response = await fetch('http://localhost:8000/api/rewrite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    selected_text: selectedText,
                    instruction,
                    context_before: contextBefore,
                    context_after: contextAfter,
                    api_config: { provider: 'volcengine' } // TODO: Get from store
                })
            });

            if (!response.ok || !response.body) {
                throw new Error("Failed to generate");
            }

            // Prepare editor for insertion
            // We replace the selection immediately, then stream append
            // Or we could stream into a temporary mark
            // Simple approach: Delete selection, then insert chunks

            // Delete original selection
            editor.chain().focus().deleteSelection().run();

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                // Insert chunk at current cursor
                editor.commands.insertContent(chunk);
            }

            toast.success("重写完成", { id: toastId });

            // P19: 保存新版本到历史记录
            const newContent = editor.getText();
            updateContent(newContent);
            saveVersion('ai', 'AI 局部重写');

        } catch (error) {
            console.error(error);
            toast.error("重写失败", { id: toastId });
            // Restore text? (Complex if using undo history)
            editor.commands.undo();
        } finally {
            setIsGenerating(false);
        }
    };

    if (isGenerating) {
        return null; // Hide menu during generation (or show a loading state if we want)
    }

    return (
        <BubbleMenu
            editor={editor}
            className="flex items-center gap-1 p-1 bg-white rounded-lg shadow-xl border border-zinc-200 overflow-hidden"
        >
            <MenuButton
                onClick={() => handleRewrite("Polish and improve clarity")}
                icon={<Sparkles className="w-4 h-4 text-indigo-500" />}
                label="润色"
            />
            <div className="w-px h-4 bg-zinc-200 mx-1" />
            <MenuButton
                onClick={() => handleRewrite("Make it shorter and more concise")}
                icon={<Minimize2 className="w-4 h-4 text-zinc-600" />}
                label="精简"
            />
            <MenuButton
                onClick={() => handleRewrite("Expand and add more details")}
                icon={<Maximize2 className="w-4 h-4 text-zinc-600" />}
                label="扩写"
            />
            <div className="w-px h-4 bg-zinc-200 mx-1" />
            <MenuButton
                onClick={() => handleRewrite("Fix grammar and spelling errors")}
                icon={<Check className="w-4 h-4 text-zinc-600" />}
                label="纠错"
            />
        </BubbleMenu>
    );
}

function MenuButton({ onClick, icon, label }: { onClick: () => void, icon: React.ReactNode, label: string }) {
    return (
        <button
            onClick={onClick}
            className="flex items-center gap-1.5 px-2 py-1.5 hover:bg-zinc-100 rounded-md text-xs font-medium text-zinc-700 transition-colors"
        >
            {icon}
            <span>{label}</span>
        </button>
    );
}
