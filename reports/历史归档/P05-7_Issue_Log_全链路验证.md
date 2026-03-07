# Phase 9 问题记录 (Issue Log)

> **日期**: 2026-01-21
> **阶段**: Phase 9 全链路验证
> **状态**: 进行中

---

## 🔴 已发现问题

### Issue #1: API 端口配置错误 (已修复)
- **发现时间**: 00:04
- **症状**: Dashboard 显示 "System Offline"
- **根因**: `frontend/src/config/api.ts` 默认端口为 8002，后端实际运行在 8000
- **修复**: 将 `localhost:8002` 改为 `localhost:8000`
- **状态**: ✅ 已修复，待验证

### Issue #2: Browser Subagent CDP 连接失败
- **发现时间**: 23:45+
- **症状**: 所有浏览器自动化测试失败
- **错误**: `failed to connect to browser via CDP: target closed: EOF`
- **影响**: 无法自动验证 UI
- **状态**: ⚠️ 环境问题，非代码问题

### Issue #3: 知识库引擎状态始终 Offline
- **发现时间**: 23:58
- **症状**: Dashboard "知识库引擎" 卡片显示 Offline
- **根因**: 后端 `/health` 响应无 `lark_connected` 字段
- **建议**: 后端需添加 Lark 连接状态到 health 响应
- **状态**: 📋 待修复 (P2 优先级)

### Issue #4: C 盘磁盘空间不足
- **发现时间**: 10:39
- **症状**: npm install 失败，ENOSPC error
- **详情**: C 盘仅剩 10MB 空间，无法安装 Lighthouse 等工具
- **影响**: P3-5 Lighthouse 无法执行
- **建议**: 清理 C 盘或使用 Chrome DevTools 手动测试
- **状态**: ⚠️ 环境问题

---

## 🟡 待验证项

| 功能 | 预期 | 实际 | 状态 |
|------|------|------|------|
| Dashboard 后端状态 | Operational + 延迟 | 需手动验证 | ⏳ |
| Settings 后端同步 | 保存成功 toast | ✅ 通过 | ✅ |
| Knowledge Mock 数据 | 显示 3 条 | ✅ 通过 | ✅ |
| Agents 页面 | 4 个卡片 | 需手动验证 | ⏳ |
| Studio 全链路 | 分析→选策略→生成 | 未测试 | ❌ |

---

## 📊 测试覆盖

- **P0**: 2/2 已实现，1/2 已验证
- **P1**: 3/3 已实现，2/3 已验证
- **P2**: 0/2 未开始

---

## 📝 后续行动

1. [ ] 手动验证 Dashboard 后端状态显示
2. [ ] 手动验证 Agents 页面
3. [ ] 手动测试 Studio 全链路
4. [ ] 修复后端 `/health` 添加 `lark_connected` 字段
