# P31: 投研 LangGraph 管线设计（v3 终稿）

> 最后更新: 2026-02-27 15:55 | 状态: 已实施

## 管线架构

```
投研模式（project_research, 空输入）：
  🔭 侦察官 → 🔬 策略官 → 📋 审核官(清洗) → ✍️ 写手 → ✨ 润色官

投研模式（project_research, 有输入）：
  🔬 策略官 → 📋 审核官(清洗) → ✍️ 写手 → ✨ 润色官

普通模式（不变）：
  🔬 策略官 → ✍️ 写手 → 📋 审核官(评分) → ✨ 润色官
```

通过 4 个条件路由函数实现：`entry_router`、`post_strategist_router`、`post_writer_router`、`post_critic_router`。

## AI 模型搭配

全局 4 个 provider，Settings 里每个智能体每个模式可自由切换。

| 智能体 | 投研默认 | 职责 |
|--------|---------|------|
| 🔭 侦察官 | Surf 1.5 | 搜索 leak.me 发现热门项目 |
| 🔬 策略官 | Surf 1.5 | 深度分析项目（融资/团队/代币） |
| 📋 审核官 | 豆包 | AI 数据清洗（去噪/去占位/去 URL） |
| ✍️ 写手 | DeepSeek V3.2 | 组装投研报告 |
| ✨ 润色官 | 豆包 | 润色定稿 |

## 新建文件

| 文件 | 职责 |
|------|------|
| `services/surf_service.py` | Surf AI API 服务封装 |
| `agents/research/__init__.py` | 投研模块入口 |
| `agents/research/scout.py` | 侦察官智能体 + 项目解析器 |
| `agents/critic/research_cleaner.py` | 投研清洗 Critic |
| `data/prompts/strategist/project_research.jinja2` | 策略官投研 prompt |
| `data/prompts/critic/project_research.jinja2` | 审核官清洗 prompt |

## 修改文件

| 文件 | 改动 |
|------|------|
| `graph.py` | +Scout 节点, +scout_projects 状态, +4 条件路由 |
| `strategist.py` | +project_research 分支 |
| `critic/__init__.py` | 投研映射 → research_cleaner |
| `core/llm.py` | +surf provider 配置 + generate_text 分支 |
| `frontend/schema.ts` | +PROVIDER_IDS.SURF, +AIProviderSchema, 投研默认改 Surf |
| `frontend/AgentModelConfig.tsx` | +Surf 模型列表 + 显示名 |
