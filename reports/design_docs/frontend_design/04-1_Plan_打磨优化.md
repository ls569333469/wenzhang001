# Phase 5: 打磨优化实施计划

> **版本**: v2.0  
> **状态**: 📋 待执行  
> **前置条件**: Phase 4 验收通过

---

## 📋 执行概览

| 步骤 | 名称 | 核心目标 | 预估工时 |
|------|------|----------|----------|
| Step 1 | 环境修复 | 解决 `ERR_CONNECTION_REFUSED` | 1h |
| Step 2 | 功能增强 | 富文本渲染 + UI 改进 | 2-3h |
| Step 3 | 清理对齐 | 视觉统一 + 代码清理 | 1-2h |

---

## 🔧 Step 1: 环境修复与后端连接 (Fix Environment)

> **目标**: 解决 `ERR_CONNECTION_REFUSED` 错误，实现环境变量化配置

### 1.1 环境变量配置

| 任务 | 文件 | 内容 |
|------|------|------|
| 创建环境文件 | `frontend/.env.local` | `NEXT_PUBLIC_API_URL=http://localhost:8002` |

### 1.2 API 改造

| 任务 | 文件 | 修改内容 |
|------|------|----------|
| 移除硬编码 | `src/config/api.ts` | `process.env.NEXT_PUBLIC_API_URL \|\| 'http://localhost:8002'` |

### 1.3 类型安全修复

| 文件 | 需修复项 |
|------|----------|
| `ConfigPanel.tsx` | `Label`, `SelectionCard`, `StyleChip`, `StartButton` 的 `any` 类型 |
| `useAgentStore.ts` | `handleEvent` 函数参数、`catch (err: any)` |

### 验收标准
- [ ] `.env.local` 已创建
- [ ] API 地址可通过环境变量配置
- [ ] 无 `any` 类型警告

---

## ✨ Step 2: 功能增强与内容渲染 (Enhance Features)

> **目标**: 从"纯文本"升级为"富文本"，改进 UI 交互

### 2.1 Markdown 渲染

| 任务 | 说明 |
|------|------|
| 安装依赖 | `npm install react-markdown rehype-highlight` |
| 组件替换 | 用 `<ReactMarkdown>` 替换纯文本显示 |
| 代码高亮 | 添加 Github 风格高亮样式 |

### 2.2 渐进式披露 (Progressive Disclosure)

改造 `ConfigPanel.tsx`：

```
📦 Basic Settings (默认展开)
├── Creation Mode
├── Writing Style
└── Article Length

📦 Advanced Settings (默认折叠)
├── Temperature
├── Top-P
└── 其他高级参数
```

**实现方式**: 使用 Shadcn `Accordion` 组件

### 2.3 交互反馈

| 场景 | 处理方式 |
|------|----------|
| 后端连接失败 | Shadcn `Toast` 显示友好提示 |
| 生成超时 | Toast 提示 + 重试按钮 |

### 验收标准
- [ ] Markdown 内容正确渲染
- [ ] 代码块有语法高亮
- [ ] ConfigPanel 使用 Accordion 分组
- [ ] 错误时显示 Toast 提示

---

## 🧹 Step 3: 清理与视觉对齐 (Cleanup)

> **目标**: 美学统一，清理遗留代码

### 3.1 圆角统一

| 检查项 | 操作 |
|--------|------|
| `rounded-md` | → `rounded-xl` |
| `rounded-sm` | → `rounded-xl` (极小标签除外) |
| Shadcn 组件 | 在 `tailwind.config.ts` 覆盖默认值 |

### 3.2 遗留清理

| 路径 | 操作 |
|------|------|
| `src/features/workbench/` | 检查是否废弃，如是则移至 `_deprecated/` |
| `globals.css` | 确保无残留非 Tailwind 样式 |

### 3.3 文档更新

| 文件 | 操作 |
|------|------|
| `01_重构总计划.md` | 勾选 Phase 5 已完成项 |
| `PROJECT_HANDBOOK.md` | 添加 Phase 5 交付记录 |

### 验收标准
- [ ] 无 `rounded-md/sm` (极小标签除外)
- [ ] 遗留代码已清理或归档
- [ ] 文档已更新

---

## 📝 执行 Prompt

### Prompt 1: Step 1 环境修复
```
请读取 P5_打磨优化_计划.md 和 P5_打磨优化_任务.md。
执行 Step 1：环境修复与后端连接。
完成后提示我启动后端验证。
```

### Prompt 2: Step 2 功能增强
```
环境修复完成。执行 Step 2：功能增强。
安装 react-markdown，改造 ConfigPanel 使用 Accordion，添加 Toast 错误提示。
```

### Prompt 3: Step 3 清理对齐
```
功能已就绪。执行 Step 3：清理与对齐。
统一圆角，清理遗留代码，更新文档。
```

---

## ⏱️ 总预估工时

| 阶段 | 工时 |
|------|------|
| Step 1: 环境修复 | 1h |
| Step 2: 功能增强 | 2-3h |
| Step 3: 清理对齐 | 1-2h |
| **合计** | **4-6h** |
