# P10 执行计划评审报告

**日期**: 2026-01-29  
**评审对象**: `reports/design_docs/frontend_design/10-1_Exec_P10执行计划.md`

---

## ✅ 优点 (Strengths)

1. **结构清晰**: 按 Phase 0-7 分阶段执行，逻辑合理，依赖关系明确。
2. **粒度具体**: 包含具体的代码片段和修改位置，可执行性强。
3. **风险意识**: 识别了"数据流断裂"和"Lark迁移"等核心风险，并给出了防范措施。
4. **验收标准**: 每个阶段都有具体的验收检查点。

---

## ⚠️ 不足与改进建议 (Weaknesses & Recommendations)

### 1. Lark 多表架构迁移风险 (High)
**问题**: Phase 6 直接切换到 `_registry` 模式。如果 Lark 表结构未建立或 API 失败，整个系统将不可用。
**建议**: 
- **增加"兼容模式"**: `SyncService` 应实现降级逻辑：优先读 `_registry` → 失败则读硬编码的旧表 ID → 最后报错。
- **自动建表脚本**: 建议编写 `backend/scripts/init_lark_registry.py`，用于自动在 Lark 中创建元数据表结构，避免手动操作错误。

### 2. 前后端数据定义一致性 (Medium)
**问题**: 
- 后端使用 Snake Case (`retention_level`)，前端通常使用 Camel Case (`retentionLevel`)。
- `GenerateRequest` 新增字段需要确保有默认值，否则 Phase 1 上线后，旧版前端请求会报错 (422 Unprocessable Entity)。
**建议**: 
- 确认后端 Pydantic 模型字段均设有默认值（如 `style: str = "auto"`）。
- 在文档中明确前后端字段名的映射关系。

### 3. 缺乏自动化单元测试 (Medium)
**问题**: 验收标准依赖"打印日志"和"SSE 返回确认"，效率低且不可回归。
**建议**: 
- 在 Phase 1/3/5 增加具体的单元测试脚本 (e.g., `tests/test_length_logic.py`, `tests/test_retention_prompt.py`)。
- 验证 `calculate_length` 和 `prompt` 渲染逻辑是否符合预期，无需每次都调用 LLM。

### 4. Mode 与 Style 的具体边界
**问题**: "Quick Take" (快讯) 是一种 Mode，但它通常也暗示了一种 Style（严肃、简练）。如果用户选了 `mode="quick_take"` 但 `style="mimeng"`（情绪化、长故事），两者会冲突。
**建议**: 
- 在 Prompt 中明确 `mode` (结构) 优先级高于 `style` (语调)，或者在前端做互斥限制（不建议，增加复杂度）。
- 建议 Prompt 策略：结构跟随 Mode，用词跟随 Style。

---

## 🔧 修订后的执行建议

### 1. 补充 Scripts (Day 1)
建议在 Phase 0 增加以下脚本编写任务：
- `backend/scripts/test_p10_logic_unit.py`: 测试长度计算、保留度分支逻辑 (不调 LLM)。
- `backend/scripts/mock_lark_registry.py`: 本地模拟 Lark Registry 数据，用于开发阶段测试 Phase 6。

### 2. 调整 Phase 6 执行策略
建议分为两步：
- **Phase 6.1 (兼容层)**: 修改代码支持 Registry，但如果读取失败，回退到硬编码配置。
- **Phase 6.2 (迁移)**: 在 Lark 创建表，录入数据，验证 Registry 读取成功。
- **Phase 6.3 (切换)**: 关闭兼容层（可选）。

---

## 🏁 结论

**方案总体可行 (Pass with Suggestions)**。
建议在执行 Phase 6 (Lark) 时格外小心，并补充单元测试脚本以提高开发效率。
