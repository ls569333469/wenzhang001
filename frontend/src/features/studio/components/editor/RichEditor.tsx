'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { Markdown } from 'tiptap-markdown';
import { useEffect } from 'react';
import { EditorToolbar } from './EditorToolbar';
import { EditorBubbleMenu } from './EditorBubbleMenu';
import BubbleMenuExtension from '@tiptap/extension-bubble-menu';
import { cn } from '@/lib/utils';

interface RichEditorProps {
    content: string;
    isStreaming?: boolean;
    onUpdate?: (content: string) => void;
    className?: string;
    placeholder?: string;
}

export function RichEditor({
    content,
    isStreaming,
    onUpdate,
    className,
    placeholder = "开始创作..."
}: RichEditorProps) {

    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [1, 2, 3]
                }
            }),
            Placeholder.configure({
                placeholder,
                emptyEditorClass: 'is-editor-empty before:content-[attr(data-placeholder)] before:text-zinc-400 before:float-left before:pointer-events-none after:hidden'
            }),
            Markdown,
            BubbleMenuExtension,
        ],
        content: content,
        immediatelyRender: false,
        editorProps: {
            attributes: {
                class: 'prose prose-zinc max-w-none focus:outline-none min-h-[600px] px-16 py-12',
            },
        },
        onUpdate: ({ editor }) => {
            if (onUpdate) {
                try {
                    const markdown = editor.storage.markdown.getMarkdown();
                    onUpdate(markdown);
                } catch (e) {
                    console.error("Markdown conversion error", e);
                }
            }
        },
    });

    useEffect(() => {
        if (!editor || !content) return;

        // Get current content to compare
        // Note: getMarkdown might differ slightly from input content (formatting normalization)
        // So stick to simple length check or just trust the store if isStreaming

        const currentMarkdown = editor.storage.markdown.getMarkdown();

        // Only update if content is definitely different and valid
        if (content !== currentMarkdown) {
            // Use emitUpdate: false to prevent triggering onUpdate loop
            editor.commands.setContent(content, false);

            // If streaming, move cursor to end?
            if (isStreaming) {
                editor.commands.focus('end');
            }
        }
    }, [content, editor, isStreaming]);

    return (
        <div className={cn("relative w-full border border-zinc-200 rounded-xl bg-white shadow-island transition-all", className)}>
            <EditorToolbar editor={editor} />
            {editor && <EditorBubbleMenu editor={editor} />}
            <EditorContent editor={editor} />
        </div>
    )
}
