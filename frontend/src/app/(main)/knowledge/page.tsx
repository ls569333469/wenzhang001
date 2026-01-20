'use client';

import { useEffect, useState } from 'react';
import { Library, FileText, Clock, RefreshCw, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '@/config/api';
import { Button } from '@/components/ui/button';

interface KnowledgeItem {
  id: string;
  title: string;
  type: string;
  source: string;
  created_at?: string;
}

export default function KnowledgePage() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchKnowledge() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/config/knowledge`);
      if (res.ok) {
        const data = await res.json();
        setItems(data.items || data || []);
      } else {
        // Fallback: Use mock data for MVP
        setItems([
          { id: '1', title: 'Web3 DAO 数据周报', type: 'document', source: 'Lark' },
          { id: '2', title: 'DeFi 协议分析模板', type: 'template', source: 'Lark' },
          { id: '3', title: 'Mimeng 风格指南', type: 'guide', source: 'Local' },
        ]);
      }
    } catch {
      setError('无法连接到知识库服务');
      // Show mock data even on error for demo
      setItems([
        { id: '1', title: 'Web3 DAO 数据周报', type: 'document', source: 'Lark' },
        { id: '2', title: 'DeFi 协议分析模板', type: 'template', source: 'Lark' },
        { id: '3', title: 'Mimeng 风格指南', type: 'guide', source: 'Local' },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchKnowledge();
  }, []);

  return (
    <div className="min-h-screen bg-paper">
      <div className="max-w-4xl mx-auto px-8 py-16 space-y-8">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-zinc-200 flex items-center justify-center">
              <Library className="w-5 h-5 text-ink-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-serif font-medium text-ink-primary">知识库</h1>
              <p className="text-sm text-ink-muted">管理来自飞书和本地的素材</p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchKnowledge}
            disabled={isLoading}
            className="rounded-xl"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </Button>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            <span className="text-sm text-amber-800">{error} (显示演示数据)</span>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-zinc-100 p-4">
            <p className="text-2xl font-serif font-bold text-ink-primary">{items.length}</p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">素材总数</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-100 p-4">
            <p className="text-2xl font-serif font-bold text-ink-primary">
              {items.filter(i => i.source === 'Lark').length}
            </p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">来自飞书</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-100 p-4">
            <p className="text-2xl font-serif font-bold text-ink-primary">
              {items.filter(i => i.source === 'Local').length}
            </p>
            <p className="text-xs text-ink-muted uppercase tracking-wider">本地素材</p>
          </div>
        </div>

        {/* Items List */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <div className="h-px flex-1 bg-zinc-200"></div>
            <span className="text-[10px] font-semibold tracking-widest text-ink-muted uppercase">
              素材列表
            </span>
            <div className="h-px flex-1 bg-zinc-200"></div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-ink-muted" />
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-12 text-ink-muted">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>暂无素材</p>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl border border-zinc-100 p-4 hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-zinc-50 rounded-lg flex items-center justify-center">
                        <FileText className="w-4 h-4 text-zinc-400" />
                      </div>
                      <div>
                        <h3 className="font-medium text-ink-primary">{item.title}</h3>
                        <p className="text-xs text-ink-muted">
                          {item.type} · {item.source}
                        </p>
                      </div>
                    </div>
                    {item.created_at && (
                      <span className="text-xs text-ink-muted flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {item.created_at}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
