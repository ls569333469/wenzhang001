## 🚨 Step 4: 逻辑缝合 (Logic Stitching) - HIGH PRIORITY

### Store 重构 (`useAgentStore.ts`)
- [ ] 引入 `GenerateRequestSchema` from `schema.ts`
- [ ] 移除本地定义的 `GenerateRequest` interface
- [ ] 更新 `startSession` 签名以接受完整 Config
- [ ] 构造符合 Schema 的 API Payload

### UI 修复 (`ConfigPanel.tsx`)
- [ ] 确保 `StartButton` 获取所有 local/url state
- [ ] 构造完整的 `CreationConfig` 对象并传递给 Store
- [ ] 验证：Network Tab 中 payload 包含 `style`, `length`, `temperature`

## 🧠 Step 5: 知识库 (Knowledge Brain)

- [ ] **ConfigPanel**: 创建 `KnowledgeSelector` 组件 (Multi-command style)
- [ ] **Sidebar**: 增加 `Knowledge` 导航项
- [ ] **Store**: 更新 payload 包含 `knowledgeSources`

## ⚙️ Step 6: 系统设置 (Settings)

- [ ] 创建 `features/settings/components/SettingsForm.tsx`
- [ ] 创建 `app/(main)/settings/page.tsx`
- [ ] 实现 LocalStorage 持久化 (API Key, Model)
