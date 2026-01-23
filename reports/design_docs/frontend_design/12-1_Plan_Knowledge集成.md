# 12-1 Strategist 集成 Knowledge_Repo 执行计划

> **目标**: 让 Strategist 从 Knowledge_Repo 检索 Web3 知识，传递给 Writer，Critic 审核准确性  
> **方案**: Feature Flag 方式，新旧流程共存  
> **预估工时**: ~1.5 小时

---

## 流程对比

### 当前流程 vs 建议新流程

```
当前流程:                              建议新流程:
                                       
用户输入主题                           用户输入主题
    ↓                                      ↓         ┌──────────────┐
策略师                                 策略师  ←───  │Knowledge_Repo│
(策略+爆款标题)                        (策略+标题+Web3上下文)  └──────────────┘
    ↓                                      ↓
🔸 选择您的角度                        🔸 选择您的角度
    ↓                                      ↓         传递Web3上下文
写手                                   写手  ←───────────┘
(Style_Repo)                           (Style_Repo + Web3知识)
    ↓                                      ↓
评审 ←─退回重写                        评审 (+ Web3准确性) ←─退回重写
    ↓                                      ↓
润色师                                 润色师
    ↓                                      ↓
最终文章                               最终文章
```

---

## 阶段一：后端 Feature Flag 配置

### [MODIFY] `backend/app/core/config.py`

添加 Feature Flag 读取函数：

```python
def get_feature_flag(flag_name: str, default: bool = False) -> bool:
    """获取 Feature Flag 配置"""
    config = load_config()
    flags = config.get("feature_flags", {})
    return flags.get(flag_name, default)
```

### [MODIFY] `backend/config/user_config.json`

添加 Feature Flags 配置项：

```json
{
  "api_keys": { ... },
  "feature_flags": {
    "use_knowledge_repo": false
  }
}
```

---

## 阶段二：Knowledge Repo 检索服务

### [NEW] `backend/app/services/knowledge_retriever.py`

创建知识检索服务：

```python
async def retrieve_web3_knowledge(topic: str, max_results: int = 5) -> str:
    """
    从 Knowledge_Repo 检索与主题相关的 Web3 知识
    
    Returns:
        格式化的 Web3 知识上下文字符串
    """
    # 1. 连接 Lark Knowledge_Repo 表
    # 2. 基于 topic 关键词检索相关记录
    # 3. 按 质量评分 排序
    # 4. 格式化返回知识片段
```

**检索逻辑**:
- 从 `LARK_KNOWLEDGE_TABLE_ID` 表读取记录
- 匹配字段: `主题`, `正文内容`
- 排序依据: `质量评分` DESC
- 返回格式: `[Web3背景 1] ... [Web3背景 2] ...`

---

## 阶段三：Strategist 集成

### [MODIFY] `backend/app/agents/strategist.py`

修改 `build_strategist_context()` 函数：

```diff
+ from ..core.config import get_feature_flag
+ from ..services.knowledge_retriever import retrieve_web3_knowledge

def build_strategist_context(state: dict) -> dict:
    mode = state["mode"]
    narrative_type = state.get("narrative_type", "project_review")
    
    rag_context = load_style_samples(mode)
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
+   # [NEW] Feature Flag: Knowledge_Repo 集成
+   web3_context = ""
+   if get_feature_flag("use_knowledge_repo"):
+       topic = state.get("raw_input", "")
+       web3_context = retrieve_web3_knowledge(topic)
    
    context = {
        "current_time_str": current_time_str,
        "narrative_type": narrative_type,
        "mode": mode,
        "mode_description": mode_descriptions.get(mode, mode),
        "narrative_desc": narrative_desc,
        "rag_context": rag_context,
+       "web3_knowledge": web3_context  # 传递给 Writer
    }
    return context
```

---

## 阶段四：前端开关 UI

### [MODIFY] `frontend/src/app/(main)/settings/page.tsx`

在 Settings 页面添加 Feature Flag 开关：

```tsx
<Card>
  <CardHeader>
    <CardTitle>实验性功能</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="flex items-center justify-between">
      <div>
        <Label>启用 Knowledge_Repo 知识检索</Label>
        <p className="text-sm text-muted-foreground">
          Strategist 将从 Web3 知识库检索相关背景
        </p>
      </div>
      <Switch 
        checked={useKnowledgeRepo}
        onCheckedChange={handleToggleKnowledgeRepo}
      />
    </div>
  </CardContent>
</Card>
```

---

## 阶段五：验证测试

### 测试用例

| 场景 | 预期结果 |
|------|----------|
| Flag = false | 当前流程，无 Web3 知识 |
| Flag = true | 新流程，Strategist 输出包含 Web3 知识 |
| Knowledge_Repo 为空 | 优雅降级，继续当前流程 |

### 验证步骤

1. 启动后端和前端
2. 在 Settings 页面切换开关
3. 在 Studio 页面运行写作流程
4. 检查 Strategist 输出是否包含 `web3_knowledge`

---

## 文件清单

| 类型 | 文件 | 说明 |
|------|------|------|
| MODIFY | `backend/app/core/config.py` | 添加 Feature Flag 函数 |
| MODIFY | `backend/config/user_config.json` | 添加配置项 |
| **NEW** | `backend/app/services/knowledge_retriever.py` | 知识检索服务 |
| MODIFY | `backend/app/agents/strategist.py` | 集成知识检索 |
| MODIFY | `frontend/src/app/(main)/settings/page.tsx` | 添加开关 UI |

---

## 预估工时

| 阶段 | 时间 |
|------|------|
| 后端 Feature Flag | 10 分钟 |
| 知识检索服务 | 30 分钟 |
| Strategist 集成 | 15 分钟 |
| 前端开关 UI | 20 分钟 |
| 测试验证 | 15 分钟 |
| **合计** | **~1.5 小时** |
