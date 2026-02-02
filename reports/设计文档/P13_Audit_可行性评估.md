# 综合审计清单可行性评估

**评估日期**: 2026-01-31  
**评估人**: Antigravity  
**项目规模**: ~15k 行代码 (backend ~10k + frontend ~5k)

---

## 📊 审计清单可行性总览

| # | 审计类别 | 可行性 | 当前具备 | 缺失条件 | 建议 |
|---|----------|:------:|:--------:|----------|------|
| 1 | 输出质量 & 一致性 | ⚠️ **部分** | 单模型测试 | 多文体/多语言样本集 | 分阶段执行 |
| 2 | 多 Agent 协作稳定性 | ✅ **可行** | LangGraph 链路 | trace 日志完善 | 立即可做 |
| 3 | Prompt 注入 & 安全 | ⚠️ **部分** | 基础调用 | 无输入过滤/moderation | 需先补防护 |
| 4 | 性能 & 压力测试 | ⚠️ **部分** | 单次调用 | 无并发/监控工具 | 需工具准备 |
| 5 | 多模型路由 & 一致性 | ✅ **可行** | 3模型配置 | 路由规则文档 | 立即可做 |
| 6 | 代码健康 & 技术债 | ✅ **可行** | 代码库完整 | 无静态分析工具 | 可用工具扫描 |

---

## 🔍 逐项详细评估

### 1️⃣ 输出质量 & 一致性审计

**目标**: 多文体、中英文、三模型对比 + ROUGE/BERTScore

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| 多文体覆盖 | 仅有 Web3 项目评论 (mimeng/banfo) | ❌ 无其他文体样本 |
| 中英文 | 仅中文 | ❌ 无英文测试 |
| 三模型对比 | Gemini/DeepSeek/Doubao 均已配置 | ✅ |
| ROUGE/BERTScore | 需安装 evaluate 库 | ⚠️ 可快速添加 |
| 风格一致性评分 | P12 已有 5 维度评分 | ✅ |
| 幻觉/风格漂移检测 | 无自动检测 | ❌ |

**🔴 阻塞点**: 
- 缺少多文体样本集 (新闻/小说/营销/技术/社交)
- 缺少英文测试数据

**建议**: 
```
Phase 1: 先用现有 Web3 素材跑三模型对比 (可立即执行)
Phase 2: 后续补充多文体样本集
Phase 3: 添加 ROUGE/BERTScore 自动评测
```

**预估工时**: Phase 1 = 4h, Phase 2 = 8h, Phase 3 = 4h

---

### 2️⃣ 多 Agent 协作链路稳定性 ✅ 可行

**目标**: 100+ 次模拟，检查消息传递/状态同步/错误传播

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| Agent 链路定义 | LangGraph `graph.py` 已完整 | ✅ |
| 状态同步 | AgentState TypedDict | ✅ |
| 错误传播 | try-except 覆盖 | ⚠️ 部分 |
| 降级机制 | 无明确 fallback | ❌ |
| trace 日志 | print 语句散落 | ⚠️ 需统一 |

**当前链路**:
```
Strategist → [用户选择] → Writer → Critic → (Polisher) → 输出
```

**可立即执行**:
```python
# 创建批量测试脚本
for i in range(100):
    try:
        result = app_graph.invoke(test_inputs[i % len(test_inputs)])
        log_result(i, "SUCCESS", result)
    except Exception as e:
        log_result(i, "FAILED", str(e))
```

**预估工时**: 6h (含 trace 日志完善)

---

### 3️⃣ Prompt 注入 & 安全检查 ⚠️ 部分可行

**目标**: jailbreak 测试，输入过滤，moderation

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| Prompt 模板 | jinja2 固定结构 | ✅ 相对安全 |
| 输入过滤 | ❌ **无** | 🔴 需补充 |
| 输出审查 | ❌ **无** | 🔴 需补充 |
| Moderation API | 未集成 | 🔴 需补充 |

**风险点**:
```python
# main.py L81 - 用户输入直接进入 LLM
input: str  # ← 无过滤

# agents/strategist.py - 直接拼接用户输入
context["raw_input"] = inputs.get("raw_input", "")  # ← 无过滤
```

**建议执行顺序**:
1. 先添加基础输入过滤 (XSS, SQL注入模式)
2. 再进行 jailbreak 测试
3. 最后集成 Moderation API

**预估工时**: 8h (含防护实施)

---

### 4️⃣ 性能 & 压力测试 ⚠️ 部分可行

**目标**: 并发 20-50, 2小时连续运行, 监控资源

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| 单次延迟测试 | 可用 time.time() | ✅ |
| 并发测试 | 需 locust/k6 工具 | ⚠️ 需安装 |
| 内存监控 | 无 | ⚠️ 需 memory_profiler |
| LLM 延迟监控 | 无 | ⚠️ 需添加 |
| 长时运行 | 可执行 | ✅ |

**已知瓶颈**:
- Strategist (Gemini): ~5-10s
- Writer (DeepSeek): ~15-30s  ← 最慢
- Critic (Doubao): ~3-5s

**建议工具**:
```bash
pip install locust memory_profiler
# 或
npm install -g k6
```

**预估工时**: 6h (含工具配置 + 基准测试)

---

### 5️⃣ 多模型路由 & 一致性 ✅ 可行

**目标**: 相同输入三模型对比，路由规则合理性

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| 多模型配置 | user_config.json 支持 | ✅ |
| 路由规则 | 硬编码在 Agent 中 | ⚠️ 需文档化 |
| 输出一致性测试 | 无 | ⚠️ 需添加 |

**当前路由逻辑**:
```
Strategist → Google Gemini (推理能力强)
Writer     → DeepSeek V3 (中文写作)
Critic     → Doubao 1.5 Pro (评分稳定)
Polisher   → Doubao 1.5 Pro (润色)
```

**可立即执行**:
```python
# 对比测试脚本
models = ["gemini", "deepseek", "doubao"]
for model in models:
    output = generate_with_model(same_input, model)
    save_for_comparison(model, output)
```

**预估工时**: 4h

---

### 6️⃣ 代码健康 & 技术债扫描 ✅ 可行

**目标**: 重复代码, God functions, 类型隐患, 依赖漏洞

| 子项 | 项目现状 | 可行性 |
|------|----------|:------:|
| 代码量 | ~15k 行 | ✅ 可扫描 |
| TypeScript 类型 | tsconfig strict=false | ⚠️ 有隐患 |
| Python 类型 | 部分 type hints | ⚠️ 不完整 |
| 依赖漏洞 | 未检查 | ⚠️ 需扫描 |

**可用工具**:
```bash
# Python
pip install pylint radon bandit
pylint app/ --output-format=json > lint_report.json
radon cc app/ -j > complexity.json
bandit -r app/ -f json > security.json

# TypeScript/JS
npm audit
npx eslint src/ --format json > eslint_report.json
```

**已知 Code Smell**:
- `main.py` 897 行 - God File
- 重复的 try-except 模式
- 硬编码配置值

**预估工时**: 4h (扫描 + 报告)

---

## 📅 推荐执行顺序

| 优先级 | 审计项 | 工时 | 理由 |
|:------:|--------|:----:|------|
| 🔴 1 | 代码健康扫描 | 4h | 快速发现问题，无依赖 |
| 🔴 1 | 多 Agent 稳定性 | 6h | 核心功能验证 |
| 🟡 2 | 多模型路由一致性 | 4h | 已有配置可直接测 |
| 🟡 2 | 输出质量 Phase 1 | 4h | 用现有素材 |
| 🟠 3 | 性能压测 | 6h | 需工具准备 |
| 🟠 3 | 安全检查 | 8h | 需先补防护 |
| **合计** | - | **32h** | - |

---

## ✅ 立即可执行清单

| # | 任务 | 命令/操作 |
|---|------|----------|
| 1 | 代码复杂度扫描 | `pip install radon && radon cc app/ -a` |
| 2 | 依赖漏洞检查 | `pip audit` / `npm audit` |
| 3 | 三模型同输入对比 | 修改 user_config 切换模型 |
| 4 | 100 次链路测试 | 编写批量脚本 |

---

## ❌ 暂不可执行 (需先补充)

| # | 审计项 | 缺失条件 |
|---|--------|----------|
| 1 | 多文体测试 | 无新闻/小说/营销样本 |
| 2 | 英文测试 | 无英文数据 |
| 3 | Jailbreak 测试 | 需先加输入过滤 |
| 4 | 并发压测 | 需安装 locust/k6 |
