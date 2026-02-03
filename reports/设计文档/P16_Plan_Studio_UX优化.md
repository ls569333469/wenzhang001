# P16: Studio UX 优化 + 模式改名

> **日期**: 2026-02-02
> **状态**: 进行中

---

## 一、模式改名 ✅ 已完成

### 1.1 映射关系

| 旧内部ID | 新内部ID | 显示名称 | 说明 |
|:---|:---|:---|:---|
| `hot_take` | `hot_take` (不变) | 🔥 锐评 | 50-150字 |
| `quick_summary` | `mid_article` | 中篇 | ~500字 |
| `deep_analysis` | `long_article` | 长篇 | ~1200字 |

### 1.2 修改范围

**前端 (11文件)**:
- `schema.ts` - 枚举、默认值、别名
- `schema.test.ts` - 测试用例
- `constants.ts` - 模式定义顺序
- `useAgentStore.ts` - 默认值
- `useModeWriterStore.ts` - 别名处理
- `usePromptStore.ts` - 接口、迁移逻辑(v2)
- `ModeWriterConfig.tsx`, `AgentModelConfig.tsx`, `WriterPromptEditor.tsx` - UI
- `defaultPrompts.ts`, `promptSchemas.ts` - 提示词配置

**后端 (6文件)**:
- `main.py`, `graph.py` - API/状态默认值
- `mode_configs.py` - 模式配置
- `prompts.py` - 模板路径映射
- `writer.py`, `critic.py` - Agent默认值

---

## 二、篇幅选择器改版 ✅ 已完成

### 2.1 设计

**旧版**:
```
[ 推文(~300字) ] [ 推文串(~800字) ] [ 帖子(~1.5k字) ]
```

**新版**:
```
[ 默认 ] [ 自定义 ] [ ___ 字 ]  ← 输入框仅在"自定义"时显示
```

### 2.2 逻辑

| 选项 | 行为 |
|:---|:---|
| **默认** | 使用 `mode_configs.py` 中该模式的预设字数 |
| **自定义** | 用户输入的字数(50-5000)覆盖默认值 |

### 2.3 修改范围

- `schema.ts` - 新增 `LengthTypeSchema`, `custom_length`
- `ConfigPanel.tsx` - 新 UI 组件
- `HeroInput.tsx` - 同步更新
- `main.py` - 新增 `length_type`, `custom_length` 参数
- `graph.py` - AgentState 新增 `custom_length`

---

## 三、UX 三项优化 [ ] 待实施

### 3.1 扩展内容区宽度
- **目标**: 减少两侧留白，内容区利用更多屏幕空间
- **涉及文件**: Studio 页面布局组件
- **预计时间**: 5分钟

### 3.2 添加"新建创作"按钮
- **目标**: 生成完成后可一键返回输入界面
- **位置**: 结果展示区顶部或底部
- **涉及文件**: 结果展示组件
- **预计时间**: 10分钟

### 3.3 生成中显示素材预览
- **目标**: 让用户知道正在处理什么内容
- **内容**: 显示正在分析的素材/参考链接
- **涉及文件**: 生成中状态组件
- **预计时间**: 10分钟

---

## 四、验收标准

- [x] 模式名称在 UI 中正确显示 (锐评 → 中篇 → 长篇)
- [x] 旧模式名 (deep_analysis, quick_summary) 兼容
- [x] localStorage 迁移无数据丢失
- [x] 篇幅选择器显示 默认/自定义
- [ ] 内容区宽度扩展
- [ ] 新建创作按钮可用
- [ ] 生成中显示素材预览
