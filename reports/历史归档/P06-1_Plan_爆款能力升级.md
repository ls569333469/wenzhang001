# Phase 10: 爆款内容生成器升级计划

> 目标：补足"爆款"核心能力，提升内容传播力与用户体验

---

## 🎯 核心目标

将量子工坊从"能生成文章"升级为"能生成爆款文章"的智能创作平台。

---

## 📋 功能清单

### P10-1: 标题AB测试模块 ⏳
**优先级**: 🔴 高 | **预估工时**: 4-6h

**功能描述**:
- 生成 3-5 个备选标题供用户选择
- 显示每个标题的"爆款公式"分析
- 支持用户手动编辑/微调标题

**实现要点**:
1. 后端：新增 `/generate-titles` API，输入主题返回多个标题选项
2. 前端：策略选择阶段后增加"标题选择"面板
3. 每个标题附带分析标签（情绪触发、悬念感、数字增益等）

---

### P10-2: 爆款要素评分显性化 ⏳
**优先级**: 🔴 高 | **预估工时**: 4-6h

**功能描述**:
- 在策略选择时显示"传播力指数"
- 标注情绪触发点、痛点强度、受众匹配度
- 可视化评分展示（雷达图/进度条）

**实现要点**:
1. 后端：`/analyze` 返回中增加 `viral_score` 字段
2. 前端：StrategySelector 卡片上显示评分指标
3. 评分维度：情绪共鸣、信息密度、行动召唤、社交货币

---

### P10-3: 开头Hook强度设置 ⏳
**优先级**: 🔴 高 | **预估工时**: 2-3h

**功能描述**:
- ConfigPanel 添加"开头吸引力"强度滑块
- 可选：温和开头 / 标准开头 / 强力Hook / 爆款开场

**实现要点**:
1. 前端：ConfigPanel 添加滑块组件
2. 后端：prompt 根据 hook_intensity 参数调整生成策略

---

### P10-4: 智能体流程详细显示 ⏳
**优先级**: 🟠 中 | **预估工时**: 2-3h

**功能描述**:
- AgentTimeline 显示更详细的执行过程
- 实时展示子步骤（如：正在分析关键词...、正在构建大纲...）
- 显示每个 Agent 的思考过程摘要

**实现要点**:
1. 后端：SSE 流增加更细粒度的 agent_update 事件
2. 前端：AgentTimeline 支持展开查看详细日志
3. 添加可折叠的"思考过程"区域

---

### P10-5: 导出功能 ⏳
**优先级**: 🟠 中 | **预估工时**: 1-2h

**功能描述**:
- WritingCanvas 添加导出按钮
- 支持导出为 Markdown / HTML / 纯文本

---

### P10-6: Prompt 精调 ⏳
**优先级**: 🟠 中 | **预估工时**: 2-4h

**功能描述**:
- 优化 Strategist/Writer/Critic 的 prompt
- 注入更多爆款写作技巧
- 改进中文表达的流畅度

---

## 📊 进度跟踪

| 编号 | 功能 | 状态 | 完成日期 |
|------|------|------|----------|
| P10-1 | 标题AB测试模块 | ⏳ 待开始 | - |
| P10-2 | 爆款要素评分 | ⏳ 待开始 | - |
| P10-3 | 开头Hook设置 | ⏳ 待开始 | - |
| P10-4 | 智能体流程详细显示 | ⏳ 待开始 | - |
| P10-5 | 导出功能 | ⏳ 待开始 | - |
| P10-6 | Prompt 精调 | ⏳ 待开始 | - |
| **P10-7** | **风格管理系统** | ⏳ 待开始 | - |
| **P10-8** | **Web3 创作模式** | ⏳ 待开始 | - |
| **P10-9** | **自适应布局 (A+)** | 🔵 设计完成 | - |

---

## 🎨 P10-7: 风格管理系统

### 当前问题

| 风格 | 素材状态 | 说明 |
|------|----------|------|
| 咪蒙体 | ✅ 已清洗 | Lark 已有数据 |
| 半佛体 | ⏳ 待清洗 | 素材已收集 |
| 新世相体 | ❌ 未确定 | 博主来源待定 |
| 视觉志体 | ❌ 未确定 | 博主来源待定 |
| 链捕手体 | ❌ 未确定 | 博主来源待定 |
| 临公子体 | ❌ 未确定 | 博主来源待定 |
| 风茕子体 | ❌ 未确定 | 博主来源待定 |
| 程十安体 | ❌ 未确定 | 博主来源待定 |

### 设计方案

#### 方案 A: 后端驱动风格配置

```
风格定义从后端 API 获取，前端动态渲染
```

**数据流**:
1. 后端 `/config/styles` 返回可用风格列表
2. 每个风格包含 `status`: `ready` | `coming_soon` | `disabled`
3. 前端根据 status 显示不同 UI 状态

**优点**:
- 新增/删除风格无需改前端代码
- 可动态管理素材博主来源
- 支持 A/B 测试不同风格

**API 设计**:
```typescript
GET /config/styles
Response: {
  styles: [
    {
      id: "mimeng",
      name: "咪蒙体",
      icon: "🔥",
      color: "#ef4444",
      status: "ready",           // ready | coming_soon | disabled
      source: "咪蒙公众号",       // 素材来源
      sampleCount: 156,          // 已清洗素材数量
      description: "情绪爆点"
    },
    ...
  ]
}
```

#### 方案 B: 配置文件驱动 (推荐)

将风格配置从代码移至 `config/styles.json`，支持热更新：

```json
{
  "styles": [
    {
      "id": "mimeng",
      "name": "咪蒙体",
      "icon": "🔥",
      "status": "ready",
      "source": "咪蒙公众号",
      "larkTableId": "tblXXXXX"
    },
    {
      "id": "banfo", 
      "name": "半佛体",
      "status": "coming_soon",
      "source": "待定"
    }
  ]
}
```

**前端 UI 变化**:
- `status: ready` → 正常可选
- `status: coming_soon` → 灰色 + "即将推出" 标签
- `status: disabled` → 隐藏

---

## 📝 P10-8: Web3 创作模式优化

### 当前模式分析

| 模式 | 适用场景 | 问题 |
|------|----------|------|
| 深度分析 | 研报、项目评测 | ✅ 合适 |
| 快速摘要 | 早报、简讯 | ✅ 合适 |
| 改写润色 | 翻译稿润色 | 🟡 场景单一 |
| 专业翻译 | 英文研报翻译 | 🟡 场景单一 |

### Web3 博主实际需求

通过分析 Web3 内容创作者的工作流，建议新增以下模式：

| 新模式 | 场景描述 | 输出特点 |
|--------|----------|----------|
| **🔥 热点追踪** | 某项目出大新闻，快速产出观点文 | 快速（15min）、有观点、结合最新数据 |
| **📊 项目评测** | 新项目研究、投资分析 | 深度、结构化、有评分/建议 |
| **🧵 Twitter 线程** | 把长文拆成推特线程 | 10-15 条、每条有 Hook、适合传播 |
| **📰 周报汇总** | 整合一周行业动态 | 结构化、分板块、数据驱动 |
| **💡 观点评论** | 对某事件发表看法 | 短小精悍、有立场、有论据 |

### 实现建议

更新 `config/constants.ts` 中的 `CREATION_MODES`:

```typescript
export const CREATION_MODES = [
  // === 核心模式 ===
  {
    id: 'hot_take',
    title: '🔥 热点追踪',
    desc: '快速出稿，紧跟热点',
    category: 'core'
  },
  {
    id: 'project_review',
    title: '📊 项目评测',
    desc: '深度分析，投资研判',
    category: 'core'
  },
  {
    id: 'weekly_digest',
    title: '📰 周报汇总',
    desc: '整合动态，结构清晰',
    category: 'core'
  },
  
  // === 格式转换 ===
  {
    id: 'twitter_thread',
    title: '🧵 推特线程',
    desc: '拆分为 10-15 条推文',
    category: 'format',
    compact: true
  },
  {
    id: 'rewrite',
    title: '✍️ 改写润色',
    category: 'format',
    compact: true
  },
  {
    id: 'translate',
    title: '🌐 专业翻译',
    category: 'format',
    compact: true
  }
];
```

---

## 🏗️ P10-9: 自适应布局 (方案 A+)

> 策略: Adaptive + Detail-on-Demand
> 设计文档: [10-2_Design_自适应布局.md](./10-2_Design_自适应布局.md)
> 演示 Demo: [10-2_Demo_滑出面板.html](./10-2_Demo_滑出面板.html)

### 核心设计

**状态驱动布局切换**:

| 用户状态 | 左侧 ConfigIsland | 中间 Canvas | 右侧 AgentIsland |
|----------|-------------------|-------------|------------------|
| 初始态 (Idle) | 隐藏/图标栏 | Hero Input (居中) | 隐藏 |
| 思考态 (Thinking) | 图标栏 | 策略选择卡片 | 展开 (显示进度) |
| 生成/阅读态 | 图标栏 | Tiptap 编辑器 | 紧凑模式 |

### 右侧滑出面板 (内置标签)

点击触发后，面板从右侧滑出，内部包含多个标签：

| 标签 | 功能 |
|------|------|
| 🧠 思维链 | 展示 DeepSeek R1 `<think>` 过程 |
| 📋 历史 | 最近创作记录，可快速加载 |
| 🖼️ 配图 | AI 配图生成 (未来功能) |
| 📤 导出 | Markdown / HTML / 复制 |

### 工作量估算

| 模块 | 预估时间 | 依赖 |
|------|----------|------|
| 状态驱动布局 | 4-6h | useAgentStore |
| 左侧图标栏 | 3-4h | 无 |
| 右侧滑出 + 内置标签 | 4-5h | shadcn/Dialog |
| Hero Input 居中 | 2-3h | 无 |
| 动画优化 | 2-3h | Framer Motion (可选) |
| **总计** | **15-21h** | ~2-3 天 |

### 实施阶段

| 阶段 | 内容 | 交付物 |
|------|------|--------|
| **Day 1** | 状态切换 + 左侧图标栏 | 基础自适应框架 |
| **Day 2** | 右侧滑出 + 内置标签 | 完整面板功能 |
| **Day 3** | 动画 + 打磨 + 测试 | 最终版本 |

### 文件变更清单

| 文件 | 变更类型 |
|------|----------|
| `StudioLayout.tsx` | **重构** - 状态驱动 grid |
| `ConfigIsland.tsx` | **重构** - 图标栏/展开模式 |
| `AgentIsland.tsx` | **修改** - 精简显示 |
| `HeroInput.tsx` | **修改** - 居中模式 |
| **[NEW]** `DetailPanel.tsx` | **新增** - 滑出面板 |
| **[NEW]** `HistoryTab.tsx` | **新增** - 历史标签 |

---

## 🔗 相关文件

- `PROJECT_HANDBOOK.md` - 项目全局规划
- `frontend/src/features/studio/components/timeline/AgentTimeline.tsx` - 智能体流程组件
- `frontend/src/features/studio/components/StrategySelector.tsx` - 策略选择组件
- `frontend/src/features/studio/layout/StudioLayout.tsx` - 布局组件
- `backend/app/main.py` - SSE 流处理

