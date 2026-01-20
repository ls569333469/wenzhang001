# 📉 前端功能缺失分析报告 (Gap Analysis) - v5.1 修正版

> **检查范围**: 仅限 `Quantum Studio v5.1` (UCB 升级) 明确需求。
> **过滤**: 已移除所有 "未来概念" (Generative UI, Cmd+K) 等非必需项。

## ⚠️ 核心缺失 (Critical Gaps)

以下 3 项是 v5.1 升级**必须填补**的空白，否则双脑架构无法运作。

### 1. 缺失 "Knowledge Brain" 入口 (左脑) 🔴
*   **需求来源**: `Quantum_Studio_v5.1_UCB_升级方案.md` (Sec 3.2 Knowledge_Repo)
*   **问题**: 后端能够处理知识库数据，但前端**没有任何按钮**让用户启用或选择知识库赛道。
*   **后果**: 用户只能生成"有风格没内容"的文章。
*   **修复目标**: 在 `/studio` 左侧栏增加 `KnowledgeSelector` (赛道 + 时效)。

### 2. 缺失 "System Settings" 页面 (配置) 🔴
*   **需求来源**: `Quantum_Studio_v5.0_Core_Workflow_Guide.md`
*   **问题**: 用户无法在界面上输入 LLM API Key，也无法配置模型。代码中写死的逻辑在新环境下无法工作。
*   **后果**: 新环境部署后，系统因缺 Key 而完全不可用。
*   **修复目标**: 新增 `/settings` 页面，提供 Key 管理表单。

### 3. 状态监控不完整 (Status) 🟡
*   **需求来源**: `Quantum_Studio_v5.1_UCB_升级方案.md` (Sec 2.1 双脑架构)
*   **问题**: 只有一个同步指示灯，无法区分"风格库"坏了还是"知识库"坏了。
*   **修复目标**: 升级为双状态指示灯 (Dual Status)。

### 4. 缺失 "Story Length Control" (字数控制) 🔵
*   **需求来源**: 用户新增需求。
*   **问题**: 用户无法指定生成文章的篇幅偏好 (短篇/中篇/长篇)。
*   **修复目标**:
    *   **前端**: 在 Narrative Control 区域增加 `LengthSelector`。
    *   **后端**: 在 `GenerateRequest` 中增加 `length` 字段，并在 Strategist/Writer 的 Prompt 中注入此约束。

---

## ✅ 已就绪功能 (Ready)
*   [x] **Abort 中断**: (Phase 1.1) 已实现。
*   [x] **Style 风格选择**: 已实现。
*   [x] **Markdown 渲染**: 已实现。
*   [x] **手动同步**: 已实现。

## 📅 下一步行动 (Action Plan)
确认以上 3 点为本次 **MPA 重构** 的唯一功能目标。
1.  搭建 MPA 框架 (`/dashboard`, `/studio`, `/settings`)。
2.  优先开发 `/settings` (解决 Key 问题)。
3.  开发 `/studio` 的 `KnowledgeSelector` (解决左脑问题)。
