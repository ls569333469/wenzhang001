# 创作工作流架构重构方案 v2

**日期**: 2026年1月28日 22:35  
**状态**: 设计方案 v2 - 根据用户反馈深度优化  
**优先级**: P0

---

## 用户反馈处理

---

## 反馈 1: 写作风格智能推荐

### 需求
输入内容素材后，系统自动推荐适合的写作风格（如 mimeng 或 banfo），供用户参考选择。

### 设计方案

#### A. 推荐触发时机
在 **Strategist 阶段**，分析用户输入后，返回风格推荐：

```
用户输入素材 → Strategist 分析 → 返回：
  - 策略方案 (options)
  - 标题候选 (title_candidates)  
  - 风格推荐 (style_recommendations) ← 新增
```

#### B. 风格推荐逻辑

**方案 1: 基于内容特征匹配**
```python
# strategist.py 新增
def recommend_styles(content: str, available_styles: List[str]) -> List[Dict]:
    """基于内容特征推荐风格"""
    
    # 特征检测
    features = {
        "has_data": bool(re.search(r'\d+[\%万亿]', content)),      # 有数据
        "has_emotion": any(w in content for w in ['焦虑', '恐慌', '暴富', '绝望']),
        "has_story": any(w in content for w in ['他说', '她说', '故事', '经历']),
        "is_technical": any(w in content for w in ['协议', '智能合约', 'TVL', 'APY']),
        "is_news": any(w in content for w in ['宣布', '发布', '获批', '上线']),
    }
    
    # 风格-特征匹配规则
    style_rules = {
        "mimeng": {"has_emotion": 2, "has_story": 1},      # 情绪驱动
        "banfo": {"has_data": 2, "is_technical": 1},       # 数据分析
        "xinshixiang": {"has_story": 2, "has_emotion": 1}, # 叙事驱动
        "insider": {"is_news": 2, "is_technical": 1},      # 内幕消息
    }
    
    # 计算匹配分数
    scores = {}
    for style, rules in style_rules.items():
        if style in available_styles:
            score = sum(rules.get(f, 0) for f, v in features.items() if v)
            scores[style] = score
    
    # 返回 Top 3
    sorted_styles = sorted(scores.items(), key=lambda x: -x[1])[:3]
    return [
        {
            "style_id": s,
            "style_name": STYLE_NAMES.get(s, s),
            "match_score": score,
            "reason": generate_reason(s, features)
        }
        for s, score in sorted_styles
    ]
```

**方案 2: LLM 辅助推荐（更智能）**
```jinja2
{# strategist.jinja2 新增推荐任务 #}
5. RECOMMEND WRITING STYLE
Based on the source material, recommend 2-3 most suitable writing styles:

Available Styles (with sample counts):
{% for style in available_styles %}
- {{ style.id }}: {{ style.name }} ({{ style.sample_count }}条素材)
{% endfor %}

Output format:
"style_recommendations": [
    {
        "style_id": "banfo",
        "style_name": "半佛仙人体",
        "match_score": 85,
        "reason": "素材包含大量数据和商业逻辑分析，适合半佛的犀利拆解风格"
    }
]
```

#### C. 前端展示
在策略选择页面显示风格推荐卡片：
```
╔════════════════════════════════════════════════╗
║  🎨 推荐写作风格                               ║
╠════════════════════════════════════════════════╣
║  ⭐ 半佛仙人体 (匹配度 85%)                    ║
║     "素材数据丰富，适合犀利拆解"              ║
║                                                ║
║  ★  咪蒙体 (匹配度 70%)                        ║
║     "情绪点明显，可强化共鸣"                  ║
║                                                ║
║  [使用推荐]  [保持当前: 咪蒙体]               ║
╚════════════════════════════════════════════════╝
```

---

## 反馈 2: 多表 Lark 素材架构

### 现状问题
- mimeng 和 banfo 各有 2W+ 行数据
- 单个 Lark 多维表格有行数上限
- 后续可能新增更多博主

### 设计方案: 博主独立表单 + 表单注册

#### A. Lark 表单架构
```
Lark Base (bloggers_repo)
├── Table: mimeng_styles      (2W+ rows)
├── Table: banfo_styles       (1W+ rows)
├── Table: xiaohongshu_styles (将来)
├── Table: insider_styles     (将来)
└── Table: _registry          (元数据表)
```

#### B. 元数据注册表 `_registry`
| 字段 | 说明 |
|------|------|
| style_id | 风格ID (mimeng, banfo...) |
| style_name | 显示名称 (咪蒙体, 半佛仙人体...) |
| table_id | 对应的 Lark Table ID |
| sample_count | 素材数量 (自动更新) |
| last_sync | 最后同步时间 |
| status | 启用/禁用 |

#### C. SyncService 多表支持
```python
# sync_service_v2.py
class MultiTableSyncService:
    def __init__(self):
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Dict]:
        """从 Lark _registry 表加载所有博主配置"""
        # 返回: {"mimeng": {"table_id": "xxx", "name": "咪蒙体", ...}, ...}
        pass
    
    def get_samples(self, style: str, count: int = 3) -> List[Dict]:
        """从指定博主的表中获取样本"""
        if style not in self.registry:
            return []
        
        table_id = self.registry[style]["table_id"]
        return self._fetch_from_table(table_id, count)
    
    def get_available_styles(self) -> List[Dict]:
        """返回所有已注册且有素材的风格"""
        return [
            {"id": k, "name": v["name"], "count": v.get("sample_count", 0)}
            for k, v in self.registry.items()
            if v.get("status") == "enabled" and v.get("sample_count", 0) > 0
        ]
    
    def register_new_blogger(self, style_id: str, table_id: str, name: str):
        """注册新博主表单"""
        # 向 _registry 表添加一条记录
        pass
```

#### D. 新增博主流程
1. 在 Lark 创建新表 `{blogger}_styles`
2. 导入清洗后的素材
3. 调用 `POST /api/bloggers/register` 注册
4. 前端自动发现并显示新风格选项

---

## 反馈 3: mode/style 分离 - 流程验证

### 核心问题
**`mode` 到底控制什么？如何与 `style` 分工？**

### 专业设计分析

#### A. 概念澄清

| 维度 | mode (创作模式) | style (写作风格) |
|------|-----------------|------------------|
| **控制什么** | 创作流程、输出结构、深度 | 语言风格、语气、句式 |
| **影响哪些 Agent** | Strategist (策略)、流程路由 | Writer (写手) |
| **用户感知** | "我要做什么" | "我要怎么表达" |

#### B. 完整数据流路径

```
前端配置
├── mode: "deep_analysis"     → 决定 Strategist 策略类型
├── style: "banfo"            → 决定 Writer 风格模板和 Few-Shot
├── length: "medium"          → 决定字数限制
└── retention_rate: 0.5       → 决定素材保留度

         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  main.py: GenerateRequest                               │
│  ─────────────────────────────────────────────────────  │
│  input: str                                             │
│  mode: str           ← 创作模式                         │
│  style: str          ← 写作风格 (新增)                  │
│  length: str         ← 篇幅长度 (新增)                  │
│  retention_rate: float ← 保留率 (新增)                  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  graph.py: AgentState                                   │
│  ─────────────────────────────────────────────────────  │
│  mode: str           ← 用于 Strategist                  │
│  style: str          ← 用于 Writer/Few-Shot 选择        │
│  length: str         ← 用于 Writer 字数控制             │
│  length_constraints: Dict  ← 计算后的字数限制           │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Strategist  │ ──▶ │   Writer     │ ──▶ │   Critic     │ ──▶ ...
│  ───────────  │     │  ───────────  │     │  ───────────  │
│  uses: mode  │     │  uses: style │     │              │
│              │     │  uses: length│     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

#### C. mode 预定义值 - 简化版

**设计原则：**
- **话题**：由用户输入素材决定（DeFi、GameFi、空投等）
- **风格**：由 `style` 参数 + Lark 素材 Few-Shot 决定
- **mode**：只控制「写作方法/深度/结构」

```python
CREATION_MODES = {
    "deep_analysis": {
        "name": "深度分析",
        "description": "全面深度分析，长文结构，多角度论证",
        "typical_length": "long",
        "structure_hint": "引子→背景→核心分析→数据支撑→结论"
    },
    "quick_take": {
        "name": "快讯速评",  
        "description": "快速产出，要点突出，适合热点追踪",
        "typical_length": "short",
        "structure_hint": "核心结论→关键数据→一句话总结"
    },
    "tutorial": {
        "name": "教程指南",
        "description": "步骤清晰，可操作性强",
        "typical_length": "medium",
        "structure_hint": "目标→前置准备→分步操作→注意事项"
    },
    "rewrite": {
        "name": "改写润色",
        "description": "基于原文改写，保持核心信息",
        "typical_length": "same_as_source",
        "structure_hint": "遵循原文结构"
    }
}
```

**这样设计的好处：**
1. 用户输入 "Solana 上的新 memecoin" → 话题自动确定
2. 用户选 style="banfo" → 风格由素材 Few-Shot 学习
3. 用户选 mode="quick_take" → 只影响篇幅和结构

#### D. 流程正常执行验证点

| 检查点 | 验证内容 |
|--------|----------|
| ① 前端→后端 | `style` 字段是否包含在请求中 |
| ② Request→State | `style` 是否正确传入 AgentState |
| ③ State→Writer | Writer 是否使用 `style` 获取样本 |
| ④ 样本获取 | `sync_service.get_samples(style=style)` |
| ⑤ Prompt 渲染 | Writer prompt 是否接收 style 相关变量 |

---

## 反馈 4: Prompt 模板 - Web3 话题覆盖

### 当前状态
根据 `09-1_Plan` 文档：
- **P10-8 Web3 创作模式优化** 计划新增：热点追踪、项目评测、推特线程
- 但尚未实施

### Prompt 模板覆盖分析

| 话题类型 | 当前支持 | 需要优化 |
|----------|:--------:|:--------:|
| 项目评测 | ✅ narrative_type="project_review" | 模板需中文化 |
| 市场新闻 | ✅ narrative_type="market_news" | 模板需中文化 |
| 教程指南 | ✅ narrative_type="tutorial" | 模板需中文化 |
| 观点输出 | ✅ narrative_type="opinion" | 模板需中文化 |
| 微小说 | ✅ narrative_type="micro_novel" | 模板需中文化 |
| 热点追踪 | ❌ 未实现 | 需新增 |
| 推特线程 | ❌ 未实现 | 需新增 |
| 空投教程 | ❌ 未实现 | 需新增 |
| Alpha 信号 | ❌ 未实现 | 需新增 |

### 框架修复后的 Prompt 精修计划
1. 中文化所有核心指令
2. 为每种 `mode`/`narrative_type` 编写专用 Prompt 片段
3. 增加显式约束（字数、格式、禁用词）
4. 增强 Few-Shot 示例引导

---

## 反馈 5: 润色师 → 排版专家

### 确认: 只需修改 Prompt 模板

**修改 `polisher.jinja2`**:

```jinja2
角色：你是「排版专家」，负责最终格式调整。

任务：
1. 调整 Markdown 格式
   - 标题层级 (# ## ###)
   - 加粗重点关键词
   - 列表格式规范
2. 优化段落分隔和换行
3. 添加适当的 emoji 装饰 (不超过 5 个)
4. 检查并修复格式问题

⚠️ 严格禁止：
- 修改任何实质内容
- 改变表述和措辞
- 删除或添加论点
- 更改数据和事实

输入内容：
{{ draft }}

编辑反馈（仅参考格式建议）：
{{ critique_feedback }}

输出：排版优化后的完整内容
```

**代码无需修改**，polisher_agent 函数保持不变。

---

## 反馈 6: 仿写相似度 - 专业设计

### 设计目标
提供专业的内容"保留度"控制机制，而非简单的百分比

### A. 保留度等级定义

| 等级 | 保留度 | 中文名 | 含义 |
|------|:------:|--------|------|
| L1 | **95%** | 润色优化 | 仅语言润色，结构和论点完全保留 |
| L2 | **75%** | 框架保留 | 保留核心框架，允许表达优化 |
| L3 | **50%** | 观点继承 | 继承核心观点，重新组织表达 |
| L4 | **30%** | 主题借用 | 仅借用主题和关键词，大幅再创作 |
| L5 | **10%** | 灵感触发 | 仅作为灵感来源，完全重新创作 |

### B. 保留度影响矩阵

| 保留度 | 结构 | 论点 | 数据 | 案例 | 表达 | 风格 |
|--------|:----:|:----:|:----:|:----:|:----:|:----:|
| L1 95% | ✅保留 | ✅保留 | ✅保留 | ✅保留 | ⚡优化 | ⚡吸收 |
| L2 75% | ✅保留 | ✅保留 | ✅保留 | ⚡可换 | ⚡重写 | ✅应用 |
| L3 50% | ⚡重组 | ✅保留 | ✅引用 | ⚡可换 | ⚡重写 | ✅应用 |
| L4 30% | ❌重建 | ⚡取精 | ⚡选用 | ❌新增 | ❌新创 | ✅应用 |
| L5 10% | ❌新建 | ❌新创 | ⚡参考 | ❌新增 | ❌新创 | ✅应用 |

### C. 仿写工作在哪个智能体?

**答案：由 Strategist + Writer 协作完成**

```
┌─────────────────────────────────────────────────────────────┐
│                    仿写任务分工                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Strategist (策略师) - 负责「信息锚点提取」                 │
│  ─────────────────────────────────────────────────────────  │
│  • 根据 retention_level 决定提取多少信息锚点                │
│  • L1-L2: 提取所有论点和数据作为 must_mention               │
│  • L3: 提取核心论点作为 must_mention，其他作为 can_extend   │
│  • L4-L5: 只提取主题关键词作为 reference_only               │
│                                                             │
│  Writer (写手) - 负责「风格应用 + 内容生成」                │
│  ─────────────────────────────────────────────────────────  │
│  • 根据 retention_level 调整创作自由度                      │
│  • L1: 逐句改写，保持原意                                   │
│  • L2: 段落重组，保持框架                                   │
│  • L3-L5: 自由发挥，参考锚点                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### D. 与正常写作的关系

**不冲突 - 统一模型**

| 场景 | retention_level | 说明 |
|------|:---------------:|------|
| 素材仿写 | L1-L2 | 用户提供完整素材，要求高度保留 |
| 参考创作 | L3 | 用户提供素材，希望借鉴但重新表达 |
| 灵感创作 | L4-L5 | 用户提供话题或片段，自由发挥 |
| 纯原创 | L5 | 用户只提供主题词，完全原创 |

**所有场景使用同一套智能体流程**，`retention_level` 只是一个参数。

### E. 实现细节

**1. GenerateRequest 新增字段**
```python
class GenerateRequest(BaseModel):
    # ...
    retention_level: int = 3  # 1-5, 默认 L3 (观点继承)
```

**2. Strategist Prompt 注入保留度指令**
```jinja2
{% if retention_level == 1 %}
## 润色优化模式 (95% 保留)
你的任务是分析并提取原文的【全部】结构和内容：
- 提取每个段落的核心论点 → 全部放入 must_mention
- 提取所有数据和事实 → 全部放入 key_data
- 记录原文的论述顺序 → 供 Writer 参考

{% elif retention_level == 2 %}
## 框架保留模式 (75% 保留)
你的任务是提取原文的【核心框架】：
- 提取主要论点 → 放入 must_mention
- 提取关键数据 → 放入 key_data
- 标记可扩展点 → 放入 can_extend

{% elif retention_level == 3 %}
## 观点继承模式 (50% 保留)
你的任务是提取原文的【核心观点】并设计新的表达方式：
- 提取 2-3 个核心观点 → 放入 must_mention
- 提取支撑数据 → 放入 key_data
- 设计 3 个不同的新角度 → 生成 options

{% elif retention_level >= 4 %}
## 灵感触发模式 (≤30% 保留)
你的任务是从原文中提取【灵感关键词】并大胆创新：
- 提取主题关键词 → 放入 reference_only (不强制使用)
- 完全自由设计新的角度和论点
- 生成 3 个创新性的选题方案
{% endif %}
```

**3. Writer Prompt 相应调整**
```jinja2
{% if retention_level <= 2 %}
⚠️ 高保留模式要求：
- 不得改变原文的核心论点
- 所有 must_mention 必须出现且位置相近
- 可以优化表达但不改变含义
{% elif retention_level == 3 %}
📝 平衡模式要求：
- 核心观点必须体现
- 表达方式可以完全重写
- 允许引入新的支撑案例
{% else %}
🚀 创新模式要求：
- 参考关键词但不拘泥
- 大胆表达新观点
- 风格为王，灵活发挥
{% endif %}
```

### G. 信息来源标记（防幻觉机制）

**现阶段方案：输出内容标记**

Writer 在生成内容时标记信息来源，便于人工核实：

```markdown
📌 [素材] ETH 价格突破 3000 美元
💡 [分析] 这可能与美联储降息预期有关
⚠️ [待核实] 预计 Q2 还将上涨 20%
```

**Prompt 约束（根据 retention_level）：**

| 等级 | 标记要求 |
|:----:|----------|
| L1-L2 | 只允许 📌[素材]，其他禁止 |
| L3 | 允许 📌[素材] + 💡[分析]，数据需来自素材 |
| L4-L5 | 允许全部标记，需人工核实 |

**未来升级路径：**
- P3: 交叉验证 - 多 Agent 核实关键数据
- P4: 求实验证 - 调用外部 API 验证链上数据

---

## 📊 修订后的实施优先级

| 优先级 | 任务 | 工作量 | 依赖 |
|--------|------|:------:|:----:|
| **P0-1** | GenerateRequest/AgentState 添加 style/length/retention 字段 | 1h | 无 |
| **P0-2** | Writer 使用 style 获取 Few-Shot | 1h | P0-1 |
| **P0-3** | 篇幅长度控制 Prompt 修改 | 1h | P0-1 |
| **P1-1** | Polisher 改为排版专家 (Prompt 修改) | 0.5h | 无 |
| **P1-2** | 保留度等级实现 (Strategist/Writer Prompt) | 3h | P0-1 |
| **P1-3** | 多表 Lark 架构 (SyncService v2) | 4h | 无 |
| **P1-4** | 多智能体 LLM 配置启用 | 2h | 无 |
| **P2-1** | 风格智能推荐 | 3h | P1-3 |
| **P2-2** | Prompt 模板中文化 | 3h | P1-2 |
| **P2-3** | 新 mode 扩展 (热点/评测/线程) | 4h | P2-2 |

---

## ✅ 确认问题

1. **多表 Lark 架构**：是否已经创建了 mimeng/banfo 的独立表单？还是目前都在一个表中？
2. **保留度命名**：L1-L5 这种命名方式是否清晰？还是用其他术语？
3. **实施节奏**：是否先实施核心框架修复 (P0)，再进行其他优化？

---

**文档版本**: v2.1 (最终版)  
**更新时间**: 2026-01-28 22:58

**包含内容**:
- ✅ 反馈 1: 写作风格智能推荐
- ✅ 反馈 2: 多表 Lark 素材架构 
- ✅ 反馈 3: mode/style 分离设计（简化为 4 个 mode）
- ✅ 反馈 4: Prompt 模板覆盖分析
- ✅ 反馈 5: 润色师 → 排版专家
- ✅ 反馈 6: 保留度等级 + 信息来源标记（防幻觉）

