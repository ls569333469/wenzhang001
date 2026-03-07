# P10 执行计划 - 难度评估与详细任务分解

**创建日期**: 2026-01-28 23:30  
**基于**: `10_Plan_创作工作流架构重构.md` v2.1

---

## 📊 总体评估

| 维度 | 评分 | 说明 |
|------|:----:|------|
| **代码改动量** | 中等 | ~500-700 行代码修改 |
| **技术难度** | ★★★☆☆ | 主要是参数传递和Prompt修改，无复杂算法 |
| **风险等级** | 中等 | 需修改核心数据流，可能影响现有功能 |
| **预估工时** | 2-3天 | 含测试和调试 |

---

## 🔧 代码改动分析

### 需要修改的文件

| 文件 | 改动类型 | 改动量 | 难度 |
|------|----------|:------:|:----:|
| `main.py` | 新增字段 | +20行 | ★★☆ |
| `graph.py` | 新增状态+传递 | +30行 | ★★☆ |
| `writer.py` | style替代mode | +40行 | ★★★ |
| `strategist.py` | 推荐+保留度 | +80行 | ★★★ |
| `polisher.jinja2` | Prompt重写 | ~30行 | ★☆☆ |
| `writer.jinja2` | 保留度指令 | +60行 | ★★☆ |
| `strategist.jinja2` | 推荐+保留度 | +80行 | ★★☆ |
| `sync_service.py` | 多表架构 | +150行 | ★★★★ |
| `前端 store` | 新参数传递 | +30行 | ★★☆ |
| `前端 ConfigPanel` | UI 控件 | +100行 | ★★★ |

**总计**: ~620 行代码修改/新增

---

## ⚠️ 潜在风险与问题

### 1. 数据流断裂风险 (高)
- **问题**: 前端→后端→Agent 的参数传递链较长
- **表现**: 新增的 `style`/`length`/`retention_level` 可能在某个环节丢失
- **防范**: 每个环节添加日志，逐步验证

### 2. Few-Shot 获取失败 (中)
- **问题**: `sync_service` 按 style 获取样本，如果 style 不存在则返回空
- **表现**: Writer 无 Few-Shot 参考，输出质量下降
- **防范**: 添加 fallback 到默认 style

### 3. Lark 多表迁移 (高)
- **问题**: 需要在 Lark 中创建 `_registry` 元数据表
- **表现**: 如果表结构不正确，整个素材系统失效
- **防范**: 先在测试 Base 中验证，再迁移生产数据

### 4. 前端状态同步 (中)
- **问题**: 新增 3 个参数需要同步到 URL/Store
- **表现**: 刷新页面后参数丢失
- **防范**: 使用 nuqs 进行 URL 状态同步

### 5. Prompt 模板过长 (低)
- **问题**: 条件分支增多导致 prompt token 超限
- **表现**: LLM 调用失败或输出截断
- **防范**: 分离模板，按需加载

---

## 📋 详细执行计划

### Phase 0: 准备工作 (0.5h)

| 任务 | 说明 | 产出 |
|------|------|------|
| 0.1 | 创建开发分支 `feature/p10-workflow-refactor` | Git branch |
| 0.2 | 备份当前 prompts | backup 文件夹 |
| 0.3 | 记录当前 API 行为 | 基线测试结果 |

---

### Phase 1: 参数传递链 (P0, 2h)

#### 1.1 后端 Request/State 扩展

**`main.py` GenerateRequest**:
```python
class GenerateRequest(BaseModel):
    input: str
    mode: str = "deep_analysis"        # 创作模式
    style: str = "auto"                # 写作风格 ← 新增
    length: str = "medium"             # 篇幅长度 ← 新增
    retention_level: int = 3           # 保留度1-5 ← 新增
    narrative_type: str = "project_review"
    # ... 其他字段
```

**`graph.py` AgentState**:
```python
class AgentState(TypedDict):
    # ... 现有字段
    style: str                         # ← 新增
    length: str                        # ← 新增
    retention_level: int               # ← 新增
    length_constraints: Dict[str, int] # ← 新增 (计算后的字数)
```

#### 1.2 节点参数传递

**`graph.py` generate_narrative**:
```python
initial_state = {
    # ... 现有字段
    "style": request.style,
    "length": request.length,
    "retention_level": request.retention_level,
    "length_constraints": calculate_length(request.length),
}
```

#### 验证点
- [ ] 打印日志确认字段传递
- [ ] SSE 返回参数确认

---

### Phase 2: Writer style 替代 mode (P0, 1.5h)

#### 2.1 修改样本获取逻辑

**`writer.py`**:
```python
def writer_agent(state: dict):
    # 旧: template = MODE_TEMPLATES.get(mode, ...)
    # 新: 从 style 获取
    style = state.get("style", "auto")
    
    if style == "auto":
        # 使用 Strategist 推荐的 style
        style = state.get("recommended_style", "mimeng")
    
    # Few-Shot 样本获取
    samples = sync_service.get_samples(style=style, count=3)
```

#### 2.2 模板选择逻辑

保留 `MODE_TEMPLATES` 但基于 `style` 选择：
```python
template = MODE_TEMPLATES.get(style, MODE_TEMPLATES["mimeng"])
```

#### 验证点
- [ ] style="banfo" 时获取半佛样本
- [ ] style="auto" 时使用推荐值

---

### Phase 3: 篇幅长度控制 (P0, 1h)

#### 3.1 长度映射

**`constants.py`** 或 `graph.py`:
```python
LENGTH_MAP = {
    "short": {"min": 300, "max": 600, "target": 450},
    "medium": {"min": 800, "max": 1500, "target": 1000},
    "long": {"min": 2000, "max": 4000, "target": 2500}
}
```

#### 3.2 Prompt 注入

**`writer.jinja2`**:
```jinja2
字数要求：
- 目标字数：{{ length_constraints.target }} 字
- 允许范围：{{ length_constraints.min }} - {{ length_constraints.max }} 字
- 超出范围将被拒绝，请严格控制
```

---

### Phase 4: Polisher 改排版专家 (P1, 0.5h)

直接修改 `polisher.jinja2`:
```jinja2
角色：你是「排版专家」，负责最终格式调整。

任务：
1. Markdown 格式规范化 (标题、加粗、列表)
2. 段落分隔优化
3. 添加适量 emoji (≤5个)
4. 修复格式问题

⚠️ 严格禁止：
- 修改实质内容
- 改变表述措辞
- 删减/添加论点
- 更改数据事实

输入：{{ draft }}
编辑反馈（仅格式）：{{ critique_feedback }}
```

---

### Phase 5: 保留度等级 (P1, 3h)

#### 5.1 Strategist Prompt 分支

**`strategist.jinja2`**:
```jinja2
{% if retention_level == 1 %}
## 润色优化模式 (95% 保留)
提取原文【全部】结构和内容...
{% elif retention_level == 2 %}
## 框架保留模式 (75% 保留)
...
{% endif %}
```

#### 5.2 Writer Prompt 约束

**`writer.jinja2`**:
```jinja2
{% if retention_level <= 2 %}
⚠️ 高保留模式：不得改变核心论点，must_mention 必须出现
{% else %}
🚀 创新模式：参考关键词，大胆发挥
{% endif %}
```

#### 5.3 信息来源标记

```jinja2
在内容中使用以下标记：
- 📌 [素材] - 来自原始素材
- 💡 [分析] - AI 推理分析
- ⚠️ [待核实] - 需人工验证
```

---

### Phase 6: Google Sheets A/B 测试数据源 (P1, 2h) ✅ 完成

> **更新**: 2026-01-29 - 由于 Lark API 配额耗尽，改用 Google Sheets 作为备用数据源

#### 6.1 用户配置 (已完成)
1. 创建 Google Cloud Service Account
2. 下载 JSON 密钥到 `backend/config/google_service_account.json`
3. 创建 Spreadsheet `Quantum_Samples`，包含 `mimeng`, `banfo` 等工作表
4. 共享给 Service Account

#### 6.2 代码实现 (已完成)

**新增文件**:
- `backend/app/services/google_sheets_source.py` - Google Sheets 数据源
- `backend/app/services/sample_service.py` - A/B 测试包装器
- `backend/scripts/test_google_sheets.py` - 连接测试脚本

**`sample_service.py` 核心逻辑**:
```python
class SampleService:
    def get_samples(self, style, emotion, count):
        if self._source_mode == "google_sheets":
            return google_sheets_source.get_samples(style, emotion, count)
        elif self._source_mode == "ab_test":
            if random.random() < self._ab_ratio:
                return google_sheets_source.get_samples(...)
            else:
                return sync_service.get_samples(...)
        else:
            return sync_service.get_samples(style, emotion, count)
```

#### 6.3 配置方式

`.env` 新增:
```env
SAMPLE_SOURCE=ab_test              # lark | google_sheets | ab_test
AB_TEST_GOOGLE_RATIO=0.5           # 0.0-1.0
GOOGLE_SHEETS_SPREADSHEET=<ID>     # 从 URL 提取
GOOGLE_SHEETS_CREDENTIALS=config/google_service_account.json
```

#### 6.4 验证结果
- ✅ 连接测试通过
- ✅ 读取到 238 条记录
- ✅ `/generate` API 正常工作

---

### Phase 7: 前端适配 (P2, 2h)

#### 7.1 ConfigPanel 新增控件

- Style 选择器 (下拉)
- Length 选择器 (Short/Medium/Long)
- Retention Level 滑块 (1-5)

#### 7.2 Store 集成

**`useAgentStore.ts`**:
```typescript
startSession: (input, options) => {
    fetch('/generate', {
        body: JSON.stringify({
            input,
            mode: options.mode,
            style: options.style,      // 新增
            length: options.length,    // 新增
            retention_level: options.retentionLevel  // 新增
        })
    })
}
```

---

## 📅 推荐执行顺序

```
Day 1 (上午):
├── Phase 0: 准备工作
├── Phase 1: 参数传递链
└── Phase 2: Writer style 替代

Day 1 (下午):
├── Phase 3: 篇幅长度控制
├── Phase 4: Polisher 改排版专家
└── 端到端测试

Day 2:
├── Phase 5: 保留度等级
└── 本地验证

Day 3:
├── Phase 6: 多表 Lark 架构
├── Phase 7: 前端适配
└── 全量测试 + 修复
```

---

## ✅ 验收标准

| 功能 | 测试方法 | 预期结果 |
|------|----------|----------|
| style 参数 | style=banfo 请求 | Writer 使用半佛样本 |
| length 控制 | length=short | 输出 300-600 字 |
| retention L1 | retention_level=1 | 输出与原文高度相似 |
| retention L5 | retention_level=5 | 仅保留主题，自由创作 |
| 排版专家 | 查看 polisher 输出 | 只改格式不改内容 |

---

**下一步**: 请确认是否开始执行，以及是否需要调整执行顺序。
