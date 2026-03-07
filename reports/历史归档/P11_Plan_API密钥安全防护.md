# API 密钥安全防护方案

**日期**: 2026-01-28  
**状态**: 执行中

---

## ✅ 已完成的防护措施

| 措施 | 状态 | 说明 |
|------|:----:|------|
| `.gitignore` 规则 | ✅ | 已包含 `user_config.json`、`.env` 等 |
| 代码残留检查 | ✅ | 搜索 `AIzaS`, `sk-` 等模式无结果 |
| Git 缓存清理 | ✅ | `user_config.json` 不在 tracked 文件中 |
| 模板文件 | ✅ | 已创建 `user_config.example.json` |

---

## 📋 建议增加的防护措施

### 1. Git Pre-commit Hook（推荐）

自动阻止包含敏感信息的提交：

**创建文件**: `.git/hooks/pre-commit`
```bash
#!/bin/sh
# 检测敏感信息模式
PATTERNS="AIzaS|sk-[a-zA-Z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN.*PRIVATE KEY"

if git diff --cached | grep -E "$PATTERNS"; then
    echo "❌ 检测到可能的敏感信息！提交已阻止。"
    echo "请检查并移除 API 密钥后重试。"
    exit 1
fi
```

**Windows PowerShell 版本** (`.git/hooks/pre-commit.ps1`):
```powershell
$diff = git diff --cached
if ($diff -match "AIzaS|sk-|AKIA|-----BEGIN") {
    Write-Host "❌ 检测到敏感信息！" -ForegroundColor Red
    exit 1
}
```

### 2. 环境变量替代硬编码

将 API 密钥从配置文件迁移到环境变量：

**`.env` 文件**（本地使用，已在 gitignore 中）:
```
GEMINI_API_KEY=AIzaSy...
DOUBAO_API_KEY=1370f27c...
```

**代码读取**:
```python
import os
gemini_key = os.getenv("GEMINI_API_KEY")
```

### 3. 密钥轮换提醒

在 `PROJECT_HANDBOOK.md` 中添加定期轮换提醒：
- 每季度轮换一次 API 密钥
- 发现泄露后立即轮换

---

## 📊 当前安全状态

```
安全等级: ████████░░ 80%

✅ .gitignore 防护
✅ 代码无残留密钥
✅ 模板文件已创建
⚠️ Pre-commit hook 未安装
⚠️ 未使用环境变量
```

---

## 🔧 下一步行动

| 优先级 | 任务 | 工作量 |
|:------:|------|:------:|
| P1 | 安装 pre-commit hook | 5分钟 |
| P2 | 迁移到环境变量 | 30分钟 |
| P3 | 添加密钥轮换提醒到手册 | 10分钟 |

---

**是否需要我立即安装 Pre-commit Hook？**
