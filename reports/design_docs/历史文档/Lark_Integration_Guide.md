# 🦅 Lark (飞书国际版) 素材库集成手册

本文档指导您如何从零开始，搭建基于 Lark Base 的 Web3 投研素材库，并将其与 AI 写作系统对接。

---

## 第一阶段：注册与建表 (Lark Setup)
> **目标**: 拥有一个云端可用的素材数据库。

1.  **注册 Lark**
    *   访问 [larksuite.com](https://www.larksuite.com/)。
    *   使用邮箱注册（建议用 Gmail/Outlook，不要用国内手机号注册飞书国内版，账号不互通）。
    *   下载 Lark App (PC/手机端)。

2.  **创建素材库 (Base)**
    *   在 Lark 主界面，点击左侧 "Base" (多维表格)。
    *   新建一个 Base，命名为 `Cortex_Materials` (或者您喜欢的名字)。
    *   将默认表格重命名为 `Snippets`。

3.  **配置字段 (Columns)**
    请严格按照下表设置字段名和类型（程序将读取这些字段名）：

| 字段名 (Field Name) | 字段类型 (Field Type) | 选项值例子 (Options) |
| :--- | :--- | :--- |
| **内容** | 多行文本 | (长文/片段) |
| **作者** | 单选 | `咪蒙`, `小侠`, `分析师A` |
| **风格** | 单选 | `咪蒙风`, `内幕风`, `小红书风` |
| **类型** | 单选 | `开头`, `金句`, `数据`, `结尾` |
| **状态** | 单选 | `待处理`, `已同步` |

**✅ 您完全可以使用中文命名！**
无论是表名（如`素材收纳箱`）、字段名（如`内容`）还是选项值（如`咪蒙风`），**都可以用中文**。
我写的 Python 程序会自动识别它们，您怎么舒服怎么来。

    > **💡 Tip**: 您可以先随便录入一条测试数据，例如：
    > *   Content: "Web3 最大的谎言也就是..."
    > *   Style: `mimeng`
    > *   Status: `Pending`

---

## 第二阶段：开放平台配置 (API Setup)
> **目标**: 获取 App ID 和 App Secret，让代码能读写表格。

1.  **创建自建应用**
    *   **如果您用的是飞书 (国内版)**: 访问 [open.feishu.cn/app](https://open.feishu.cn/app?lang=zh-CN)
    *   **如果您用的是 Lark (国际版)**: 访问 [open.larksuite.com/developers](https://open.larksuite.com/developers)
    *   点击 "创建企业自建应用" (Create Custom App)。
    *   名称: `Writer_Bot`，描述: `Sync materials to AI`。

2.  **开启权限 (Scopes)**
    *   进入应用详情页 -> "Permissions & Scopes" (权限管理)。
    *   在搜索框输入 **"多维表格"** (或者 **"Bitable"**)。
    *   勾选以下核心权限（中文名称可能略有不同，认准“读写”即可）：
        *   ✅ **查看多维表格** (`bitable:app:read`)
        *   ✅ **编辑多维表格** (或 **管理多维表格**) (`bitable:app:write` / `bitable:record:write`)
        *   (如果找不到具体的，就勾选带有 "编辑" 或 "管理" 字样的多维表格权限)
    *   **重要**: 勾选后，点击页面上方的 "Create Version" (创建版本) -> "Publish" (发布)，**否则权限不会生效**！

3.  **获取凭证 (Credentials)**
    *   进入 "Credentials & Basic Info"。
    *   **App ID**: `cli_xxxxxx`
    *   **App Secret**: `xxxxxxxx`
    *   👉 **请记录这两个值，稍后填入后端配置。**

4.  **添加机器人到表格**
    *   回到第一阶段创建的 `Cortex_Materials` 表格页面。
    *   点击右上角 "..." (更多) -> "Add Custom App"。
    *   搜索 `Writer_Bot` 并添加。

---

## 第三阶段：获取 Table ID
> **目标**: 告诉程序去读哪张表。

1.  在浏览器打开您的 Base 表格。
2.  观察 URL 结构：
    `https://YourOrg.larksuite.com/base/bascnXXXXXXXXXX?table=tblYYYYYYYYYY`
3.  提取关键 ID：
    *   **App Token (Base ID)**: `bascnXXXXXXXXXX` (从 `base/` 后开始，到 `?` 前)
    *   **Table ID**: `tblYYYYYYYYYY` (从 `table=` 后开始)

---

## 第四阶段：后端代码集成 (Backend Integration)
> **目标**: 更新 `task.md`，准备接下来的 P8 开发。

**只需要您提供以下 4 个值，后续代码开发交给我：**
1.  `LARK_APP_ID`
2.  `LARK_APP_SECRET`
3.  `LARK_BASE_TOKEN`
4.  `LARK_TABLE_ID`

---

### 🎉 操作流 (Future Workflow)

一切配置好后，您的日常工作流变为：
1.  **刷推特/看研报** -> 看到好句子 -> **复制到 Lark 表格** -> 打标 `Pending`。
2.  (AI 自动运行) -> 后端每 10 分钟拉取 `Pending` 数据 -> 存入内存 -> 自动把表格状态改为 `Synced`。
3.  **写文章** -> Writer Agent 自动从内存中调用最新的素材。

**准备好相关 ID 后，请告诉我，我将更新后端配置。**
