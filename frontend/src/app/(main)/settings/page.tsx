'use client';

import React, { useEffect, useState } from 'react';
import { cn } from "@/lib/utils";
import { Settings, Key, Globe, Layout, Check, AlertCircle, Sparkles, Loader2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { toast } from 'sonner';
import { DEFAULT_PROMPTS as DEFAULTS } from '@/config/constants';
import { API_BASE_URL } from '@/config/api';
import { PromptEditor } from '@/components/PromptEditor';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4-turbo');
  const [baseUrl, setBaseUrl] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Phase 6: Prompt State
  const [prompts, setPrompts] = useState({
    strategist: DEFAULTS.strategist,
    writer: DEFAULTS.writer,
    critic: DEFAULTS.critic
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

      // 3. Load Prompts from backend first, then localStorage fallback
      try {
        const promptRes = await fetch(`${API_BASE_URL}/config/prompts`);
        if (promptRes.ok) {
          const promptData = await promptRes.json();
          setPrompts({
            strategist: promptData.strategist || DEFAULTS.strategist,
            writer: promptData.writer || DEFAULTS.writer,
            critic: promptData.critic || DEFAULTS.critic
          });
        }
      } catch {
        // Fallback to localStorage
        const pStrat = localStorage.getItem('qs_prompt_strategist');
        const pWriter = localStorage.getItem('qs_prompt_writer');
        const pCritic = localStorage.getItem('qs_prompt_critic');
        setPrompts({
          strategist: pStrat || DEFAULTS.strategist,
          writer: pWriter || DEFAULTS.writer,
          critic: pCritic || DEFAULTS.critic
        });
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
      localStorage.setItem('qs_prompt_strategist', prompts.strategist);
      localStorage.setItem('qs_prompt_writer', prompts.writer);
      localStorage.setItem('qs_prompt_critic', prompts.critic);

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

      // 3. Sync prompts to backend
      const promptAgents = ['strategist', 'writer', 'critic'] as const;
      const promptValues = [prompts.strategist, prompts.writer, prompts.critic];

      await Promise.all(
        promptAgents.map((agent, i) =>
          fetch(`${API_BASE_URL}/config/prompts/${agent}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: promptValues[i] })
          }).catch(() => { }) // Ignore individual failures
        )
      );

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

        {/* API Configuration */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
              <Key className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="flex-1 space-y-1">
              <h3 className="font-medium text-ink-primary">模型提供商</h3>
              <p className="text-xs text-ink-muted">配置 LLM 提供商连接</p>
            </div>
          </div>

          <div className="space-y-4 pl-11">
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">API 密钥</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
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
                placeholder="https://api.openai.com/v1"
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
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-4o">GPT-4o</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="deepseek-chat">DeepSeek V3</option>
              </select>
            </div>
          </div>
        </section>

        {/* Prompt Configuration (P10-6 Enhanced) */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-500" />
              智能体提示词配置
            </h3>
            <span className="text-[10px] text-zinc-400 bg-zinc-100 px-2 py-0.5 rounded-full">
              P10-6 Enhanced
            </span>
          </div>

          <div className="grid grid-cols-1 gap-8">
            {/* Strategist Prompt */}
            <PromptEditor
              label="策略师 (分析阶段)"
              agent="strategist"
              value={prompts.strategist}
              onChange={(v) => setPrompts({ ...prompts, strategist: v })}
              defaultValue={DEFAULTS.strategist}
            />

            {/* Writer Prompt */}
            <PromptEditor
              label="写手 (撰写阶段)"
              agent="writer"
              value={prompts.writer}
              onChange={(v) => setPrompts({ ...prompts, writer: v })}
              defaultValue={DEFAULTS.writer}
            />

            {/* Critic Prompt */}
            <PromptEditor
              label="评论家 (审核阶段)"
              agent="critic"
              value={prompts.critic}
              onChange={(v) => setPrompts({ ...prompts, critic: v })}
              defaultValue={DEFAULTS.critic}
            />
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
      </div>
    </div>
  );
}

