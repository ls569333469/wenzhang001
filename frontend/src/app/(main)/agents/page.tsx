
import { Users } from 'lucide-react';

export default function AgentsPage() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center p-8 text-ink-secondary">
            <div className="w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center mb-6">
                <Users className="w-8 h-8 text-zinc-400" />
            </div>
            <h1 className="text-2xl font-serif font-bold text-ink-primary mb-2">智能体团队</h1>
            <p className="max-w-md mx-auto mb-8">
                正在施工中... 这里将显示所有可用的智能体及其状态。
            </p>
            <div className="text-xs font-mono bg-zinc-50 px-3 py-1 rounded border border-zinc-200">
                Route: /agents
            </div>
        </div>
    );
}
