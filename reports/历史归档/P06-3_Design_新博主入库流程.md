# P10-7 新博主入库流程设计

> 目标：建立标准化的新博主风格入库流程

---

## 📦 入库流程总览

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1: 素材收集  →  Phase 2: 智能清洗  →  Phase 3: 质量验证     │
│       ↓                    ↓                    ↓                   │
│  [原始文章]          [AI 分析+切片]         [多角度生成测试]        │
│       ↓                    ↓                    ↓                   │
│  [20-100篇]          [上传 Lark]           [评分达标?]              │
│                            ↓                    ↓                   │
│                      [配置更新]             [上线/迭代]             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 素材收集

| 项目 | 要求 |
|------|------|
| **来源** | 博主公众号/微博/专栏 |
| **数量** | 最少 20 篇，推荐 50-100 篇 |
| **格式** | Markdown / 纯文本 |
| **命名** | `{日期}_{标题}.md` |
| **存放** | `backend/data/Web2风格/{blogger_id}/` |

---

## Phase 2: 智能清洗 (cleaner_cli 增强)

### 2.1 基础切片 (现有功能)
- Hook (开头爆点)
- Body (正文段落)
- Quote (金句)
- Transition (过渡句)

### 2.2 🆕 AI 风格分析 (新增)

清洗时 AI 应输出：

```json
{
  "blogger_id": "example_blogger",
  "style_profile": {
    "core_strengths": ["情绪共鸣", "数据驱动", "案例丰富"],
    "tone": "犀利幽默 + 专业深度",
    "structure_pattern": "问题引入 → 案例轰炸 → 观点升华",
    "sentence_style": "短句爆发，多用反问和排比"
  },
  "recommended_combinations": [
    {"with": "mimeng", "weight": 40, "reason": "情绪互补"},
    {"with": "banfo", "weight": 60, "reason": "逻辑互补"}
  ],
  "recommended_for": ["项目评测", "行业批判", "投资避坑"],
  "temperature": 0.7,
  "forbidden_words": ["delve", "tapestry"]
}
```

### 2.3 上传 Lark

- 切片存入统一表，`style` 字段标记博主 ID
- 元数据存入配置表

---

## Phase 3: 质量验证

### 3.1 多角度生成测试

| 测试维度 | 测试内容 | 次数 |
|----------|----------|------|
| **主题类型** | 热点追踪 / 项目评测 / 行业批判 | 各 2 次 |
| **内容长度** | 短篇 / 中篇 / 长文 | 各 1 次 |
| **风格搭配** | 单风格 / 与推荐风格组合 | 各 2 次 |

### 3.2 评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 风格还原度 | 30% | 是否像原博主 |
| 可读性 | 25% | 流畅、不卡顿 |
| 爆款潜力 | 25% | 情绪触发、分享欲 |
| 专业度 | 20% | 事实准确、逻辑清晰 |

### 3.3 达标标准

- **综合评分 ≥ 70**: ✅ 上线
- **综合评分 60-70**: 🟡 需微调（调整 traits 或补充素材）
- **综合评分 < 60**: 🔴 不通过（大量补充素材或放弃）

---

## Phase 4: 配置上线

### 4.1 更新 config.yaml

```yaml
new_blogger:
  id: "new_blogger"
  name: "新博主体"
  icon: "🆕"
  color: "#xxx"
  description: "AI分析生成的描述"
  data_dir: "data/Web2风格/new_blogger"
  max_samples: 3
  traits:
    tone: "AI分析生成"
    structure: "AI分析生成"
    sentence_style: "AI分析生成"
  forbidden_words: []
  temperature: 0.7
```

### 4.2 更新前端 schema.ts

```typescript
export const WritingStyleSchema = z.enum([
  // ... 现有风格
  'new_blogger',  // 新增
]);
```

### 4.3 添加组合 (可选)

```yaml
new_combo:
  id: "new_combo"
  name: "XX组合"
  styles:
    - { id: "new_blogger", weight: 60 }
    - { id: "mimeng", weight: 40 }
  recommended_for: ["场景1", "场景2"]
```

---

## 🔧 待开发功能

| 功能 | 优先级 | 说明 |
|------|--------|------|
| cleaner_cli AI 分析模块 | 🔴 高 | 自动生成 style_profile |
| 质量验证脚本 | 🟠 中 | 批量生成+评分 |
| 风格管理 UI | 🟡 低 | 可视化管理 |

---

## 📋 入库清单 (Checklist)

新博主入库时，按此清单执行：

- [ ] 收集素材 ≥20 篇
- [ ] 存放到正确目录
- [ ] 运行 cleaner_cli 清洗
- [ ] 检查 AI 风格分析结果
- [ ] 上传到 Lark
- [ ] 更新 config.yaml
- [ ] 更新 schema.ts
- [ ] 运行质量验证测试 (≥6次)
- [ ] 评分达标 (≥70分)
- [ ] 部署上线
- [ ] 更新前端风格列表

---

> 下一步：实现哪个模块？
