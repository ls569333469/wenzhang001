# Google Sheets 替代 Lark 方案评估

**日期**: 2026-01-29  
**作者**: 晚班 (Claude)  
**状态**: 📋 方案评估 - 待白班审核

---

## 📊 执行摘要

| 维度 | 评估 |
|------|:----:|
| **可行性** | ✅ 完全可行 |
| **迁移工作量** | 中等 (~3-4 小时) |
| **风险等级** | 低 |
| **推荐程度** | ⭐⭐⭐⭐⭐ 强烈推荐 |

---

## 1️⃣ 问题背景

### 当前痛点
- Lark API 免费版有 **月度调用配额限制**
- 当前已耗尽，错误代码 `99991403`
- 影响：无法实时从 Lark 获取 Few-Shot 样本，依赖 fallback

### 现有架构
```
sync_service.py (216行)
├── sync_from_lark()     # 从 Lark 拉取待处理记录
├── get_samples()        # 按 style 获取样本 (核心接口)
├── load_library()       # 读取本地 JSON 缓存
└── save_library()       # 写入本地 JSON 缓存
```

**关键发现**: `get_samples()` 实际从本地 `style_library.json` 读取，Lark 仅用于同步更新。这大大降低了迁移复杂度。

---

## 2️⃣ Google Sheets vs Lark 对比

| 维度 | Lark (飞书) | Google Sheets | 优势方 |
|------|-------------|---------------|:------:|
| **免费配额** | 有月度限制 (已耗尽) | 300次/分钟，无月度限制 | 🏆 Google |
| **单表容量** | ~10万行 | 1000万单元格 (~50万行x20列) | 🏆 Google |
| **API 稳定性** | 良好 | 非常稳定 | 🏆 Google |
| **Python 库** | 自己封装 `lark_client` | `gspread` (6k+ GitHub Stars) | 🏆 Google |
| **认证方式** | Tenant Token (需刷新) | Service Account (永久) | 🏆 Google |
| **国内访问** | ✅ 无问题 | ⚠️ 需翻墙或代理 | ⚠️ Lark |
| **现有数据** | 已有 2W+ 条 | 需迁移 | - |

### ⚠️ 关键风险：网络访问

**中国大陆访问 Google API 需要代理**

解决方案：
1. 服务器部署在海外 (如 Vercel, Railway)
2. 使用代理配置 `HTTPS_PROXY` 环境变量
3. 使用 Google Cloud 的中国区域镜像 (有限支持)

---

## 3️⃣ 技术实现方案

### 3.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      SyncService v2                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   DataSourceInterface                    │ │
│  │  get_samples(style, count) → List[Dict]                 │ │
│  │  sync_new_records() → int                               │ │
│  └─────────────────────────────────────────────────────────┘ │
│              ▲                           ▲                   │
│              │                           │                   │
│  ┌───────────┴───────────┐   ┌──────────┴──────────┐       │
│  │   LarkDataSource      │   │  GoogleSheetsSource │       │
│  │   (现有实现)          │   │  (新增实现)         │       │
│  └───────────────────────┘   └─────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Google Sheets 表结构

**Spreadsheet**: `Quantum_Samples`

| Sheet Name | 对应 Style | 预计行数 |
|------------|-----------|:--------:|
| mimeng | 咪蒙体 | ~12,000 |
| banfo | 半佛仙人体 | ~8,000 |
| xinshixiang | 新世相体 | ~3,000 |
| ... | ... | ... |
| _registry | 元数据表 | ~10 |

**`_registry` Sheet 结构**:
| style_id | style_name | row_count | last_sync | status |
|----------|------------|:---------:|-----------|--------|
| mimeng | 咪蒙体 | 12345 | 2026-01-29 | enabled |
| banfo | 半佛仙人体 | 8901 | 2026-01-29 | enabled |

### 3.3 核心代码实现

```python
# backend/app/services/google_sheets_source.py

import gspread
from google.oauth2.service_account import Credentials
import random
from typing import List, Dict

class GoogleSheetsDataSource:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, credentials_path: str, spreadsheet_name: str):
        creds = Credentials.from_service_account_file(credentials_path, scopes=self.SCOPES)
        self.gc = gspread.authorize(creds)
        self.spreadsheet = self.gc.open(spreadsheet_name)
        self._cache = {}  # 内存缓存，减少 API 调用
    
    def get_samples(self, style: str, count: int = 3) -> List[Dict]:
        """从对应 Sheet 获取随机样本"""
        if style not in self._cache:
            try:
                worksheet = self.spreadsheet.worksheet(style)
                self._cache[style] = worksheet.get_all_records()
            except gspread.exceptions.WorksheetNotFound:
                return []
        
        records = self._cache[style]
        if not records:
            return []
        
        return random.sample(records, min(count, len(records)))
    
    def refresh_cache(self, style: str = None):
        """刷新缓存（可选指定 style）"""
        if style:
            self._cache.pop(style, None)
        else:
            self._cache.clear()
```

### 3.4 配置文件

```python
# .env 新增
SAMPLE_SOURCE=google_sheets  # 或 lark, local
GOOGLE_SHEETS_CREDENTIALS=config/google_service_account.json
GOOGLE_SHEETS_SPREADSHEET=Quantum_Samples
```

---

## 4️⃣ 迁移步骤

### Phase A: 准备 (30分钟)
1. 创建 Google Cloud 项目
2. 启用 Google Sheets API
3. 创建 Service Account，下载 JSON 密钥
4. 创建 Google Spreadsheet，共享给 Service Account

### Phase B: 数据迁移 (1小时)
1. 从 Lark 导出数据为 CSV
2. 导入到 Google Sheets 各 Sheet
3. 验证数据完整性

### Phase C: 代码实现 (2小时)
1. 安装依赖：`pip install gspread google-auth`
2. 实现 `GoogleSheetsDataSource` 类
3. 修改 `SyncService` 支持多数据源切换
4. 添加环境变量配置

### Phase D: 测试验证 (30分钟)
1. 单元测试 `get_samples()` 
2. 集成测试完整 Writer 流程
3. 性能测试（首次加载 vs 缓存加载）

---

## 5️⃣ 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:----:|:----:|----------|
| 国内无法访问 Google | 高 | 高 | 部署到海外服务器，或配置代理 |
| API 速率限制 (300/分钟) | 低 | 低 | 本地缓存 + 批量读取 |
| 数据格式不兼容 | 低 | 中 | 导入前验证字段映射 |
| Service Account 密钥泄露 | 低 | 高 | 加入 .gitignore，使用环境变量 |

---

## 6️⃣ 替代方案对比

| 方案 | 工作量 | 长期可持续性 | 网络依赖 |
|------|:------:|:------------:|:--------:|
| **Google Sheets** | 中 | ⭐⭐⭐⭐⭐ | 需翻墙 |
| 本地 JSON 文件 | 低 | ⭐⭐⭐ | 无 |
| Notion API | 中 | ⭐⭐⭐⭐ | 国内可用 |
| Airtable | 中 | ⭐⭐⭐⭐ | 国内可用 |
| 自建数据库 (SQLite) | 中 | ⭐⭐⭐⭐⭐ | 无 |

---

## 7️⃣ 推荐决策

### 如果服务器在海外 → ✅ 使用 Google Sheets
- 配额充足，免费
- 生态成熟，`gspread` 库稳定
- 与现有 Google Cloud 服务集成良好

### 如果服务器在国内 → 🟡 考虑 Notion 或 Airtable
- 无需翻墙
- API 配额也较宽松

### 如果追求零依赖 → ✅ 使用本地 JSON + 定期手动更新
- 已有 `style_library.json` 机制
- 完全离线，无网络风险

---

## ✅ 下一步行动

~~请白班同事确认：~~
~~1. **服务器部署环境**：海外还是国内？~~
~~2. **是否接受 Google Sheets 方案**？~~
~~3. **如接受**：是否已有 Google Cloud 项目和 Service Account？~~

**✅ 已确认**: 用户已有 Google Cloud，服务器部署海外/香港。方案已批准。

---

## 🚀 执行指南 (用户操作步骤 - 中文界面)

### Step 1: 创建服务账号 (10分钟)

1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 在顶部选择您的项目 (如截图中的 `fangxie002`)
3. 左侧菜单导航: `IAM和管理` → `服务账号` → 点击顶部 `+ 创建服务账号`
4. 填写:
   - **服务账号名称**: `quantum-sheets-reader`
   - **服务账号说明**: `Quantum Studio 样本数据只读访问`
5. 点击 `创建并继续`
6. **授予对项目的访问权限**: 跳过 (我们只读 Sheets，无需特殊角色)
7. 点击 `完成`

### Step 2: 下载密钥 JSON (2分钟)

1. 在服务账号列表中，点击刚创建的 `quantum-sheets-reader` 账号
2. 点击顶部的 `密钥` 标签页
3. 点击 `添加密钥` → `创建新密钥` → 选择 `JSON`
4. 浏览器会自动下载一个 `.json` 文件
5. 将文件重命名并保存到项目目录:
   ```
   backend/config/google_service_account.json
   ```

### Step 3: 启用 Google Sheets API (2分钟)

1. 在左侧菜单点击 `API和服务` → `已启用的API和服务`
2. 点击顶部 `+ 启用API和服务`
3. 搜索 `Google Sheets API`
4. 点击进入后，点击 `启用`

### Step 4: 创建 Google Spreadsheet (5分钟)

1. 打开 [Google 表格](https://sheets.google.com/)
2. 点击 `+` 创建新的空白表格
3. 点击左上角 "无标题的电子表格" 重命名为: `Quantum_Samples`
4. 在底部 Sheet 标签处右键 → `插入工作表`，创建以下工作表:
   - `mimeng` (咪蒙体样本)
   - `banfo` (半佛仙人体样本)
   - `_registry` (元数据)

### Step 5: 共享给服务账号 (2分钟)

1. 在 Spreadsheet 右上角点击 `共享`
2. 在 "添加用户和群组" 输入框中，粘贴服务账号邮箱:
   ```
   quantum-sheets-reader@您的项目ID.iam.gserviceaccount.com
   ```
   *(邮箱可在 Google Cloud Console → 服务账号列表 → "电子邮件" 列复制)*
3. 权限下拉选择 `查看者`
4. 取消勾选 "通知用户" (服务账号不需要邮件通知)
5. 点击 `共享`

### Step 6: 导入现有数据 (可选)

如果需要迁移现有 Lark 数据:
1. 从 Lark 导出表格为 CSV 文件
2. 在 Google 表格中: `文件` → `导入` → `上传` → 选择 CSV 文件
3. 选择 "替换当前工作表" 并点击 `导入数据`

---

## 📋 配置完成清单

完成后请确认:

- [ ] Service Account JSON 已保存到 `backend/config/google_service_account.json`
- [ ] Google Spreadsheet `Quantum_Samples` 已创建
- [ ] Spreadsheet 已共享给 Service Account
- [ ] (可选) 数据已导入

**确认后回复"配置完成"，Agent 将开始代码实现。**

---

**备注**: 此方案与 P10 Phase 6 (多表 Lark 架构) 目标一致，可视为 Phase 6 的替代实现。
