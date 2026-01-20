import { ReactNode } from "react";
import { StudioNavbar } from "@/features/studio/components/layout/StudioNavbar";

interface StudioLayoutProps {
    children: ReactNode;
    leftPanel?: ReactNode;
    rightPanel?: ReactNode;
}

/**
 * StudioLayout - Z-Stack 布局管理器
 * 
 * 负责组装:
 * 1. Background Layer (Canvas)
 * 2. Main Content Layer (Center)
 * 3. Island Layer (Nav, Left, Right)
 */
export function StudioLayout({ children, leftPanel, rightPanel }: StudioLayoutProps) {
    return (
        <div className="min-h-screen bg-canvas text-ink-primary font-sans relative selection:bg-zinc-900 selection:text-white">

            {/* Layer 0: Background Texture */}
            <div className="fixed inset-0 opacity-[0.03] pointer-events-none z-0"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }} />

            {/* Layer 2: Navbar (Highest Z-Index) */}
            <StudioNavbar />

            {/* Layer 2: Islands */}
            {leftPanel && (
                <div className="animate-in slide-in-from-left-4 duration-500 delay-100">
                    {leftPanel}
                </div>
            )}

            {rightPanel && (
                <div className="animate-in slide-in-from-right-4 duration-500 delay-100">
                    {rightPanel}
                </div>
            )}

            {/* Layer 1: Main Content (Scrollable) */}
            <main className="relative z-10 min-h-screen pt-32 pb-20 flex justify-center overflow-y-auto overflow-x-hidden">
                <div className="w-full max-w-[calc(100vw-34rem)] px-6 transition-[max-width] duration-300">
                    {children}
                </div>
            </main>

        </div>
    );
}
