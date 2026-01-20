# 🛠️ 素材库集成技术方案 (Feishu vs Notion)

本文档详细描述了如何将 **飞书多维表格 (Lark Base)** 或 **Notion Database** 集成到我们的 AI 写作系统中，实现素材的自动化同步。

---

## 🟢 方案 A：飞书多维表格 (Lark Base)
> **推荐指数**: ⭐⭐⭐⭐⭐ (国内访问最快，API 极其稳定)

### 1. 数据库设计 (Schema)
在飞书多维表格中新建一个名为 `AI素材库` 的数据表（Base），包含以下字段：

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| **Content** | 多行文本 | ✅ | 素材正文 (建议 <300字) |
| **Author** | 单选 | ✅ | 来源博主 (如: 咪蒙, 交易员小侠) |
| **Style** | 单选 | ✅ | 风格映射 (如: `mimeng`, `insider`, `xiaohongshu`) |
| **Type** | 单选 | ✅ | 用途 (如: `Hook/开头`, `Quote/金句`, `Ending/结尾`) |
| **Emotion** | 单选 | ❌ | 情绪标签 (如: `焦虑`, `FOMO`, `爽感`) |
| **Status** | 单选 | ✅ | 状态流转 (`待同步` -> `已同步`) |
| **LastUpdated** | 修改时间 | - | 系统自动记录 |

### 2. 集成流程 (Workflow)

1.  **创建应用**: 在 [飞书开放平台](https://open.feishu.cn/) 创建一个企业自建应用 "Writer Assistant"。
2.  **获取权限**: 开启 `bitable:app:read` (读取多维表格) 和 `bitable:app:update` (更新记录) 权限。
3.  **获取 App Token & Table ID**: 打开多维表格，URL 中获取。
4.  **Python 后端逻辑 (`app/services/feishu_sync.py`)**:
    *   **Step 1**: 定时请求飞书 API `GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`。
    *   **Step 2**: 筛选条件 `filter = AND(CurrentValue.[Status]="待同步")`。
    *   **Step 3**: 获取记录后，将其转换为 JSON 存入 `backend/data/style_library.json`。
    *   **Step 4**: 调用 API `PUT` 回写，将这些记录的 `Status` 更新为 `已同步`。

### 3. 数据样例 (JSON Payload)
```json
{
  "fields": {
    "Content": "大厂抛弃你的时候，连一声招呼都不打...",
    "Author": "咪蒙",
    "Style": "mimeng",
    "Type": "Hook",
    "Status": "已同步"
  }
}
```

---

## 🔵 方案 B：Notion Database
> **推荐指数**: ⭐⭐⭐⭐ (全球化首选，但国内 API 偶尔有网络波动)

### 1. 数据库设计 (Schema)
在 Notion 中新建一个 Database `Material Bank`，Property 设置如下：

| Property Name | Type | Options (Select) |
| :--- | :--- | :--- |
| **Name** (Title) | Text | (素材简述) |
| **Full Content** | Text | (正文内容) |
| **Tags** | Multi-select | `mimeng`, `crypto` |
| **Category** | Select | `Opening`, `Body`, `Ending` |
| **Sync Status** | Status | `Not Synced`, `Synced` |

### 2. 集成流程 (Workflow)

1.  **创建 Integration**: 在 [Notion Developers](https://www.notion.so/my-integrations) 创建 "AI Sync Bot"。
2.  **分享数据库**: 在 Notion 页面右上角 Share，邀请该 Bot 编辑。
3.  **Python 后端逻辑 (`app/services/notion_sync.py`)**:
    *   **Step 1**: 请求 `POST https://api.notion.com/v1/databases/{database_id}/query`。
    *   **Step 2**: Body 指明 filter: `{"property": "Sync Status", "status": {"equals": "Not Synced"}}`。
    *   **Step 3**: 解析复杂的 Notion Block 结构（注意：Notion 的 Rich Text 解析较飞书麻烦）。
    *   **Step 4**: 更新 Page 属性，标记为 Synced。

---

## ⚖️ 深度对比 (Pros & Cons)

| 维度 | 飞书 (Feishu/Lark) | Notion |
| :--- | :--- | :--- |
| **API 速度** | 🚀 极快 (国内服务器) | 🐢 较慢 (需科学网络) |
| **结构化程度** | ⭐⭐⭐⭐⭐ (多维表格原生支持 API) | ⭐⭐⭐⭐ (Database 也很强) |
| **数据解析难度** | ✅ 简单 (直接返回 Value) | ⚠️ 复杂 (返回 Block 对象) |
| **手机端体验** | ✅ 微信级体验，秒开 | ⚠️ 启动略慢 |
| **AI 扩展性** | ✅ 自带飞书 AI 列 (自动打标) | ✅ Notion AI (需付费) |

## 📢 最终建议
对于 **Web3 投研 + 国内自媒体** 场景，**飞书** 是绝对的首选。
1.  **不丢包**: 国内网络直连。
2.  **团队协作**: 如果您以后有助理帮忙从推特搬运素材，飞书的权限管理更符合国人习惯。
