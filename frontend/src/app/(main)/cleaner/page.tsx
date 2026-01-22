"use client";

import { useState, useEffect } from "react";
import {
    Database, FolderOpen, Play, Pause, RefreshCw,
    CheckCircle, XCircle, Clock, FileText, Brain
} from "lucide-react";

interface CleanerStats {
    style_count: number;
    knowledge_count: number;
    pending_files: number;
}

interface SourceDir {
    name: string;
    path: string;
    file_count: number;
    children: SourceDir[];
}

interface CleanerJob {
    id: string;
    status: string;
    input_path: string;
    target: string;
    progress: number;
    processed: number;
    uploaded: number;
    created_at: string;
    error?: string;
}

export default function CleanerPage() {
    const [stats, setStats] = useState<CleanerStats | null>(null);
    const [sources, setSources] = useState<SourceDir[]>([]);
    const [jobs, setJobs] = useState<CleanerJob[]>([]);
    const [selectedPath, setSelectedPath] = useState("");
    const [target, setTarget] = useState("knowledge");
    const [provider, setProvider] = useState("deepseek");
    const [loading, setLoading] = useState(false);

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // 加载统计
    const loadStats = async () => {
        try {
            const res = await fetch(`${apiBase}/cleaner/stats`);
            const data = await res.json();
            setStats(data);
        } catch (e) {
            console.error("Failed to load stats:", e);
        }
    };

    // 加载源目录
    const loadSources = async () => {
        try {
            const res = await fetch(`${apiBase}/cleaner/sources`);
            const data = await res.json();
            setSources(data.sources || []);
        } catch (e) {
            console.error("Failed to load sources:", e);
        }
    };

    // 加载任务
    const loadJobs = async () => {
        try {
            const res = await fetch(`${apiBase}/cleaner/jobs`);
            const data = await res.json();
            setJobs(data.jobs || []);
        } catch (e) {
            console.error("Failed to load jobs:", e);
        }
    };

    // 创建任务
    const createJob = async () => {
        if (!selectedPath) return;
        setLoading(true);
        try {
            const res = await fetch(`${apiBase}/cleaner/jobs`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    input_path: selectedPath,
                    target,
                    provider,
                    mode: "auto"
                })
            });
            const data = await res.json();
            await loadJobs();
        } catch (e) {
            console.error("Failed to create job:", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadStats();
        loadSources();
        loadJobs();
        const interval = setInterval(loadJobs, 5000);
        return () => clearInterval(interval);
    }, []);

    const renderSourceTree = (items: SourceDir[], depth = 0) => {
        return items.map((item) => (
            <div key={item.path} style={{ marginLeft: depth * 16 }}>
                <button
                    onClick={() => setSelectedPath(item.path)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm w-full text-left transition-colors ${selectedPath === item.path
                            ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                            : "hover:bg-white/5 text-gray-300"
                        }`}
                >
                    <FolderOpen size={16} className="text-yellow-500" />
                    <span>{item.name}</span>
                    {item.file_count > 0 && (
                        <span className="ml-auto text-xs text-gray-500">{item.file_count}</span>
                    )}
                </button>
                {item.children && item.children.length > 0 && (
                    <div className="ml-2 border-l border-white/10">
                        {renderSourceTree(item.children, depth + 1)}
                    </div>
                )}
            </div>
        ));
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "completed": return <CheckCircle className="text-green-500" size={18} />;
            case "failed": return <XCircle className="text-red-500" size={18} />;
            case "running": return <RefreshCw className="text-blue-500 animate-spin" size={18} />;
            default: return <Clock className="text-gray-500" size={18} />;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <Brain className="text-purple-400" size={32} />
                        <h1 className="text-2xl font-bold">数据清洗控制中心</h1>
                    </div>
                    <button
                        onClick={() => { loadStats(); loadJobs(); }}
                        className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <RefreshCw size={16} />
                        刷新
                    </button>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-3 gap-4 mb-8">
                    <div className="bg-gradient-to-br from-pink-500/10 to-pink-500/5 border border-pink-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                                <span className="text-xl">🩸</span>
                            </div>
                            <span className="text-pink-400 font-medium">Style_Repo</span>
                        </div>
                        <div className="text-3xl font-bold">{stats?.style_count || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">风格切片素材</div>
                    </div>

                    <div className="bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                                <span className="text-xl">🥩</span>
                            </div>
                            <span className="text-orange-400 font-medium">Knowledge_Repo</span>
                        </div>
                        <div className="text-3xl font-bold">{stats?.knowledge_count || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">Web3 知识素材</div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                                <FileText className="text-blue-400" size={20} />
                            </div>
                            <span className="text-blue-400 font-medium">待处理文件</span>
                        </div>
                        <div className="text-3xl font-bold">{stats?.pending_files || 0}</div>
                        <div className="text-sm text-gray-400 mt-1">JSON + TXT 文件</div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                    {/* 左侧: 新建任务 */}
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Play size={18} className="text-green-400" />
                            新建清洗任务
                        </h2>

                        {/* 目录选择 */}
                        <div className="mb-4">
                            <label className="text-sm text-gray-400 mb-2 block">选择素材目录</label>
                            <div className="bg-black/30 border border-white/10 rounded-lg p-3 max-h-48 overflow-y-auto">
                                {sources.length > 0 ? renderSourceTree(sources) : (
                                    <div className="text-gray-500 text-sm">加载中...</div>
                                )}
                            </div>
                            {selectedPath && (
                                <div className="mt-2 text-sm text-blue-400">
                                    已选择: {selectedPath}
                                </div>
                            )}
                        </div>

                        {/* 配置 */}
                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="text-sm text-gray-400 mb-2 block">目标存储库</label>
                                <select
                                    value={target}
                                    onChange={(e) => setTarget(e.target.value)}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm"
                                >
                                    <option value="knowledge">Knowledge_Repo (肉)</option>
                                    <option value="style">Style_Repo (血)</option>
                                </select>
                            </div>
                            <div>
                                <label className="text-sm text-gray-400 mb-2 block">AI 模型</label>
                                <select
                                    value={provider}
                                    onChange={(e) => setProvider(e.target.value)}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm"
                                >
                                    <option value="deepseek">DeepSeek V3.2 (推荐)</option>
                                    <option value="doubao">豆包 Seed</option>
                                </select>
                            </div>
                        </div>

                        {/* 启动按钮 */}
                        <button
                            onClick={createJob}
                            disabled={!selectedPath || loading}
                            className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-all flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <RefreshCw className="animate-spin" size={18} />
                            ) : (
                                <Play size={18} />
                            )}
                            启动任务
                        </button>
                    </div>

                    {/* 右侧: 任务队列 */}
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Database size={18} className="text-purple-400" />
                            任务队列
                        </h2>

                        <div className="space-y-3">
                            {jobs.length === 0 ? (
                                <div className="text-gray-500 text-sm text-center py-8">
                                    暂无任务
                                </div>
                            ) : (
                                jobs.slice().reverse().map((job) => (
                                    <div
                                        key={job.id}
                                        className="bg-black/30 border border-white/10 rounded-lg p-4"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                {getStatusIcon(job.status)}
                                                <span className="font-medium text-sm">{job.input_path.split('/').pop()}</span>
                                            </div>
                                            <span className={`text-xs px-2 py-1 rounded ${job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                                                    job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                                                        job.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                                                            'bg-gray-500/20 text-gray-400'
                                                }`}>
                                                {job.status}
                                            </span>
                                        </div>

                                        {job.status === 'running' && (
                                            <div className="mt-2">
                                                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                                                        style={{ width: `${job.progress}%` }}
                                                    />
                                                </div>
                                                <div className="flex justify-between text-xs text-gray-500 mt-1">
                                                    <span>已处理: {job.processed}</span>
                                                    <span>已入库: {job.uploaded}</span>
                                                </div>
                                            </div>
                                        )}

                                        {job.status === 'completed' && (
                                            <div className="text-xs text-gray-400 mt-1">
                                                处理 {job.processed} → 入库 {job.uploaded}
                                            </div>
                                        )}

                                        {job.error && (
                                            <div className="text-xs text-red-400 mt-2">
                                                错误: {job.error}
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
