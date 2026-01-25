'use client';

import { useEffect, useState } from 'react';
import { Database, FolderOpen, Play, Pause, RefreshCw, AlertCircle, CheckCircle2, Clock, Loader2, ChevronRight, ArrowLeft, X, FileText } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface IngestStatus {
  hash_cache_count: number;
  lark_record_count: number;
  status: string;
}

interface FolderInfo {
  name: string;
  total_count: number;
  processed_count: number;
  pending_count: number;
  status: 'completed' | 'partial' | 'pending' | 'empty';
}

export default function KnowledgePage() {
  const [ingestStatus, setIngestStatus] = useState<IngestStatus | null>(null);
  const [folders, setFolders] = useState<FolderInfo[]>([]);
  const [history, setHistory] = useState<{ timestamp: string; status: string }[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [ingestMode, setIngestMode] = useState<'optimized' | 'legacy'>('optimized');
  const [dataSource, setDataSource] = useState<'web3' | 'web2' | 'custom'>('web3');
  const [customPath, setCustomPath] = useState<string>('');
  const [showBrowser, setShowBrowser] = useState(false);
  const [browserItems, setBrowserItems] = useState<{ name: string; path: string; children_count: number }[]>([]);
  const [browserFiles, setBrowserFiles] = useState<{ name: string; path: string; size: number; ext: string }[]>([]);
  const [browserPath, setBrowserPath] = useState('');
  const [browserParent, setBrowserParent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 费用计算常量
  const COST_PER_RECORD = 0.012; // ¥0.012/条

  async function fetchStatus() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/status`);
      if (res.ok) {
        const data = await res.json();
        setIngestStatus(data);
      } else {
        setError('无法获取入库状态');
      }
    } catch {
      setError('后端服务不可用');
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchFolders() {
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/folders?source=${dataSource}`);
      if (res.ok) {
        const data = await res.json();
        setFolders(data.folders || []);
      } else {
        setFolders([]);
      }
    } catch {
      setFolders([]);
    }
  }

  async function fetchHistory() {
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      }
    } catch {
      // ignore
    }
  }

  async function browsePath(path: string = '') {
    try {
      const url = path ? `${API_BASE_URL}/ingest/browse?path=${encodeURIComponent(path)}` : `${API_BASE_URL}/ingest/browse`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setBrowserItems(data.items || []);
        setBrowserFiles(data.files || []);
        setBrowserPath(data.current_path || '');
        setBrowserParent(data.parent_path);
      }
    } catch {
      toast.error('无法浏览目录');
    }
  }

  function openBrowser() {
    setShowBrowser(true);
    browsePath();
  }

  function selectDirectory(path: string) {
    setCustomPath(path);
    setDataSource('custom');
    setShowBrowser(false);
    toast.success(`已选择: ${path.split('\\').pop()}`);
  }

  async function handleStartIngest() {
    setIsRunning(true);
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: ingestMode, source: dataSource })
      });
      if (res.ok) {
        toast.success('入库任务已启动');
        // Refresh status after a delay
        setTimeout(fetchStatus, 2000);
      } else {
        toast.error('启动失败');
        setIsRunning(false);
      }
    } catch {
      toast.error('请求失败');
      setIsRunning(false);
    }
  }

  async function handlePause() {
    try {
      const res = await fetch(`${API_BASE_URL}/ingest/pause`, { method: 'POST' });
      if (res.ok) {
        toast.success('已暂停');
        setIsRunning(false);
      }
    } catch {
      toast.error('暂停失败');
    }
  }

  useEffect(() => {
    fetchStatus();
    fetchFolders();
    fetchHistory();
  }, [dataSource]);

  const pendingCount = folders.reduce((sum, f) => sum + f.pending_count, 0);
  const processedCount = folders.reduce((sum, f) => sum + f.processed_count, 0);
  const estimatedCost = (pendingCount * COST_PER_RECORD).toFixed(2);

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-4xl mx-auto px-8 py-16 space-y-8">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-zinc-200 flex items-center justify-center">
              <Database className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-2xl font-serif font-medium text-ink-primary">Knowledge 数据管理</h1>
              <p className="text-sm text-ink-muted">批量入库与状态监控</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => { fetchStatus(); fetchFolders(); }}
            disabled={isLoading}
            className="rounded-xl"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新状态
          </Button>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            <span className="text-sm text-amber-800">{error}</span>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-1">
            <p className="text-2xl font-serif font-bold text-ink-primary">
              {ingestStatus?.hash_cache_count?.toLocaleString() ?? '-'}
            </p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">Hash 缓存</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-1">
            <p className="text-2xl font-serif font-bold text-ink-primary">
              {ingestStatus?.lark_record_count?.toLocaleString() ?? '-'}
            </p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">Lark 记录</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-1">
            <p className="text-2xl font-serif font-bold text-ink-primary">{folders.length}</p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">总文件夹</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-1">
            <p className="text-2xl font-serif font-bold text-emerald-600">¥{estimatedCost}</p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">预估费用 ({pendingCount}条)</p>
          </div>
        </div>

        {/* Config Section */}
        <div className="grid grid-cols-2 gap-4">
          {/* Data Source (Placeholder) */}
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-ink-primary">数据源</h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="source"
                  checked={dataSource === 'web3'}
                  onChange={() => setDataSource('web3')}
                  className="text-primary"
                />
                <span className="text-sm">Web3素材 (41 文件夹)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="source"
                  checked={dataSource === 'web2'}
                  onChange={() => setDataSource('web2')}
                  className="text-primary"
                />
                <span className="text-sm">Web2风格</span>
              </label>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="source"
                    checked={dataSource === 'custom'}
                    onChange={() => { }}
                    className="text-primary"
                  />
                  <span className="text-sm">自定义目录</span>
                </label>
                <Button variant="outline" size="sm" onClick={openBrowser} className="h-6 text-xs">
                  浏览...
                </Button>
              </div>
              {dataSource === 'custom' && customPath && (
                <p className="text-xs text-ink-muted pl-5 truncate">
                  └ {customPath.split('\\').pop()}
                </p>
              )}
            </div>
          </div>

          {/* A/B Mode */}
          <div className="bg-white rounded-xl border border-zinc-100 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-ink-primary">入库方案</h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mode"
                  checked={ingestMode === 'optimized'}
                  onChange={() => setIngestMode('optimized')}
                  className="text-primary"
                />
                <span className="text-sm">方案B - 优化版 (推荐)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="mode"
                  checked={ingestMode === 'legacy'}
                  onChange={() => setIngestMode('legacy')}
                  className="text-primary"
                />
                <span className="text-sm">方案A - 旧版 (兜底)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Folders List */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-zinc-200"></div>
            <span className="text-[10px] font-semibold tracking-widest text-ink-muted uppercase">
              文件夹列表
            </span>
            <div className="h-px flex-1 bg-zinc-200"></div>
          </div>

          <div className="bg-white rounded-xl border border-zinc-100 divide-y divide-zinc-100 max-h-80 overflow-y-auto">
            {folders.map((folder) => (
              <div key={folder.name} className="flex items-center justify-between p-3 hover:bg-zinc-50">
                <div className="flex items-center gap-3">
                  <FolderOpen className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-ink-primary truncate max-w-[200px]">{folder.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  {/* 显示 已入库/总数 */}
                  <span className="text-xs font-mono text-ink-muted">
                    {folder.processed_count}/{folder.total_count}
                  </span>
                  {folder.status === 'completed' && (
                    <span className="flex items-center gap-1 text-xs text-emerald-600">
                      <CheckCircle2 className="w-3 h-3" />
                      全部完成
                    </span>
                  )}
                  {folder.status === 'partial' && (
                    <span className="flex items-center gap-1 text-xs text-amber-600">
                      <Clock className="w-3 h-3" />
                      +{folder.pending_count} 新增
                    </span>
                  )}
                  {folder.status === 'pending' && (
                    <span className="flex items-center gap-1 text-xs text-zinc-400">
                      <Clock className="w-3 h-3" />
                      待处理
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={handleStartIngest}
            disabled={isRunning}
            className="bg-primary text-white hover:bg-primary/90 rounded-xl shadow-lg shadow-primary/20"
          >
            {isRunning ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            {isRunning ? '入库中...' : '开始入库'}
          </Button>
          <Button
            variant="outline"
            onClick={handlePause}
            disabled={!isRunning}
            className="rounded-xl"
          >
            <Pause className="w-4 h-4 mr-2" />
            暂停
          </Button>
        </div>

        {/* Cost Info */}
        <div className="text-xs text-ink-muted bg-zinc-50 rounded-lg p-3">
          <p>💡 费用说明: 基于历史数据 (5,806 条 = ¥65)，单条成本约 ¥0.012</p>
          <p className="mt-1">📊 增量更新: 系统自动检测新文件，已处理文件会跳过</p>
        </div>
      </div>

      {/* Directory Browser Modal */}
      {showBrowser && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[100]" onClick={() => setShowBrowser(false)}>
          <div
            className="bg-white rounded-2xl shadow-2xl w-[600px] h-[600px] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-zinc-50 rounded-t-2xl">
              <h3 className="font-semibold text-ink-primary text-lg">选择数据目录</h3>
              <button onClick={() => setShowBrowser(false)} className="text-ink-muted hover:text-ink-primary p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Path Input */}
            <div className="p-3 border-b bg-white">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={browserPath}
                  onChange={(e) => setBrowserPath(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && browsePath(browserPath)}
                  className="flex-1 px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="输入路径，如：D:\测试222"
                />
                <Button size="sm" onClick={() => browsePath(browserPath)}>
                  前往
                </Button>
              </div>
            </div>

            {/* Breadcrumb Navigation */}
            <div className="px-4 py-2 bg-zinc-50 border-b flex items-center gap-1 text-sm overflow-x-auto">
              {browserPath.split('\\').filter(Boolean).map((part, index, arr) => {
                const fullPath = arr.slice(0, index + 1).join('\\');
                return (
                  <span key={index} className="flex items-center">
                    {index > 0 && <ChevronRight className="w-3 h-3 text-zinc-400 mx-1" />}
                    <button
                      onClick={() => browsePath(fullPath.includes(':') ? fullPath : fullPath + '\\')}
                      className="text-primary hover:underline"
                    >
                      {part}
                    </button>
                  </span>
                );
              })}
            </div>

            {/* Parent Button */}
            {browserParent && (
              <button
                onClick={() => browsePath(browserParent)}
                className="flex items-center gap-2 px-4 py-2 text-sm text-ink-muted hover:bg-zinc-100 border-b"
              >
                <ArrowLeft className="w-4 h-4" />
                返回上级目录
              </button>
            )}

            {/* Directory List */}
            <div className="flex-1 overflow-y-auto">
              {browserItems.length === 0 ? (
                <div className="p-8 text-center text-ink-muted text-sm">
                  <FolderOpen className="w-12 h-12 mx-auto mb-2 text-zinc-300" />
                  此目录为空或无访问权限
                </div>
              ) : (
                browserItems.map((item) => (
                  <div
                    key={item.path}
                    className="flex items-center justify-between px-4 py-3 hover:bg-zinc-50 border-b border-zinc-100 group"
                  >
                    <button
                      onClick={() => browsePath(item.path)}
                      className="flex items-center gap-3 text-left flex-1 min-w-0"
                    >
                      <FolderOpen className="w-5 h-5 text-amber-500 shrink-0" />
                      <span className="text-sm text-ink-primary truncate">{item.name}</span>
                      <span className="text-xs text-ink-muted shrink-0">({item.children_count} 项)</span>
                    </button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); selectDirectory(item.path); }}
                      className="h-7 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      选择此目录
                    </Button>
                  </div>
                ))
              )}

              {/* 文件列表 */}
              {browserFiles.length > 0 && (
                <>
                  <div className="px-4 py-2 bg-zinc-100 text-xs text-ink-muted font-medium">
                    文件 ({browserFiles.length} 个)
                  </div>
                  {browserFiles.map((file) => (
                    <div
                      key={file.path}
                      className="flex items-center gap-3 px-4 py-2 text-ink-muted border-b border-zinc-100"
                    >
                      <FileText className="w-4 h-4 text-zinc-400 shrink-0" />
                      <span className="text-sm truncate">{file.name}</span>
                      <span className="text-xs text-zinc-400 shrink-0">
                        {file.size > 1024 ? `${(file.size / 1024).toFixed(1)} KB` : `${file.size} B`}
                      </span>
                    </div>
                  ))}
                </>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t bg-zinc-50 rounded-b-2xl flex justify-between items-center">
              <span className="text-xs text-ink-muted truncate max-w-[300px]">
                当前: {browserPath}
              </span>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setShowBrowser(false)}>
                  取消
                </Button>
                <Button onClick={() => selectDirectory(browserPath)}>
                  选择当前目录
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
