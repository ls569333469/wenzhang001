'use client';

import { type Editor } from '@tiptap/react';
import { Bold, Italic, Heading1, Heading2, List, ListOrdered, Quote, Undo, Redo, Eraser } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming this exists, based on other files

interface EditorToolbarProps {
    editor: Editor | null;
    actions?: React.ReactNode;
}

export function EditorToolbar({ editor, actions }: EditorToolbarProps) {
    if (!editor) {
        return null;
    }

    return (
        <div className="border-b border-zinc-200 bg-zinc-50 p-2 flex items-center gap-1 flex-wrap shrink-0 rounded-t-xl z-10 relative">
            <ToolbarButton
                onClick={() => editor.chain().focus().toggleBold().run()}
                isActive={editor.isActive('bold')}
                icon={<Bold className="w-4 h-4" />}
                title="Bold"
            />
            <ToolbarButton
                onClick={() => editor.chain().focus().toggleItalic().run()}
                isActive={editor.isActive('italic')}
                icon={<Italic className="w-4 h-4" />}
                title="Italic"
            />

            <div className="w-px h-4 bg-zinc-300 mx-1" />

            <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                isActive={editor.isActive('heading', { level: 1 })}
                icon={<Heading1 className="w-4 h-4" />}
                title="Heading 1"
            />
            <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                isActive={editor.isActive('heading', { level: 2 })}
                icon={<Heading2 className="w-4 h-4" />}
                title="Heading 2"
            />

            <div className="w-px h-4 bg-zinc-300 mx-1" />

            <ToolbarButton
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                isActive={editor.isActive('bulletList')}
                icon={<List className="w-4 h-4" />}
                title="Bullet List"
            />
            <ToolbarButton
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                isActive={editor.isActive('orderedList')}
                icon={<ListOrdered className="w-4 h-4" />}
                title="Ordered List"
            />
            <ToolbarButton
                onClick={() => editor.chain().focus().toggleBlockquote().run()}
                isActive={editor.isActive('blockquote')}
                icon={<Quote className="w-4 h-4" />}
                title="Quote"
            />

            <div className="w-px h-4 bg-zinc-300 mx-1" />

            <ToolbarButton
                onClick={() => editor.chain().focus().unsetAllMarks().run()}
                icon={<Eraser className="w-4 h-4" />}
                title="Clear Formatting"
            />

            <div className="flex-1" />

            {actions && (
                <div className="flex items-center gap-1.5 mr-2">
                    {actions}
                    <div className="w-px h-4 bg-zinc-300 mx-1" />
                </div>
            )}

            <ToolbarButton
                onClick={() => editor.chain().focus().undo().run()}
                disabled={!editor.can().undo()}
                icon={<Undo className="w-4 h-4" />}
                title="Undo"
            />
            <ToolbarButton
                onClick={() => editor.chain().focus().redo().run()}
                disabled={!editor.can().redo()}
                icon={<Redo className="w-4 h-4" />}
                title="Redo"
            />
        </div>
    );
}

interface ToolbarButtonProps {
    onClick: () => void;
    isActive?: boolean;
    disabled?: boolean;
    icon: React.ReactNode;
    title: string;
}

function ToolbarButton({ onClick, isActive, disabled, icon, title }: ToolbarButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={cn(
                "p-2 rounded-md transition-colors text-zinc-600 hover:bg-zinc-200 hover:text-zinc-900",
                isActive && "bg-zinc-200 text-zinc-900 font-medium",
                disabled && "opacity-50 cursor-not-allowed hover:bg-transparent"
            )}
            title={title}
            type="button"
        >
            {icon}
        </button>
    );
}
