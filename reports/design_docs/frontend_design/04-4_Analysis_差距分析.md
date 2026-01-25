# 📉 Phase 5 差距分析与修复计划 (Gap Analysis & Fix Plan)

**审计对象**: Frontend v5.1 vs Schema v9.0 vs 业务需求
**审计时间**: 2026-01-20
**状态**: 🔴 严重 (Critical)

> **摘要**: 前端虽然实现了 "Vibe" 风格的 UI，但内在逻辑存在严重断层。70% 的配置项未传递给后端，且缺少关键的知识库与 API Key 管理入口。

---

## 1. ⚠️ 显性功能缺失 (Feature Gaps)
*用户界面上直接感知到的功能缺失。*

| 功能模块 | 缺失描述 | 严重程度 | 来源 |
| :--- | :--- | :--- | :--- |
| **Knowledge Brain** | **无入口**。后端支持知识库，但前端左侧栏无入口，用户无法选择知识库赛道。 | 🔴 阻塞 | 原 `差距分析报告.md` |
| **System Settings** | **无页面**。用户无法配置 LLM API Key 或选择模型。代码中 Key 为硬编码/环境变量，无法动态修改。 | 🔴 阻塞 | 原 `差距分析报告.md` |
| **Status Monitor** | **不完整**。只有单指示灯，无法区分 "风格库" 异常还是 "知识库" 异常 (双脑状态)。 | 🟡 中 | 原 `差距分析报告.md` |

---

## 2. 🔍 隐性逻辑断层 (Logic Gaps)
*UI 存在控件，但数据流在传输过程中丢失。*

**审计矩阵 (Schema vs UI vs Store)**

| 字段名 (Schema) | UI 控件 | 逻辑绑定 (Store/Action) | 诊断结论 |
| :--- | :--- | :--- | :--- |
| **style** | ✅ StyleChip | ❌ **完全丢失** | 点击 Start 时未传递。后端接收到的永远是默认值。 |
| **length** | ✅ Buttons | ❌ **完全丢失** | 点击 Start 时未传递。 |
| **temperature** | ✅ Slider | ❌ **完全丢失** | 点击 Start 时未传递。 |
| **mode** | ✅ SelectionCard | ⚠️ **部分丢失** | Store 使用了错误的类型定义，且混入了非 Schema 字段。 |
| **knowledge_ids** | ❌ **无控件** | ❌ **无法传递** | Schema 定义了字段，但前端无控件支持多选知识库。 |
| **prompt** | ✅ Textarea | ⚠️ **命名不匹** | UI 使用 `input`，Schema 定义为 `prompt`。需映射。 |

---

## 3. 📉 业务内容断层 (Business Content Gaps)
*UI 与 核心业务逻辑库 (`src/lib/styles.ts`) 的断连。*

**审计发现**: 
用户提到的 "Web2素材" (咪蒙/半佛) 和 "Web3素材" (媒体库) 实际上已在 `src/lib/styles.ts` 中定义，但在 Schema 和 UI 中 **完全未接入**。

| 业务需求 | 现状 (Schema/UI) | 目标 (lib/styles.ts) | 差距 |
| :--- | :--- | :--- | :--- |
| **Web2 风格库** | 仅支持 generic enum (`professional`, `casual`) | 定义了 8 种具体人格: `mimeng`(咪蒙), `banfo`(半佛), etc. | **人格缺失**。前端未提供这些高价值预设。 |
| **Web3 风格库** | 无 | 定义了 `lianbushou`(链捕手), `lingongzi`(临公子) | **行业深度缺失**。 |
| **风格混合 (Mix)** | 仅支持单选 Style | 支持权重混合: `[{id: "lianbushou", weight: 60}, {id: "mimeng", weight: 40}]` | **复杂逻辑丢失**。无法实现 "专业内容+情绪表达" 的组合。 |
| **叙事模板** | 仅 `mode` 字符串 | 定义了详细结构: `project_review` (背景/功能/分析/建议) | **结构化缺失**。无法引导后端按模板生成。 |
| **知识库 (Web3)** | 仅 Mock ID | 需对应后端 42 个赛道文件夹 (`data/Web3素材/`) | **数据源断层**。目前无法选择真实的 Web3 知识库。 |

---

## 4. 深度代码根因

### 3.1 Store 类型定义错误
文件 `src/features/agent/stores/useAgentStore.ts` 未引用 Schema，而是自定义了简略接口：

```typescript
// ❌ 现状
export interface GenerateRequest {
    input: string; // 应为 prompt
    mode: string;
    narrative_type: string; // Schema 中不存在
    // ⚠️ 缺失 style, length, temperature, config...
}
```

### 3.2 UI 事件绑定丢失
文件 `src/features/studio/components/ConfigPanel.tsx` 的 `StartButton` 组件虽然接收了 props，但调用时丢弃了数据：

```typescript
// ❌ 现状
startSession({
    input: input.trim(),
    mode, 
    narrative_type: 'project_review', 
    // ⚠️ style, length, temp 被丢弃
}); 
```

---

## 4. 🚑 修复行动计划 (Fix Plan)

建议将 **Phase 5** 延长，增加以下子步骤：

### Step 4: 逻辑缝合 (Logic Stitching)
- [ ] **Store 重构**: `useAgentStore` 直接引用 Schema 的 `GenerateRequest` 类型。
- [ ] **UI 修复**: `StartButton` 从 URL State (nuqs) 读取所有配置 (`style`, `length`, `temp`) 并完整传递。
- [ ] **API 修正**: 确保发往 `/generate` 的 Payload 符合 Zod Schema 校验。

### Step 5: 知识库入口 (Knowledge Entry)
- [ ] **Sidebar 更新**: 在左侧栏增加 "Knowledge" 菜单。
- [ ] **ConfigPanel 更新**: 新增 `KnowledgeSelector` (Multi-Select) 控件。

### Step 6: 设置页 (System Settings)
- [ ] **路由**: 创建 `/settings` 页面。
- [ ] **表单**: 实现 API Key 和 Model 配置表单 (Localstorage 持久化)。

### Step 7: 内容注入 (Content Injection) - **HIGH PRIORITY**
- [ ] **Schema 升级**: 同步 `lib/styles.ts` 中的 ID 到 `schema.ts`。
- [ ] **UI 升级**: `StyleSelector` 改为渲染 `CORE_STYLES` + `EXTENDED_STYLES`。
- [ ] **Store 适配**: 支持传递 `styles` 数组 (带权重) 而非单一 `string`。


---

**决策**: 立即执行 **Step 4: 逻辑缝合**，随后必须执行 **Step 7: 内容注入** 以满足业务需求。
