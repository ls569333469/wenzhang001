'use client';

import React, { useEffect, useState } from 'react';
import { cn } from "@/lib/utils";
import { Settings, Key, Globe, Layout, Check, AlertCircle, Sparkles, Loader2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { toast } from 'sonner';
import { DEFAULT_PROMPTS as DEFAULTS } from '@/config/constants';
import { API_BASE_URL } from '@/config/api';

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

      // 1. Try to load from backend first
      try {
        const res = await fetch(`${API_BASE_URL}/config/keys`);
        if (res.ok) {
          const data = await res.json();
          if (data.api_key) setApiKey(data.api_key);
          if (data.model) setModel(data.model);
          if (data.base_url) setBaseUrl(data.base_url);
        }
      } catch {
        // Backend unavailable, fall back to localStorage
        console.log('[Settings] Backend unavailable, using localStorage');
      }

      // 2. Load from localStorage as fallback/override
      const storedKey = localStorage.getItem('qs_api_key');
      const storedModel = localStorage.getItem('qs_model');
      const storedUrl = localStorage.getItem('qs_base_url');
      if (storedKey) setApiKey(storedKey);
      if (storedModel) setModel(storedModel);
      if (storedUrl) setBaseUrl(storedUrl);

      // Load Prompts (always from localStorage)
      const pStrat = localStorage.getItem('qs_prompt_strategist');
      const pWriter = localStorage.getItem('qs_prompt_writer');
      const pCritic = localStorage.getItem('qs_prompt_critic');

      setPrompts({
        strategist: pStrat || DEFAULTS.strategist,
        writer: pWriter || DEFAULTS.writer,
        critic: pCritic || DEFAULTS.critic
      });

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

      // 2. Sync to backend
      const res = await fetch(`${API_BASE_URL}/config/keys`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          model: model,
          base_url: baseUrl
        })
      });

      if (res.ok) {
        toast.success('Configuration saved to server');
      } else {
        toast.success('Saved locally (server sync failed)');
      }
    } catch {
      toast.success('Saved locally (server unavailable)');
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
            <h1 className="text-2xl font-serif font-medium text-ink-primary">System Settings</h1>
            <p className="text-sm text-ink-muted">Configure your Quantum Studio environment</p>
          </div>
        </div>

        {/* API Configuration */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
              <Key className="w-4 h-4 text-indigo-600" />
            </div>
            <div className="flex-1 space-y-1">
              <h3 className="font-medium text-ink-primary">Model Provider</h3>
              <p className="text-xs text-ink-muted">Configure connection to LLM provider</p>
            </div>
          </div>

          <div className="space-y-4 pl-11">
            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
              <p className="text-[10px] text-ink-muted flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                Stored locally in your browser. Never synced to server.
              </p>
            </div>

            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">Base URL (Optional)</label>
              <input
                type="text"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://api.openai.com/v1"
                className="w-full p-2.5 text-sm bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none font-mono"
              />
            </div>

            <div className="grid gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-ink-muted">Model Name</label>
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

        {/* Prompt Configuration (New Phase 6) */}
        <section className="bg-white rounded-2xl shadow-island border border-zinc-100 p-6 space-y-6">
          <h3 className="text-sm font-semibold text-ink-primary flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            Agent Process Configuration
          </h3>

          <div className="grid grid-cols-1 gap-6">
            {/* Strategist Prompt */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-ink-muted uppercase">Strategist Prompt (Analysis)</label>
              <textarea
                value={prompts.strategist}
                onChange={(e) => setPrompts({ ...prompts, strategist: e.target.value })}
                className="w-full h-32 p-3 text-xs bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono leading-relaxed resize-y"
                placeholder="Enter system prompt for Strategist..."
              />
            </div>

            {/* Writer Prompt */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-ink-muted uppercase">Writer Prompt (Drafting)</label>
              <textarea
                value={prompts.writer}
                onChange={(e) => setPrompts({ ...prompts, writer: e.target.value })}
                className="w-full h-32 p-3 text-xs bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono leading-relaxed resize-y"
                placeholder="Enter system prompt for Writer..."
              />
            </div>

            {/* Critic Prompt */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-ink-muted uppercase">Critic Prompt (Review)</label>
              <textarea
                value={prompts.critic}
                onChange={(e) => setPrompts({ ...prompts, critic: e.target.value })}
                className="w-full h-32 p-3 text-xs bg-zinc-50 border border-zinc-200 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary font-mono leading-relaxed resize-y"
                placeholder="Enter system prompt for Critic..."
              />
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
            {isSaving ? 'Saving...' : 'Save Configuration'}
          </Button>
        </div>
      </div>
    </div>
  );
}
