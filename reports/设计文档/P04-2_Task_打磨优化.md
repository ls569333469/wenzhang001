# Phase 5: 打磨优化任务清单

> **状态**: 📋 待执行  
> **版本**: v2.0

---

## ✅ 已完成

- [x] AI 静态代码审计 → `PHASE5_AUDIT_REPORT.md`
- [x] Console 错误分析
- [x] 创建实施计划 `P5_打磨优化_计划.md`

---

## 🔧 Step 1: 环境修复与后端连接

### 环境配置
- [x] 创建 `frontend/.env.local`
- [x] 写入 `NEXT_PUBLIC_API_URL=http://localhost:8002`

### API 改造
- [x] 修改 `src/config/api.ts`
- [x] 使用 `process.env.NEXT_PUBLIC_API_URL` 替换硬编码

### 类型安全
- [x] 修复 `ConfigPanel.tsx` 中的 `any` 类型
  - [x] `Label` 组件
  - [x] `SelectionCard` 组件
  - [x] `StyleChip` 组件
  - [x] `StartButton` 组件
- [x] 修复 `useAgentStore.ts` 中的 `any` 类型
  - [x] `handleEvent` 函数参数
  - [x] `catch (err: any)`

### 验收
- [ ] 启动后端，确认无 `ERR_CONNECTION_REFUSED`

---

### Markdown 渲染
- [x] 安装 `react-markdown` + `rehype-highlight`
- [x] 修改画布组件使用 `<ReactMarkdown>`
- [x] 添加代码高亮样式 (Github 风格)

### 渐进式披露 (ConfigPanel)
- [x] 安装/确认 Shadcn Accordion
- [x] 创建 "Basic Settings" 分组 (默认展开)
- [x] 创建 "Advanced Settings" 分组 (默认折叠)

### 交互反馈
- [x] 连接失败时显示 Toast 提示
- [x] 超时时显示重试按钮

---

## 🧹 Step 3: 清理与对齐

### 圆角统一
- [x] 扫描并替换 `rounded-md` → `rounded-xl`
- [x] 扫描并替换 `rounded-sm` → `rounded-xl`
- [x] 更新 Shadcn 组件默认圆角

### 遗留清理
- [x] 检查 `features/workbench/` 是否废弃
- [x] 如废弃，移至 `_deprecated/` 目录 (Deleted)
- [x] 检查 `globals.css` 无残留样式

### 文档更新
- [x] 更新 `01_重构总计划.md` Phase 5 状态
- [x] 更新 `PROJECT_HANDBOOK.md` 添加交付记录

---

## 📝 执行 Prompt

**Step 1**: 
```
执行 P5 Step 1：环境修复与后端连接
```

**Step 2**: 
```
执行 P5 Step 2：功能增强
```

**Step 3**: 
```
执行 P5 Step 3：清理与对齐
```
