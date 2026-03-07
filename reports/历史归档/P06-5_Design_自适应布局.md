# 方案 A+: 自适应 Studio 布局设计

> 策略: Adaptive + Detail-on-Demand
> 演示 Demo: [10-2_Demo_滑出面板.html](./10-2_Demo_滑出面板.html)

---

## 📐 布局状态矩阵

| 用户状态 | 左侧 ConfigIsland | 中间 Canvas | 右侧 AgentIsland |
|----------|-------------------|-------------|------------------|
| **初始态 (Idle)** | 隐藏/图标栏 | Hero Input (居中大输入框) | 隐藏 |
| **思考态 (Thinking)** | 图标栏 (可展开) | 策略选择卡片 | 展开 (显示进度) |
| **生成/阅读态** | 图标栏 (可展开) | Tiptap 编辑器 | 紧凑模式 |

---

## 🔧 技术实现分解

### 模块 1: 状态驱动布局切换
**文件**: `StudioLayout.tsx`

```typescript
type StudioPhase = 'idle' | 'thinking' | 'generating' | 'reading';

function StudioLayout() {
    const { status } = useAgentStore();
    const phase = mapStatusToPhase(status);
    
    return (
        <div className={cn(
            "grid h-full transition-all duration-500",
            phase === 'idle' && "grid-cols-1",           // 单栏居中
            phase === 'thinking' && "grid-cols-[auto_1fr_280px]",
            phase === 'generating' && "grid-cols-[48px_1fr_200px]"
        )}>
            <ConfigIsland phase={phase} />
            <Canvas phase={phase} />
            <AgentIsland phase={phase} />
        </div>
    );
}
```

**工作量**: 4-6h

---

### 模块 2: 左侧图标栏模式
**文件**: `ConfigIsland.tsx`

```
极简模式 (48px):         展开模式 (320px):
┌────┐                   ┌──────────────────┐
│ ⚙️ │  ← 点击展开        │  创作配置         │
│ 📝 │                   │  ──────────       │
│ 🎨 │                   │  • 深度分析 ●     │
│ 📚 │                   │  • 快速摘要       │
└────┘                   │  ...              │
                         └──────────────────┘
```

**工作量**: 3-4h

---

### 模块 3: 右侧滑出面板 (内置标签)
**文件**: `AgentIsland.tsx`, `DetailPanel.tsx`

**触发方式**: 点击 Timeline 中的 "[查看思维链]" 或左侧图标

**面板结构**:
```
┌───────────────────────────────────────────┐
│  [🧠思维链] [📋历史] [🖼️配图] [📤导出] [X] │ ← 标签栏
├───────────────────────────────────────────┤
│                                           │
│  (根据选中标签显示不同内容)                │
│                                           │
│  Tab 1: DeepSeek R1 <think> 过程          │
│  Tab 2: 最近创作历史列表                  │
│  Tab 3: AI 配图生成 (占位符)              │
│  Tab 4: 导出选项 (Markdown/HTML/复制)      │
│                                           │
├───────────────────────────────────────────┤
│  [📝继续上次] [🔄重新生成]                │ ← 底部快捷区
└───────────────────────────────────────────┘
```

**交互效果**:
- 面板从右侧滑出 (400px)
- 中央画布自动压缩，**不遮挡**
- 面板内标签切换即时生效

**工作量**: 4-5h

---

### 模块 4: Hero Input 居中模式
**文件**: `HeroInput.tsx`

初始态时输入框居中显示，类似 ChatGPT/Claude 首页：

```
        ┌────────────────────────────────────┐
        │  输入您的研究主题或指令...           │
        │                                    │
        │  [深度分析 ▼]  [咪蒙体 ▼]           │ ← 快捷配置
        │                                    │
        │              [开始创作 ▶]           │
        └────────────────────────────────────┘
```

**工作量**: 2-3h

---

## ⚠️ 潜在隐患

| 隐患 | 等级 | 缓解措施 |
|------|------|----------|
| **状态切换卡顿** | 🟠 中 | 使用 CSS transition + will-change |
| **图标不直观** | 🟠 中 | 添加 Tooltip + 首次使用引导 |
| **配置项隐藏** | 🟡 低 | 保留"高级设置"展开按钮 |
| **移动端适配** | 🔴 高 | 暂不考虑，优先桌面端 |

---

## 📊 工作量汇总

| 模块 | 预估时间 | 依赖 |
|------|----------|------|
| 状态驱动布局 | 4-6h | useAgentStore |
| 左侧图标栏 | 3-4h | 无 |
| 右侧滑出 + 内置标签 | 4-5h | shadcn/Dialog |
| Hero Input 居中 | 2-3h | 无 |
| 动画优化 | 2-3h | Framer Motion (可选) |
| **总计** | **15-21h** | ~2-3 个工作日 |

---

## 🏗️ 实施阶段

### Day 1: 基础框架
- [ ] 实现 `StudioPhase` 状态逻辑
- [ ] 改造 `StudioLayout` 支持 grid 切换
- [ ] 左侧图标栏基础版

### Day 2: 面板实现
- [ ] 右侧滑出面板 `DetailPanel.tsx`
- [ ] 内置标签 (思维链/历史/配图/导出)
- [ ] Hero Input 居中模式

### Day 3: 打磨验收
- [ ] 过渡动画优化
- [ ] Tooltip / 引导
- [ ] 测试验收

---

## 📁 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `StudioLayout.tsx` | **重构** | 状态驱动 grid 布局 |
| `ConfigIsland.tsx` | **重构** | 支持图标栏/完整模式 |
| `AgentIsland.tsx` | **修改** | 精简 Timeline |
| `HeroInput.tsx` | **修改** | 居中模式 + 快捷配置 |
| **[NEW]** `DetailPanel.tsx` | **新增** | 右侧滑出面板 + 内置标签 |
| **[NEW]** `HistoryTab.tsx` | **新增** | 历史记录标签内容 |
| **[NEW]** `ExportTab.tsx` | **新增** | 导出标签内容 |
