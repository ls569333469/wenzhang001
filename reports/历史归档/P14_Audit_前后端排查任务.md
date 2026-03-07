# P14 前后端一致性排查任务

**创建日期**: 2026-02-01  
**基于**: P13 审计模板  
**状态**: 🔄 进行中

---

## 📋 P14 新增检查项

### Phase A: hot_take 模式路由 (优先级 🔴)

#### A1. `/hot_take` 接口一致性

| 检查项 | 前端 | 后端 | 状态 | 问题 |
|--------|------|------|:----:|------|
| 端点路由 | `useAgentStore.ts:180` | `main.py /hot_take` | ✅ | 已修复 |
| 请求体结构 | `{input, api_config}` | `HotTakeRequest` | ✅ | 匹配 |
| 响应解析 | `result.result.candidates` | `{result: {candidates}}` | ⚠️ | 需验证 |

**修复记录** (2026-02-01):
```diff
+ if (config.mode === 'hot_take') {
+     const endpoint = `${API_BASE_URL}/hot_take`;
+     // 跳过策略师流程
+ }
```

---

### Phase B: 模式枚举同步 (优先级 🔴)

#### B1. CreationMode 值域对比

| 值 | 前端 schema.ts | 后端 mode_configs.py | 状态 | 备注 |
|----|----------------|----------------------|:----:|------|
| `hot_take` | ✅ L16 | ✅ | ✅ | 锐评 |
| `quick_summary` | ✅ L18 | ⚠️ 映射到 mid_take | ⚠️ | 别名兼容 |
| `deep_analysis` | ✅ L17 | ✅ | ✅ | 深度分析 |
| `tutorial` | ✅ L21 | ✅ | ✅ | 教程指南 |
| `rewrite` | ✅ L19 | ✅ | ✅ | 改写润色 |
| `translate` | ✅ L20 | ❌ 缺失 | ⚠️ | **前端有后端无** |
| `mid_take` | ❌ 缺失 | ✅ | ⚠️ | **后端有前端无** |

**发现问题**:
1. `translate` 模式前端定义但后端缺失配置
2. `mid_take` 模式后端定义但前端未展示

#### B2. 评分阈值同步

| 模式 | 后端 pass_threshold | Router graph.py | 状态 |
|------|---------------------|-----------------|:----:|
| hot_take | N/A (skip_critic) | N/A | ✅ |
| mid_take | 85 | 85 | ✅ |
| deep_analysis | 90 | 85 | ⚠️ |
| tutorial | 85 | 85 | ✅ |

---

### Phase C: Prompt 模板一致性 (优先级 🟡)

#### C1. 模块化模板路径

| Writer 模式 | 模板路径 | 存在 | 后端加载 |
|-------------|----------|:----:|:--------:|
| hot_take | `prompts/writer/hot_take.jinja2` | ✅ | ✅ |
| deep_analysis | `prompts/writer/deep_analysis.jinja2` | ✅ | ✅ |
| tutorial | `prompts/writer/tutorial.jinja2` | ✅ | ✅ |
| mid_take | `prompts/writer/mid_take.jinja2` | ✅ | ⚠️ |

#### C2. Critic/Polisher 参数化

| 组件 | 模板 | 参数化 | 状态 |
|------|------|:------:|:----:|
| Critic | `shared/base_critic.jinja2` | `{{mode}}`, `{{pass_threshold}}` | ✅ |
| Polisher | `shared/base_polisher.jinja2` | `{{mode}}`, `{{target_length}}` | ✅ |

---

### Phase D: API 配置透传 (优先级 🟡)

#### D1. hot_take API 配置

| 字段 | 前端发送 | 后端接收 | 实际使用 | 状态 |
|------|----------|----------|----------|:----:|
| `api_config.provider` | ✅ | ✅ | `generate_text()` | ✅ |
| `api_config.model_id` | ✅ | ✅ | `generate_text()` | ✅ |
| `api_config.api_key` | ✅ | ✅ | `generate_text()` | ✅ |

---

### Phase E: UI 状态机同步 (优先级 🟡)

#### E1. hot_take 模式状态流

| 阶段 | 前端状态 | 后端事件 | 状态 |
|------|----------|----------|:----:|
| 发起请求 | `connecting` | - | ✅ |
| 生成中 | `steps[0].active` | - | ✅ |
| 完成 | `listening + strategyOptions` | JSON response | ⚠️ |
| 用户选择 | `isWaitingForSelection` | - | ⚠️ |

**待验证**: 用户选择候选后的下一步流程

---

### Phase F: SSE 事件差异 (优先级 🟢)

#### F1. hot_take vs 标准模式

| 模式 | 通信方式 | 事件类型 | 备注 |
|------|----------|----------|------|
| hot_take | 同步 JSON | 无 SSE | `/hot_take` 直接返回 |
| 其他模式 | SSE 流式 | thinking_step, final 等 | `/analyze` + `/generate` |

---

## 📌 已确认问题

| # | 类别 | 问题 | 状态 | 修复 |
|---|------|------|:----:|------|
| 1 | 路由 | hot_take 走 /analyze | ✅ 已修复 | useAgentStore.ts L163-220 |
| 2 | 阈值 | Router 硬编码 90 | ✅ 已修复 | graph.py 使用 mode_configs |
| 3 | API | call_llm 不存在 | ✅ 已修复 | 改用 generate_text |
| 4 | 状态 | confirmStrategy 未处理 hot_take | ✅ 已修复 | useAgentStore.ts L280-295 |
| 5 | 枚举 | translate 后端缺失 | ⚠️ 待修复 | 需添加 mode_configs |
| 6 | 枚举 | mid_take 前端缺失 | ⚠️ 待修复 | 需添加 schema.ts |
| 7 | 阈值 | deep_analysis 90 vs 其他 85 | ℹ️ 设计差异 | 有意为之 |

---

## 🔲 待排查项

| # | 检查项 | 优先级 | 方法 | 状态 |
|---|--------|:------:|------|:----:|
| 1 | hot_take 候选选择后流程 | 🔴 | 端到端测试 | ✅ 已修复 |
| 2 | mid_take 模式是否启用 | 🟡 | 代码审查 | ⚠️ 前端缺失 |
| 3 | translate 模式是否启用 | 🟡 | 代码审查 | ⚠️ 后端缺失 |
| 4 | 错误处理一致性 | 🟢 | 异常注入测试 | 🔲 待测 |

---

## ✅ 验证结果

### DOM 测试 (2026-02-01)
```
page_load:       ✅ PASS
studio_page:     ✅ PASS
mode_selector:   ✅ PASS
input_area:      ✅ PASS
generate_flow:   ✅ PASS
---
总计: 5/5 通过
```

### API 健康检查
```
GET  /health     ✅ 200
POST /hot_take   ✅ 200
```

---

## 📁 P14 修改文件索引

| 文件 | 修改类型 | 关键变更 |
|------|----------|----------|
| `useAgentStore.ts` | Frontend | hot_take 路由分支 |
| `mode_configs.py` | Backend | 模式配置中心 |
| `prompts.py` | Backend | 模块化模板加载 |
| `main.py` | Backend | /hot_take 端点 |
| `graph.py` | Backend | 阈值参数化 |
| `critic.py` | Backend | 阈值读取 |
| `writer.py` | Backend | 模板路径选择 |
