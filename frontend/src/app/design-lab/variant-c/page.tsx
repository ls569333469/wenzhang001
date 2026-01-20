import { AlignLeft, Mic, Share2, SquarePen, X } from "lucide-react";

/**
 * Variant C: "Zen Focus" (Immersive)
 * 核心理念: 沉浸、去噪、流体
 * 适用场景: 纯粹的写作与阅读体验
 */
export default function VariantC() {
    return (
        <div className="min-h-screen bg-[#F2F2F2] text-[#1A1A1A] font-serif flex relative transition-colors duration-500">

            {/* 1. Adaptive Header (Transparent) */}
            <header className="fixed top-0 left-0 right-0 h-20 flex items-center justify-between px-8 z-50 pointer-events-none">
                <div className="pointer-events-auto w-10 h-10 bg-white/50 backdrop-blur-md rounded-full flex items-center justify-center hover:bg-white transition-all cursor-pointer shadow-sm">
                    <X className="w-5 h-5 opacity-60" />
                </div>
                <div className="pointer-events-auto flex items-center gap-2 bg-white/80 backdrop-blur-xl px-2 py-1.5 rounded-full shadow-lg border border-white/20">
                    <div className="w-8 h-8 bg-black rounded-full text-white flex items-center justify-center">
                        <SquarePen className="w-4 h-4" />
                    </div>
                    <span className="px-3 font-sans text-sm font-medium">Drafting Mode</span>
                </div>
                <div className="pointer-events-auto w-10 h-10 bg-white/50 backdrop-blur-md rounded-full flex items-center justify-center hover:bg-white transition-all cursor-pointer shadow-sm">
                    <Share2 className="w-4 h-4 opacity-60" />
                </div>
            </header>

            {/* 2. Main Content (Fluid) */}
            <main className="flex-1 flex items-center justify-center p-8">
                <div className="w-full max-w-3xl space-y-8 animate-in fade-in zoom-in duration-500">
                    <input
                        type="text"
                        placeholder="Start with a thought..."
                        className="w-full bg-transparent text-5xl font-serif placeholder:text-zinc-300 focus:outline-none text-center"
                    />
                    <div className="flex justify-center gap-4 opacity-0 hover:opacity-100 transition-opacity duration-500 delay-300">
                        <ActionButton icon={AlignLeft} label="Structure" />
                        <ActionButton icon={Mic} label="Dictate" />
                    </div>
                </div>
            </main>

            {/* 3. Bottom Context (Minimal) */}
            <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur-md px-6 py-3 rounded-2xl shadow-xl flex items-center gap-6 border border-white/50 z-40">
                <div className="text-xs font-sans text-zinc-500 text-center">
                    <div className="font-bold text-zinc-900">3 Agents</div>
                    Active
                </div>
                <div className="w-px h-6 bg-zinc-200" />
                <div className="text-xs font-sans text-zinc-500 text-center">
                    <div className="font-bold text-zinc-900">420</div>
                    Words
                </div>
            </div>

        </div>
    );
}

function ActionButton({ icon: Icon, label }: any) {
    return (
        <button className="flex items-center gap-2 px-6 py-3 bg-white rounded-full shadow-sm hover:shadow-md transition-all font-sans text-sm font-medium text-zinc-600 hover:text-zinc-900">
            <Icon className="w-4 h-4" />
            {label}
        </button>
    )
}
