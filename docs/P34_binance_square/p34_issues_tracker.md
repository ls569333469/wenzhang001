# P34 待优化和修复事项

> 整理于 2026-03-08，基于当天广场模式测试和数据链路验证

---

## 🔴 严重（必须修复）

### 1. 知识库引擎离线
- **现象**：仪表盘显示"知识库引擎 — 服务离线"，策略师报告 `Analyzing input with 0 reference(s)`
- **影响**：模型没有项目参考数据，完全依赖预训练知识，导致严重幻觉
- **原因**：本地 Chroma（`PersistentClient("./chroma_db/")`）未能启动或连接
- **修复方向**：排查 `chroma_service.py` 的初始化逻辑

### 2. 广场模式事实幻觉
- **现象**：输入 Fabric Foundation（机器人/ROBO），输出全是 Hyperledger Fabric（联盟链/IBM）
- **影响**：内容完全不可用，Critic 评分 0 分 REWRITE
- **原因**：
  - 知识库离线 → 无项目数据辅助
  - 提示词缺少"必须严格基于用户输入素材"的硬约束
- **修复方向**：
  1. 修复知识库连接
  2. 提示词中增加素材强绑定规则

---

## 🟡 重要（需要优化）

### 3. 广场提示词借鉴改写（8项）
- **状态**：借鉴清单已确定（[borrowing_plan.md](file:///C:/Users/ls569/.gemini/antigravity/brain/3b0a457d-30bc-4243-9f02-64f10eb520da/borrowing_plan.md)），未开始实施
- **涉及文件**：
  - `strategist/binance_square.jinja2` — 加入思维工具、约束示例、差异化规则
  - `writer/binance_square.jinja2` — 加入节奏规则、人味要求、禁词系统
  - `critic/binance_square.jinja2` — 新建，加入平台规则检测
- **相关文档**：
  - [prompt_side_by_side.md](file:///C:/Users/ls569/.gemini/antigravity/brain/3b0a457d-30bc-4243-9f02-64f10eb520da/prompt_side_by_side.md) — 三模式提示词对比
  - [prompt_comparison.md](file:///C:/Users/ls569/.gemini/antigravity/brain/3b0a457d-30bc-4243-9f02-64f10eb520da/prompt_comparison.md) — 详细分析

### 4. 短帖/长帖任务切换
- **需求**：广场模式需支持两种任务
  - 短帖：100-500 字（官方要求）
  - 长帖：500+ 字（官方要求）
- **当前状态**：只有统一的900字限制，没有区分
- **修复方向**：前端加切换器 + 后端 `mode_configs.py` 增加子类型

### 5. 必要标签自动注入
- **需求**：`#Mira $MIRA @账号` 等标签必须出现在生成内容中
- **当前状态**：没有标签注入机制
- **修复方向**：
  - 前端：手动标签输入框 + 自动匹配建议
  - 后端：提示词中注入必需标签列表
  - 限制：价格标签不超过3个

---

## 🟢 新功能（需要构建）

### 6. 项目知识库架构
- **目标**：为广场模式建立项目数据库，支持"选项目→自动读取知识→生成内容"
- **已验证的组件**：

| 组件 | 状态 | 数据 |
|------|------|------|
| Chroma Cloud (`xueqiu`) | ✅ 已连通 | fabric.foundation 官网 33 条 |
| 6551 Twitter API | ✅ 已连通 | @FabricFND 39 条推文 |
| 6551 News API | 🔲 未测试 | — |
| 项目元数据 | 🔲 未设计 | name/token/account/tags |

- **待建设**：
  1. 项目配置文件（JSON/SQLite）：存 name、token、account、tags、campaign
  2. 6551 数据 → Chroma Cloud 同步脚本
  3. 广场模式生成时自动查询 Chroma Cloud 获取素材
  4. 去重逻辑：新生成内容 vs 已发布内容

### 7. 6551 MCP 正式集成
- **已完成**：
  - opentwitter-mcp repo 已 clone 到 `d:\AI_Projects\2026001\opentwitter-mcp`
  - API Token 已存入 `.env`（`TWITTER_TOKEN`）
  - 直接 HTTP 调用验证通过
- **待做**：
  - 写 `twitter_6551_service.py` 封装 API 调用
  - 定时任务：每日自动拉取关注项目的最新推文
  - 存入 Chroma Cloud 对应 collection

### 8. Surf API 精确搜索优化
- **问题**：泛搜 "Fabric Foundation" 返回 Hyperledger Fabric 数据
- **方向**：搜索时加精确约束（`$ROBO @FabricFND`），或降低对 Surf 的依赖

---

## 📋 凭证清单

| 服务 | .env 变量 | 状态 |
|------|-----------|------|
| Chroma Cloud | `CHROMA_CLOUD_API_KEY` / `TENANT` / `DATABASE` | ✅ |
| 6551 Twitter | `TWITTER_TOKEN` (JWT) | ✅ |
| Binance Square | `BINANCE_SQUARE_API_KEY` | ✅ |
| Surf API | `SURF_API_KEY` | ✅ |
| Claude/DGrid | `ANTHROPIC_API_KEY` | ✅ |

---

## 📎 今日产出文件

| 文件 | 内容 |
|------|------|
| `reports/surf_test/fabricfnd_6551.md` | @FabricFND 39条推文（6551 API） |
| `reports/surf_test/robo_analysis.md` | ROBO 项目分析（Surf API） |
| `opentwitter-mcp/` | 6551 MCP 源码（已 clone） |
