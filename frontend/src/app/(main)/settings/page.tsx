'use client';

import * as React from 'react';
import { Eye, EyeOff, Save } from "lucide-react";

/**
 * Settings Page v8.0: Digital Luxury Aesthetic
 * 
 * Design: Clean editorial layout, generous spacing
 * Typography-driven hierarchy, no heavy card borders
 */

export default function SettingsPage() {
  const [showApiKey, setShowApiKey] = React.useState(false);
  const [temperature, setTemperature] = React.useState(0.7);

  return (
    <div className="h-full flex flex-col bg-paper overflow-hidden">
      {/* Header */}
      <div className="px-8 pt-8 pb-6 shrink-0">
        <h1 className="text-2xl font-serif font-medium text-ink-primary tracking-tight">
          系统设置
        </h1>
        <p className="text-sm text-ink-muted/60 mt-1">
          配置模型参数与集成服务
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-8 pb-32">
        <div className="max-w-xl space-y-12">

          {/* Section: Model */}
          <section className="space-y-6">
            <h2 className="text-xs font-medium text-ink-muted/60 uppercase tracking-widest">
              模型配置
            </h2>

            <div className="space-y-8">
              {/* Provider */}
              <div className="space-y-2">
                <label className="text-sm text-ink-muted">
                  LLM Provider
                </label>
                <select className="w-full py-2.5 text-ink-primary bg-transparent border-b border-hairline/50 focus:border-ink-primary focus:outline-none transition-colors cursor-pointer">
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="gemini">Google (Gemini)</option>
                  <option value="volcengine">火山引擎 (Doubao)</option>
                </select>
              </div>

              {/* API Key */}
              <div className="space-y-2">
                <label className="text-sm text-ink-muted">
                  API Key
                </label>
                <div className="relative">
                  <input
                    type={showApiKey ? "text" : "password"}
                    placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
                    className="w-full py-2.5 pr-10 text-ink-primary bg-transparent border-b border-hairline/50 focus:border-ink-primary focus:outline-none transition-colors font-mono text-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-0 top-1/2 -translate-y-1/2 p-2 text-ink-muted/50 hover:text-ink-primary transition-colors"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Temperature */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-ink-muted">
                    Temperature
                  </label>
                  <span className="text-sm font-mono text-ink-primary">
                    {temperature.toFixed(1)}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full h-1 bg-hairline/50 rounded-full appearance-none cursor-pointer accent-zinc-900"
                />
                <div className="flex justify-between text-[10px] text-ink-muted/50">
                  <span>保守</span>
                  <span>创意</span>
                </div>
              </div>
            </div>
          </section>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-hairline/50 to-transparent" />

          {/* Section: System Prompt */}
          <section className="space-y-6">
            <h2 className="text-xs font-medium text-ink-muted/60 uppercase tracking-widest">
              系统提示词
            </h2>

            <textarea
              placeholder="定义 AI 的角色和行为准则..."
              className="w-full py-3 text-ink-primary bg-transparent border-b border-hairline/50 focus:border-ink-primary focus:outline-none transition-colors resize-none min-h-[140px] text-sm leading-relaxed"
              defaultValue="你是一位专业的 Web3 投研分析师，擅长撰写深度分析文章。你的写作风格专业严谨，善于用数据和案例支撑观点。"
            />
          </section>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-hairline/50 to-transparent" />

          {/* Section: Integrations */}
          <section className="space-y-6">
            <h2 className="text-xs font-medium text-ink-muted/60 uppercase tracking-widest">
              飞书集成
            </h2>

            <div className="space-y-8">
              <div className="space-y-2">
                <label className="text-sm text-ink-muted">App ID</label>
                <input
                  type="text"
                  placeholder="cli_xxxxxxxxxxxxxxxx"
                  className="w-full py-2.5 text-ink-primary bg-transparent border-b border-hairline/50 focus:border-ink-primary focus:outline-none transition-colors font-mono text-sm"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-ink-muted">App Secret</label>
                <input
                  type="password"
                  placeholder="xxxxxxxxxxxxxxxxxxxxxxxx"
                  className="w-full py-2.5 text-ink-primary bg-transparent border-b border-hairline/50 focus:border-ink-primary focus:outline-none transition-colors font-mono text-sm"
                />
              </div>
            </div>
          </section>
        </div>
      </div>

      {/* Floating Save Button */}
      <div className="absolute bottom-0 left-0 right-0 pointer-events-none">
        <div className="h-20 bg-gradient-to-t from-paper via-paper/95 to-transparent" />
        <div className="bg-paper px-8 pb-6 pointer-events-auto">
          <div className="max-w-xl">
            <button className="flex items-center gap-2 px-6 py-2.5 bg-zinc-900 text-white rounded-md hover:bg-zinc-800 transition-all text-sm font-medium shadow-lg shadow-zinc-900/10 ml-auto">
              <Save className="w-4 h-4 opacity-70" />
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
