# P19: 创作工坊 2.0 - TipTap 富文本编辑器

> **日期**: 2026-02-03  
> **状态**: ✅ **已完成** (2026-02-04)  
> **前置依赖**: P18 完成  
> **技术选型**: TipTap (MIT, ProseMirror-based)  
> **预估工时**: 9.5h | **实际工时**: ~8h

---

## 📋 核心目标

将创作工坊升级为**富文本编辑器**，支持：
1. 🔄 **生成态布局** - 流式内容输出，非空白等待
2. ✏️ **富文本编辑** - 格式化、段落结构
3. 🎯 **局部重写** - 选中段落 → AI 重写
4. 📊 **版本对比** - 多版本历史 + Diff 视图
5. 🧩 **统一侧边栏** - 整合悬浮面板

---

## 🏗️ 整体架构

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         创作工坊 2.0 架构                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│   ┌─────────────────────────────────────┐  ┌─────────────────────────┐     │
│   │         TipTap 编辑器 (960px)       │  │  统一侧边栏 (Tab)       │     │
│   │                                     │  │  [进度][版本][日志][导出]│     │
│   │  ┌─────────────────────────────┐    │  ├─────────────────────────┤     │
│   │  │ 工具栏                      │    │  │                         │     │
│   │  │ [B] [I] [H1] [H2] [🔄重写]  │    │  │  ✓ 策略分析             │     │
│   │  └─────────────────────────────┘    │  │  → 初稿撰写 v2          │     │
│   │                                     │  │  ○ 质量审核             │     │
│   │  ┌─────────────────────────────┐    │  │  ○ 润色打磨             │     │
│   │  │                             │    │  │                         │     │
│   │  │  [富文本内容区]             │    │  │  ─────────────────────  │     │
│   │  │                             │    │  │  📜 版本历史            │     │
│   │  │  选中文字后显示浮动菜单:    │    │  │  v2 82分 REFINE ●       │     │
│   │  │  [🔄 重写] [📝 扩展] [🗑️]   │    │  │  v1 59分 REWRITE        │     │
│   │  │                             │    │  │  [对比 v1↔v2]          │     │
│   │  └─────────────────────────────┘    │  └─────────────────────────┘     │
│   └─────────────────────────────────────┘                                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 分阶段实施

### Phase 1: 基础设施 ⏱️2.5h 🔴 高优先级

| # | 任务 | 工时 | 说明 |
|---|------|:----:|------|
| 1.1 | 安装 TipTap 依赖 | 15min | 见下方依赖清单 |
| 1.2 | 创建 `RichEditor.tsx` | 30min | 封装 TipTap，支持受控模式 |
| 1.3 | 集成到 StudioPage | 30min | 替换现有内容显示区 |
| 1.4 | 样式适配 | 30min | 与现有 UI 风格统一 |
| 1.5 | 流式内容注入 | 30min | SSE 内容实时写入 + 光标跟随 |
| 1.6 | 画布宽度扩展 | 15min | 720px → 960px |

**技术要点**:
- 流式注入需处理光标位置、选区保持
- 使用 `editor.commands.insertContent()` 追加内容

**交付物**: 基础富文本编辑器，支持流式内容显示

---

### Phase 2: 悬浮面板整合 ⏱️1h 🔴 高优先级

| # | 任务 | 工时 | 说明 |
|---|------|:----:|------|
| 2.1 | 创建 `UnifiedSidebar.tsx` | 20min | Tab 容器组件 |
| 2.2 | 迁移进度显示 | 15min | 从原 AgentTimeline 迁移 |
| 2.3 | 日志 Tab 优化 | 15min | 去技术化，友好格式 |
| 2.4 | 移除旧悬浮栏 | 10min | 删除/隐藏原组件 |

**Tab 结构**:
- `[进度]`: 智能体执行状态
- `[版本]`: 版本历史 (Phase 3 实现内容)
- `[日志]`: 执行日志 (用户友好格式)
- `[导出]`: MD/HTML 导出

**交付物**: 统一的右侧 Tab 面板

---

### Phase 3: 版本历史 + 对比 ⏱️2h 🟡 中优先级

| # | 任务 | 工时 | 说明 |
|---|------|:----:|------|
| 3.1 | 版本存储结构 | 30min | 扩展 `useAgentStore` |
| 3.2 | 版本列表 UI | 30min | 在 [版本] Tab 中显示 |
| 3.3 | 版本切换 | 30min | 点击版本 → 编辑器加载 |
| 3.4 | Diff 对比视图 | 30min | 使用 `diff` 库高亮差异 |

**数据结构**:
```typescript
interface DraftVersion {
  id: string;
  version: number;
  content: string;           // TipTap JSON 格式
  critique: {
    score: number;
    verdict: 'REWRITE' | 'REFINE' | 'PASS';
    suggestions: string[];
  } | null;
  timestamp: string;
  source: 'ai' | 'user';     // AI 生成 or 用户手动编辑
}

// Store 扩展
draftHistory: DraftVersion[];
currentVersionId: string | null;
```

**交付物**: 可点击查看历史版本，支持 v1↔v2 对比

---

### Phase 4: AI 局部重写 ⏱️3h 🔴 高优先级

| # | 任务 | 工时 | 说明 |
|---|------|:----:|------|
| 4.1 | 浮动菜单扩展 | 45min | 选中文字后显示 AI 操作菜单 |
| 4.2 | 后端 `/api/rewrite` API | 1h | 见下方 API 设计 |
| 4.3 | 前端调用集成 | 45min | 点击"重写" → 调用 API → 替换 |
| 4.4 | Loading + 错误处理 | 30min | 见下方错误处理设计 |

**API 设计**:
```typescript
// POST /api/rewrite (实际实现)
interface PartialRewriteRequest {
  selected_text: string;
  context: {
    before: string;      // 选中文字前 100 字
    after: string;       // 选中文字后 100 字
    mode: string;        // mid_article 等
    style: string;       // mimeng 等
  };
  action: 'rewrite' | 'expand' | 'simplify';
}

interface PartialRewriteResponse {
  result: string;
  suggestions?: string[];  // 可选：多个候选
}
```

**错误处理**:
```typescript
interface RewriteError {
  type: 'network' | 'timeout' | 'content_violation' | 'rate_limit';
  message: string;
  canRetry: boolean;
}

// UI 反馈策略
| 错误类型 | UI 反馈 |
|---------|--------|
| network | Toast "网络错误" + 重试按钮 |
| timeout | 显示"AI 正在思考..." + 继续等待 |
| content_violation | Toast + 显示原因 |
| rate_limit | Toast "请稍后重试" + 倒计时 |
```

**交付物**: 选中文字 → AI 重写/扩展/简化

---

### Phase 5: 体验优化 ⏱️1h 🟢 低优先级

| # | 任务 | 工时 | 说明 |
|---|------|:----:|------|
| 5.1 | 快捷键支持 | 20min | `Cmd+Shift+R` 重写选中 |
| 5.2 | 自动保存 | 20min | 每 30s 保存到 localStorage |
| 5.3 | 导出功能 | 10min | 导出 Markdown / HTML |
| 5.4 | 移动端适配 | 10min | 响应式布局检查 |

**交付物**: 快捷键、自动保存、导出

---

## 📦 依赖清单

```bash
# TipTap 核心
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit

# 扩展
npm install @tiptap/extension-placeholder     # 占位符
npm install @tiptap/extension-bubble-menu     # 浮动菜单
npm install @tiptap/extension-highlight       # 高亮 (Diff)

# Diff 对比
npm install diff                              # 文本对比算法
```

---

## 📂 文件结构

```
frontend/src/features/studio/
├── components/
│   ├── editor/
│   │   ├── RichEditor.tsx          # TipTap 封装组件 ✅
│   │   ├── EditorToolbar.tsx       # 工具栏 ✅
│   │   ├── EditorBubbleMenu.tsx    # AI 浮动菜单 ✅ (原名 AIBubbleMenu)
│   │   └── DiffViewer.tsx          # 版本对比视图 ✅
│   ├── sidebar/
│   │   ├── UnifiedSidebar.tsx      # 统一右侧面板
│   │   ├── ProgressTab.tsx         # 进度 Tab
│   │   ├── VersionTab.tsx          # 版本 Tab
│   │   ├── LogsTab.tsx             # 日志 Tab
│   │   └── ExportTab.tsx           # 导出 Tab
│   └── ...
├── extensions/                       # (未单独创建，逻辑集成在 EditorBubbleMenu)
└── stores/
    └── useEditorStore.ts           # 编辑器状态管理

backend/app/
├── api/rewrite.py                  # 新增 /api/rewrite API ✅
└── main.py                         # 注册 rewrite_router ✅
```

---

## ✅ 执行检查表

| Phase | 任务 | 工时 | 优先级 | 状态 |
|:-----:|------|:----:|:------:|:------:|
| **1** | 基础设施 (TipTap + 流式) | 2.5h | 🔴 高 | ✅ 完成 |
| **2** | 悬浮面板整合 | 1h | 🔴 高 | ✅ 完成 |
| **3** | 版本历史 + 对比 | 2h | 🟡 中 | ✅ 完成 |
| **4** | AI 局部重写 | 3h | 🔴 高 | ✅ 完成 |
| **5** | 体验优化 | 1h | 🟢 低 | ✅ 完成 |
| **总计** | | **9.5h** | | ✅ |

---

## 📋 验收标准

### Phase 1
- [x] TipTap 编辑器正常渲染
- [x] 支持基础格式化 (加粗、斜体、标题)
- [x] 流式内容实时注入，光标跟随
- [x] 画布宽度 960px

### Phase 2
- [x] 右侧面板统一为 Tab 切换
- [x] 旧悬浮栏已移除
- [x] 日志格式对用户友好

### Phase 3
- [x] 版本历史列表显示在 [版本] Tab
- [x] 点击版本可切换编辑器内容
- [x] 支持两版本 Diff 对比视图

### Phase 4
- [x] 选中文字后显示 AI 浮动菜单
- [x] 点击"重写"触发后端 API (`/api/rewrite`)
- [x] 重写结果替换选中内容
- [x] 错误时显示友好提示

### Phase 5
- [x] 快捷键 `Ctrl+S` 手动保存
- [x] 自动保存功能正常 (60s 间隔)
- [x] 导出 Markdown / HTML 功能正常
- [x] **视觉对齐**: HeroInput `variant="canvas"` 模式修复布局错位

---

## ⚠️ 风险与注意事项

1. **TipTap 流式更新**: 需要仔细处理光标位置，避免用户正在编辑时被打断
2. **版本存储**: 大量版本会占用 localStorage，考虑清理策略
3. **后端 API 安全**: `/partial-rewrite` 需要防止 Prompt Injection
4. **移动端**: TipTap 在移动端触摸选择可能有兼容问题

### 🚦 执行备忘录 (Pre-flight Check)
- **状态管理**: `WritingCanvas` 将从 Input/Display 模式切换为统一的 Editor 模式。建议生成开始后，Input 组件卸载，TipTap 挂载并接管内容显示。
- **React 19 兼容性**: 确保所有 TipTap 相关组件文件头部添加 `'use client'` 指令。
- **性能优化**: 流式内容注入建议使用 `requestAnimationFrame` 或 100ms 节流，避免高频渲染导致编辑器卡顿。
