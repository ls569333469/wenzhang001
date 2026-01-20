# Phase 7: 全链路深度测试计划与报告 (Deep System Verification)

> **任务目标**: 验证前端与后端在"Mimeng Style (from Lark)" + "Web3 DAO Data (from Lark)" 场景下的协同工作能力。
> **测试素材**: JustLend DAO 销毁数据。

---

## 1. 测试策略 (Test Strategy)

由于前端尚未部署 Mimeng 风格选项，我们将利用 **Phase 6 开发的 Prompt Injection 特性** 来模拟此需求。

### 1.1 输入构造 (Input Construction)
- **User Input**: 
  ```text
  JustLend DAO 已通过两阶段系统性回购销毁机制，累计完成 1,084,890,753 枚 JST 的销毁... (用户提供的完整文本)
  ```
- **Prompt Injection (Frontend Layer)**:
  我们将模拟前端 `injectPrompts` 函数的行为，构造带有 `[SYSTEM OVERRIDE]` 前缀的最终 Payload。
  - **Strategist**: "Analyze this as a Web3 Data Report."
  - **Writer**: "Role: Mimeng (咪蒙). Style: Emotional, provocative, short sentences. Use 'KV' language. Focus on 'Transparency' and 'Value'."
  - **Context**: Connect to Lark Web3 Data (via Backend RAG).

### 1.2 验证路径 (Verification Path)
1.  **Backend Connectivity**: 运行 `test_lark_connection.py` 确认 Lark 连接。
2.  **API Simulation**:
    -   **Step 1 (/analyze)**: 发送 Payload，验证 Strategist 是否能识别 Mimeng 风格要求并提取 "JustLend" 相关 Anchors。
    -   **Step 2 (/generate)**: 发送带有 `selected_option` 的请求，验证 Writer 是否生成了 Mimeng 风格的中文文章。
3.  **Result Analysis**: 检查输出是否包含 "JustLend", "10.96%" 等关键数据，且语气是否符合 Mimeng 风格。

---

## 2. 预检报告 (Pre-Flight Check)

- [ ] **Lark Connection**: (待运行 `test_lark_connection.py`)
- [ ] **Backend Service**: (假设已运行，通过 Curl 验证)

---

## 3. 执行日志 (Execution Log)

### 3.1 Backend Lark Check
- **Command**: `python backend/test_lark_connection.py`
- **Result**: ✅ Success. Token retrieved.

### 3.2 Simulation Results
- **Tools**: `test_analyze_request.py` (Step 1), `test_generate_request.py` (Step 2)
- **Step 1 (Analyze)**: 
  - **Status**: ✅ Success
  - **Output**: [analysis_result.json](file:///d:/AI_Projects/2026001/backend/analysis_result.json)
  - **Observations**: Successfully identified "JustLend" anchors. Generated 3 valid options.
- **Step 2 (Generate)**:
  - **Status**: ✅ Success
  - **Selected Option**: "Fear of Missing Out" (Option 1)
  - **Output**: [generation_result.md](file:///d:/AI_Projects/2026001/backend/generation_result.md)
  - **Observations**: 
    - Data Accuracy: Perfect (1,084,890,753 JST, 10.96%).
    - Style: High match (Used terms like "FOMO", "Diamond Hands", "Ngmi").
    - Workflow: Writer -> Critic (Reject) -> Writer (Revise) -> Critic (Approve) -> Lark Archive (Success).

## 4. 结论 (Conclusion)
系统在"Prompt Injection"模式下表现优异，成功打通了 Lark 数据源与深度思考工作流。虽然前端 UI 尚未直接暴露 Mimeng 风格，但后端能力已完全就绪。前端通过 `injectPrompts` 可以无缝对接此能力。

**Verdict**: **PASS** ✅
