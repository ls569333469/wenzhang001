# Phase 9: 全链路验证与页面完善计划 (Full Chain & Page Completion)

> **版本**: v1.0
> **日期**: 2026-01-20
> **状态**: 📋 规划中
> **目标**: 彻底解决前端重构过程中的遗留问题，确保所有页面功能完整

---

## 1. 问题诊断 (Issue Diagnosis)

### 1.0 代码验证结果 (Code Validation - 2026-01-20 23:30)
| 检查项 | 实际状态 | 问题详情 |
|--------|----------|----------|
| `confirmStrategy` | ❌ **空实现** | 第 145-171 行 try 块为空，无实际 `/generate` 调用 |
| 测试框架 (Vitest) | ❌ **未安装** | `package.json` 无 vitest 依赖 |
| 测试框架 (Playwright) | ❌ **未安装** | 仅有 Next.js 内置 testmode，无独立 Playwright |
| 现有测试文件 | ❌ **无** | `src/` 目录下无任何 `.test.ts` 文件 |
| 后端接口 | ✅ | `/analyze`, `/generate`, `/health` 均存在 |

### 1.1 页面完成度审计
| 页面 | 路由 | 当前状态 | 问题 |
|------|------|----------|------|
| **Dashboard** | `/dashboard` | ⚠️ 部分完成 | MonitorCard 显示 Offline，未实际连接后端 |
| **Studio** | `/studio` | ✅ 核心完成 | 两阶段流已实现，但 `confirmStrategy` 未完整实现 |
| **Knowledge** | `/knowledge` | ❌ 占位符 | 仅显示"施工中"，无实际功能 |
| **Agents** | `/agents` | ❌ 占位符 | 仅显示"施工中"，无实际功能 |
| **Settings** | `/settings` | ⚠️ 部分完成 | UI 存在，但 API Key 未与后端同步 |

### 1.2 链路问题诊断
| 链路 | 状态 | 问题描述 |
|------|------|----------|
| **Frontend → Backend** | ⚠️ | `confirmStrategy` 未完整实现，无法触发 `/generate` |
| **Backend → Lark** | ✅ | 验证通过 (Phase 7) |
| **Settings → Backend** | ❌ | 前端 Settings 仅存 localStorage，未同步后端 |
| **Dashboard → Health** | ❌ | MonitorCard 未实际调用 `/health` 接口 |

---

## 2. 实施计划 (Implementation Plan)

### 🔴 P0: 链路修复 (Critical Path Fix)

#### 2.1 修复 `confirmStrategy` (Studio 核心链路)
- **文件**: `useAgentStore.ts`
- **问题**: `confirmStrategy` 逻辑不完整，缺少对 `/generate` 的实际调用
- **方案**:
  1. 在 Store 中保存 `lastRequestPayload` (input + config)
  2. `confirmStrategy` 时重建 payload 并附加 `selected_option`
  3. 调用 `/generate` 并处理 SSE 流

#### 2.2 修复 Dashboard MonitorCard
- **文件**: `MonitorCard.tsx`, `dashboard/page.tsx`
- **问题**: 静态显示 online/offline，无实际后端调用
- **方案**:
  1. 添加 `useEffect` 调用 `/health` 接口
  2. 根据响应动态更新状态

---

### 🟡 P1: 页面补全 (Page Completion)

#### 2.3 Knowledge 页面 MVP
- **目标**: 展示 Lark 知识库的素材列表
- **功能**:
  - 调用后端 `/config/knowledge` 获取素材列表
  - 显示素材标题、类型、创建时间
  - 支持搜索/筛选

#### 2.4 Agents 页面 MVP
- **目标**: 展示智能体团队及其配置状态
- **功能**:
  - 显示 4 个 Agent (Strategist, Writer, Critic, Polisher)
  - 展示每个 Agent 的当前模型配置
  - 链接至 Settings 进行配置修改

#### 2.5 Settings 后端同步
- **问题**: 当前仅存 localStorage
- **方案**: 调用后端 `/config/keys` 进行读写

---

### 🟢 P2: DOM 测试与 UX 验证

#### 2.6 全链路 E2E 测试
使用 Browser Subagent 进行真实 DOM 交互测试：
1. **场景 1**: Dashboard → Studio → 输入 → 分析 → 选择策略 → 生成
2. **场景 2**: Settings 保存 → 验证 localStorage 更新
3. **场景 3**: 页面导航流畅性测试

#### 2.7 视觉回归检查
- 检查所有页面的 Zinc 色系一致性
- 检查 Island 阴影/圆角规范
- 检查响应式布局 (移动端适配)

---

### 🔵 P3: 前端测试体系建设 (Frontend Testing Framework)

#### 3.0 依赖安装 (Prerequisites)
```bash
# 安装 Vitest + React Testing Library
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom

# 安装 Playwright
npm install -D @playwright/test
npx playwright install

# 安装 Lighthouse CLI
npm install -D lighthouse
```

#### 3.1 单元测试 (Unit Testing)
- **工具**: Vitest (与 Vite/Next.js 生态兼容)
- **范围**:
  - 工具函数 (`lib/utils.ts`)
  - Schema 验证 (`schema.ts`)
  - Store 逻辑 (`useAgentStore.ts` 的纯函数部分)
- **目标**: 覆盖率 ≥ 60%

#### 3.2 组件测试 (Component Testing)
- **工具**: React Testing Library + Vitest
- **范围**:
  - `ContextPanel`: 验证 `info_anchors` 正确渲染
  - `StrategySelector`: 验证点击触发 `confirmStrategy`
  - `AgentTimeline`: 验证状态变化 (idle → thinking → completed)
- **目标**: 核心组件 100% 覆盖

#### 3.3 端到端测试 (E2E Testing)
- **工具**: Playwright (速度快，支持多浏览器)
- **场景**:
  1. **完整创作流程**: Dashboard → Studio → 输入 → 分析 → 选策略 → 生成
  2. **设置保存**: Settings 页面保存 → 验证 localStorage
  3. **导航测试**: 所有页面可达性
- **目标**: 核心用户路径 100% 覆盖

#### 3.4 视觉回归测试 (Visual Regression)
- **工具**: Playwright + Percy 或 BackstopJS
- **范围**:
  - 关键页面截图对比 (Dashboard, Studio, Settings)
  - 响应式布局 (Desktop 1920px, Tablet 768px, Mobile 375px)
- **目标**: 零视觉回归

#### 3.5 性能与兼容性测试
- **工具**: Lighthouse CLI
- **指标**:
  | 指标 | 目标 |
  |------|------|
  | LCP (Largest Contentful Paint) | < 2.5s |
  | FCP (First Contentful Paint) | < 1.8s |
  | CLS (Cumulative Layout Shift) | < 0.1 |
  | Accessibility Score | ≥ 90 |
- **浏览器**: Chrome, Firefox, Safari

---

## 3. 执行顺序 (Execution Order)

```
P0-1: 修复 confirmStrategy (链路核心)
P0-2: 修复 Dashboard MonitorCard (健康检查)
  ↓
P1-1: Settings 后端同步 (基础设施)
P1-2: Knowledge 页面 MVP
P1-3: Agents 页面 MVP
  ↓
P2-1: 全链路 E2E 测试 (Browser Subagent)
P2-2: 视觉回归检查
  ↓
P3-1: 测试框架搭建 (Vitest + Playwright)
P3-2: 单元测试编写
P3-3: 组件测试编写
P3-4: E2E 自动化测试
P3-5: 性能测试报告
```

---

## 4. 验收标准 (Acceptance Criteria)

| 检查项 | 预期结果 |
|--------|----------|
| **全链路** | 用户完成 Studio 完整流程 (输入 → 分析 → 选策略 → 生成) |
| **Dashboard** | MonitorCard 实时显示后端状态 |
| **Knowledge** | 显示至少 10 条 Lark 素材 |
| **Agents** | 显示 4 个 Agent 及其模型配置 |
| **Settings** | 保存后能通过 `/config/keys` 验证 |
| **单元测试** | 覆盖率 ≥ 60% |
| **组件测试** | 核心组件 100% 覆盖 |
| **E2E 测试** | 核心流程自动化通过 |
| **Lighthouse** | 性能分数 ≥ 85 |

---

## 5. 预估工时 (Estimated Effort)

| 任务 | 预估时间 |
|------|----------|
| P0: 链路修复 | 2h |
| P1: 页面补全 | 3h |
| P2: DOM 测试 | 1h |
| P3: 测试体系建设 | 4h |
| **总计** | **10h** |
