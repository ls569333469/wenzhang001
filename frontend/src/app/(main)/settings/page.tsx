'use client';

import React, { useEffect, useState } from 'react';
import { cn } from "@/lib/utils";
import { Settings, Key, Globe, Layout, Check, AlertCircle, Sparkles, Loader2, FlaskConical, Database, FolderOpen } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { toast } from 'sonner';
import { DEFAULT_PROMPTS as DEFAULTS } from '@/config/constants';
import { API_BASE_URL } from '@/config/api';
import { PromptEditor } from '@/components/PromptEditor';
import { PromptManager } from '@/features/settings/components/PromptManager';
import { AgentModelConfig } from '@/features/settings/AgentModelConfig';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4-turbo');
  const [baseUrl, setBaseUrl] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // P14-B: Provider Keys and Agent Config
  const [providerKeys, setProviderKeys] = useState<Record<string, string>>({});



  // Phase 12: Feature Flags
  const [useKnowledgeRepo, setUseKnowledgeRepo] = useState(false);

  // Phase 14: 数据清洗配置
  const [ingestConfig, setIngestConfig] = useState({
    web3TableId: '',
    web2TableId: '',
    scoreThreshold: 6
  });

  useEffect(() => {
    async function loadSettings() {
      setIsLoading(true);

      // 1. Try to load API keys from backend
      try {
        const res = await fetch(`${API_BASE_URL}/config/keys`);
        if (res.ok) {
          const data = await res.json();
          if (data.api_key) setApiKey(data.api_key);
          if (data.model) setModel(data.model);
          if (data.base_url) setBaseUrl(data.base_url);
        }
      } catch {
        console.log('[Settings] Backend unavailable, using localStorage');
      }

      // 2. Load from localStorage as fallback/override
      const storedKey = localStorage.getItem('qs_api_key');
      const storedModel = localStorage.getItem('qs_model');
      const storedUrl = localStorage.getItem('qs_base_url');
      if (storedKey) setApiKey(storedKey);
      if (storedModel) setModel(storedModel);
      if (storedUrl) setBaseUrl(storedUrl);

      // P14-B: Load Provider Keys
      try {
        const storedKeys = localStorage.getItem('qs_provider_keys');
        if (storedKeys) {
          setProviderKeys(JSON.parse(storedKeys));
        }
      } catch (e) {
        console.error('Failed to parse provider keys', e);
      }



      // 4. Load Feature Flags
      try {
        const flagRes = await fetch(`${API_BASE_URL}/config/feature-flags`);
        if (flagRes.ok) {
          const flagData = await flagRes.json();
          setUseKnowledgeRepo(flagData.use_knowledge_repo || false);
        }
      } catch {
        console.log('[Settings] Feature flags unavailable');
      }

      // 5. Load Ingest Config
      try {
        const ingestRes = await fetch(`${API_BASE_URL}/config/ingest`);
        if (ingestRes.ok) {
          const ingestData = await ingestRes.json();
          setIngestConfig({
            web3TableId: ingestData.web3_table_id || '',
            web2TableId: ingestData.web2_table_id || '',
            scoreThreshold: ingestData.score_threshold || 6
          });
        }
      } catch {
        console.log('[Settings] Ingest config unavailable');
      }

      setIsLoading(false);
    }

    loadSettings();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // 1. Save to localStorage (always works)
      localStorage.setItem('qs_api_key', apiKey);
      localStorage.setItem('qs_model', model);
      localStorage.setItem('qs_base_url', baseUrl);


      // P14-B: Save Provider Keys
      localStorage.setItem('qs_provider_keys', JSON.stringify(providerKeys));

      // 2. Sync API keys to backend
      const res = await fetch(`${API_BASE_URL}/config/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          model: model,
          base_url: baseUrl
        })
      });



      // 4. Sync feature flags to backend
      await fetch(`${API_BASE_URL}/config/feature-flags`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          use_knowledge_repo: useKnowledgeRepo
        })
      }).catch(() => { });

      // 5. Save ingest config to backend
      await fetch(`${API_BASE_URL}/config/ingest`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          web3_table_id: ingestConfig.web3TableId,
          web2_table_id: ingestConfig.web2TableId,
          score_threshold: ingestConfig.scoreThreshold
        })
      }).catch(() => { });

      if (res.ok) {
        toast.success('配置已保存到服务器');
      } else {
        toast.success('已保存到本地 (服务器同步失败)');
      }
    } catch {
      toast.success('已保存到本地 (服务器不可用)');
    } finally {
      setIsSaving(false);
    }
  };

  const updateProviderKey = (provider: string, key: string) => {
    setProviderKeys(prev => ({ ...prev, [provider]: key }));
  };

  return (
    <div className="flex flex-col h-full bg-canvas overflow-y-auto">
      <div className="max-w-3xl mx-auto w-full p-8 space-y-8">
        {/* Header */}
        <div className="flex items-center gap-3 pb-6 border-b border-zinc-100">
          <div className="w-10 h-10 bg-white rounded-xl shadow-sm border border-zinc-200 flex items-center justify-center">
            <Settings className="w-5 h-5 text-ink-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-serif font-medium text-ink-primary">系统设置</h1>
            <p className="text-sm text-ink-muted">配置您的 Quantum Studio 环境</p>
          </div>
        </div>

        {/* P14-B: Provider Configuration */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-medium text-ink-primary">模型接入配置</h2>
              <p className="text-sm text-ink-muted">配置各 AI 平台的 API Key，未配置的平台将无法使用。</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {[
              { id: 'volcengine', label: '火山引擎', placeholder: 'ak-...' },
              { id: 'google', label: 'Google Gemini', placeholder: 'AIza...' },
            ].map(p => (
              <div key={p.id} className="space-y-2">
                <label className="text-sm font-medium text-gray-700">{p.label}</label>
                <input
                  type="password"
                  value={providerKeys[p.id] || ''}
                  onChange={(e) => updateProviderKey(p.id, e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-50 border border-zinc-200 rounded-lg text-sm"
                  placeholder={p.placeholder}
                />
              </div>
            ))}
          </div>
        </section>

        {/* P14-B: Agent Model Allocation (includes P14-C Mode Writer config) */}
        <section>
          <AgentModelConfig apiKeys={providerKeys} />
        </section>

        {/* Existing API Configuration (Legacy/Global) */}
        {/* Legacy API Configuration - 保留用于全局兼容 */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
              <Key className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="flex-1 space-y-1">
              <h3 className="font-medium text-ink-primary">全局 API 配置 (Legacy)</h3>
              <p className="text-xs text-ink-muted">兼容旧版流程，建议使用上方"模型接入配置"</p>
            </div>
          </div>

          <div className="space-y-4 pl-11">
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">API 密钥</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="ak-... 或 AIza..."
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
              <p className="text-[10px] text-ink-muted flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                存储在本地浏览器中，不会上传到服务器
              </p>
            </div>

            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">基础 URL (可选)</label>
              <input
                type="text"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://ark.cn-beijing.volces.com/api/v3"
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
            </div>

            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">模型名称</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none cursor-pointer"
              >
                <option value="doubao-seed-2-0-lite-260215">豆包 Seed 2.0 Lite (推荐)</option>
                <option value="deepseek-v3-2-251201">DeepSeek V3.2</option>
                <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                <option value="gemini-3-pro-preview">Gemini 3 Pro Preview</option>
              </select>
            </div>
          </div>
        </section>

        {/* P15: Full Agent Prompt Editor */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-500" />
              智能体提示词配置 (P15)
            </h3>
            <span className="text-[10px] text-zinc-400 bg-zinc-100 px-2 py-0.5 rounded-full">
              New
            </span>
          </div>

          <PromptManager />
        </section>

        {/* Data Ingest Configuration (P14) */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center shrink-0">
              <Database className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="flex-1 space-y-1">
              <h3 className="font-medium text-ink-primary">数据清洗配置</h3>
              <p className="text-xs text-ink-muted">配置 Lark 表格和入库参数</p>
            </div>
          </div>

          <div className="space-y-4 pl-11">
            {/* Web3 Table ID */}
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">Web3 Knowledge 表格 ID</label>
              <input
                type="text"
                value={ingestConfig.web3TableId}
                onChange={(e) => setIngestConfig({ ...ingestConfig, web3TableId: e.target.value })}
                placeholder="tblkvQK9aKxP0wsk"
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
            </div>

            {/* Web2 Table ID */}
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">Web2 Style 表格 ID</label>
              <input
                type="text"
                value={ingestConfig.web2TableId}
                onChange={(e) => setIngestConfig({ ...ingestConfig, web2TableId: e.target.value })}
                placeholder="tblXXXXXXXX (可选)"
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
            </div>

            {/* Score Threshold */}
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">
                LLM 评分阈值 (低于此分数不入库)
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={ingestConfig.scoreThreshold}
                  onChange={(e) => setIngestConfig({ ...ingestConfig, scoreThreshold: parseInt(e.target.value) })}
                  className="flex-1 h-2 bg-zinc-200 rounded-lg appearance-none cursor-pointer"
                />
                <span className="w-12 text-center text-sm font-mono bg-zinc-100 rounded-lg py-1">
                  {ingestConfig.scoreThreshold} 分
                </span>
              </div>
              <p className="text-[10px] text-ink-muted">
                推荐值: 6 分 (过滤低质量内容)
              </p>
            </div>
          </div>
        </section>

        {/* Experimental Features (P12) */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
              <FlaskConical className="w-4 h-4 text-amber-500" />
              实验性功能
            </h3>
            <span className="text-[10px] text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
              Feature Flags
            </span>
          </div>

          <div className="pl-6 space-y-4">
            {/* Knowledge Repo Toggle */}
            <div className="flex items-center justify-between p-4 bg-zinc-50 rounded-xl">
              <div className="flex-1">
                <label className="text-sm font-medium text-ink-primary">
                  启用 Knowledge_Repo 知识检索
                </label>
                <p className="text-xs text-ink-muted mt-1">
                  策略师将从 Web3 知识库检索相关背景，提升内容专业性
                </p>
              </div>
              <button
                onClick={() => setUseKnowledgeRepo(!useKnowledgeRepo)}
                className={cn(
                  "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                  useKnowledgeRepo ? "bg-primary" : "bg-zinc-200"
                )}
              >
                <span
                  className={cn(
                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm",
                    useKnowledgeRepo ? "translate-x-6" : "translate-x-1"
                  )}
                />
              </button>
            </div>
          </div>
        </section>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <Button
            onClick={handleSave}
            disabled={isSaving || isLoading}
            className="bg-primary text-white hover:bg-primary/90 rounded-xl shadow-lg shadow-primary/20"
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Check className="w-4 h-4 mr-2" />
            )}
            {isSaving ? '保存中...' : '保存配置'}
          </Button>
        </div>
      </div >
    </div >
  );
}

