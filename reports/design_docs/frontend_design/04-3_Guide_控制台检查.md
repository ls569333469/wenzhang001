# Console 检查指南 (人工执行)

## 📋 前置条件

确保以下服务已启动：

```powershell
# 终端 1: 启动后端
cd d:\AI_Projects\2026001\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8002
```

```powershell
# 终端 2: 启动前端
cd d:\AI_Projects\2026001\frontend
npm run dev
```

---

## 🔍 检查步骤

### Step 1: 打开页面
1. 浏览器访问 `http://localhost:3000/studio`
2. 等待页面完全加载

### Step 2: 打开开发者工具
1. 按 `F12` 或右键 → 检查
2. 点击 **Console** 面板
3. 刷新页面 (`Ctrl+R`)

### Step 3: 检查错误

| 类型 | 严重程度 | 处理方式 |
|------|----------|----------|
| 🔴 红色 Error | **必须修复** | 记录错误信息和文件位置 |
| 🟡 黄色 Warning | 建议修复 | 特别关注 "key" 相关警告 |
| 🔵 蓝色 Info | 可忽略 | 一般为开发提示 |

### Step 4: 记录问题

如发现错误，请复制以下信息：
1. 错误消息全文
2. 文件名和行号 (如 `ConfigPanel.tsx:251:9`)
3. 堆栈跟踪 (点击展开)

---

## ❌ 已知问题 (可忽略)

以下错误属于正常现象：

| 错误 | 原因 |
|------|------|
| `ERR_CONNECTION_REFUSED :8002` | 后端未启动 |
| `WebSocket connection failed` | HMR 热更新断开，重启 dev server |
| `contentEditable` 警告 | React 已知问题 |

---

## ✅ 预期结果

| 检查项 | 预期 |
|--------|------|
| 红色 Error | 0 条 (后端启动后) |
| 黄色 Warning | ≤ 2 条 (contentEditable 可忽略) |
| 页面加载 | 正常显示 Studio 布局 |
