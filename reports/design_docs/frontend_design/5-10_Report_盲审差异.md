# 📉 功能完整性盲审报告 (Content-Based Audit)

**审计对象**:
- **Truth (真理)**: `src/features/studio/schema.ts` (结合 `src/lib/styles.ts` 业务定义)
- **UI (现状)**: `src/features/studio/components/ConfigPanel.tsx`
- **审计时间**: 2026-01-20

---

## 1. ⚠️ Schema vs UI 差异 (Strict Audit)
*定义在 `schema.ts` 但 UI 中无控件的字段。*

| 缺失字段 | 数据类型 | 严重程度 | 建议控件 | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| **maxTokens** | `number` | 🟡 中 | Slider / Input | Schema 默认 4096，UI 无法调整。 |

> **注意**: `knowledgeSources`, `temperature` 此前已修复，目前 UI 中 **已存在** 对应控件。

---

## 2. 📉 业务逻辑断层 (Business Logic Gaps)
*定义在 `src/lib/styles.ts` (业务真理) 但 UI/Schema 未接入的字段。*

| 缺失业务逻辑 | 现状 | 真理 (The Truth) | 建议方案 |
| :--- | :--- | :--- | :--- |
| **Styles (人格)** | 仅 generic enum (`professional`...) | `mimeng`, `banfo`, `lianbushou` (8种) | **UI 全量补全**: 将 StyleChip 替换为富头像选择器。 |
| **Mixins (混合)** | 单选 | 支持 `{ style: string, weight: number }[]` | 暂缓，优先打通单选。 |

---

## 3. 🚨 用户期望缺失 (Expected Feature Gaps)
*用户提及但代码库 (Schema) 中完全不存在的字段。*

| 期望字段 | 现状 | 建议 |
| :--- | :--- | :--- |
| **top_p** | ❌ Schema/UI 均无 | 需先升级 Schema，再加 UI Slider。 |
| **output_format** | ❌ Schema/UI 均无 | 需先升级 Schema，再加 UI Select (Markdown/JSON)。 |

---

## 📊 审计结论

1.  **基础设施基本完备**: 核心的 Mode, Length, Temp, Knowledge 都已有控件。
2.  **内容严重断层**: UI 目前是 "Generic" 的，完全没有体现本项目特色的 "Mimeng/Web3" 风格库。这验证了 **70% 高级参数缺失** 的猜想（主要指业务风格参数）。
3.  **Schema 需升级**: 需扩充 `top_p` 等高级参数以满足 Power User 需求。

**下一步建议**: 执行 **Phase 5.7: 业务内容注入**，全量补全 UI。
