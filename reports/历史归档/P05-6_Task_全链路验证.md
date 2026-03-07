# Phase 9: 详细执行任务清单 (Execution Tasks)

> **版本**: v1.0
> **日期**: 2026-01-20
> **策略**: 务实方案 (P0-P2 必做, P3 简化)

---

## 🔴 P0: 核心链路修复 (预估 1.5h)

### P0-1: 修复 `confirmStrategy` (45min)

**问题定位**: `useAgentStore.ts` 第 145-171 行 try 块为空

**修复步骤**:
1. 在 `AgentState` 接口新增:
   ```typescript
   lastRequestPayload: {
       input: string;
       config: GenerateConfig;
   } | null;
   ```

2. 在 `startSession` 中保存 payload:
   ```typescript
   set({ lastRequestPayload: { input, config } });
   ```

3. 实现 `confirmStrategy`:
   ```typescript
   confirmStrategy: async (option: any) => {
       const { lastRequestPayload } = get();
       if (!lastRequestPayload) return;
       
       const response = await fetch(`${API_URL}/generate`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
               ...lastRequestPayload,
               selected_option: option
           })
       });
       
       // Process SSE stream...
   }
   ```

**验收标准**:
- [ ] 用户选择策略后，Timeline 进入 Writer 阶段
- [ ] 最终生成内容显示在 Canvas 中

---

### P0-2: 修复 Dashboard MonitorCard (30min)

**问题定位**: `MonitorCard.tsx` 静态显示 status

**修复步骤**:
1. 在 `dashboard/page.tsx` 添加健康检查:
   ```typescript
   const [backendStatus, setBackendStatus] = useState<'online'|'offline'>('offline');
   
   useEffect(() => {
       fetch('http://localhost:8000/health')
           .then(res => res.ok ? setBackendStatus('online') : setBackendStatus('offline'))
           .catch(() => setBackendStatus('offline'));
   }, []);
   ```

2. 传递动态状态给 MonitorCard:
   ```tsx
   <MonitorCard label="后端核心" status={backendStatus} />
   ```

**验收标准**:
- [ ] 后端运行时显示绿色 "Online"
- [ ] 后端停止时显示红色 "Offline"

---

## 🟡 P1: 页面补全 (预估 2h)

### P1-1: Settings 后端同步 (30min)

**问题定位**: `settings/page.tsx` 仅存 localStorage

**修复步骤**:
1. 在 `handleSave` 中添加后端同步:
   ```typescript
   await fetch('http://localhost:8000/config/keys', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ api_key: apiKey, model, base_url: baseUrl })
   });
   ```

2. 在 `useEffect` 中从后端加载:
   ```typescript
   fetch('http://localhost:8000/config/keys')
       .then(res => res.json())
       .then(data => {
           if (data.api_key) setApiKey(data.api_key);
           // ...
       });
   ```

**验收标准**:
- [ ] 保存后刷新页面，配置仍存在
- [ ] 后端 `user_config.json` 更新

---

### P1-2: Knowledge 页面 MVP (45min)

**目标**: 展示 Lark 素材列表

**实现步骤**:
1. 创建 API 调用:
   ```typescript
   const [materials, setMaterials] = useState([]);
   useEffect(() => {
       fetch('http://localhost:8000/config/knowledge')
           .then(res => res.json())
           .then(setMaterials);
   }, []);
   ```

2. 替换占位符为列表:
   ```tsx
   <div className="grid gap-4">
       {materials.map(m => (
           <div key={m.id} className="p-4 bg-white rounded-xl border">
               <h3>{m.title}</h3>
               <p className="text-sm text-ink-muted">{m.type}</p>
           </div>
       ))}
   </div>
   ```

**验收标准**:
- [ ] 页面显示至少 1 条素材 (或"暂无数据"提示)
- [ ] 无 JS 错误

---

### P1-3: Agents 页面 MVP (45min)

**目标**: 展示 4 个 Agent 及其配置

**实现步骤**:
1. 定义 Agent 列表:
   ```typescript
   const agents = [
       { id: 'strategist', name: '策略师', icon: Brain },
       { id: 'writer', name: '写手', icon: Pen },
       { id: 'critic', name: '评论家', icon: Eye },
       { id: 'polisher', name: '润色师', icon: Sparkles }
   ];
   ```

2. 创建 AgentCard 组件展示配置状态

**验收标准**:
- [ ] 显示 4 个 Agent 卡片
- [ ] 每个卡片显示对应模型名称

---

## 🟢 P2: DOM 测试与验证 (预估 1h)

### P2-1: 全链路 E2E 测试 (Browser Subagent)

**测试场景**:
1. Dashboard → Studio 导航
2. 输入文本 → 点击提交 → 等待分析
3. 选择策略 → 等待生成
4. 验证 Canvas 显示内容

**执行方式**: 使用 Browser Subagent 手动执行

---

### P2-2: Lighthouse 性能测试Lighthouse 性能测试

**执行命令**:
```bash
npx lighthouse http://localhost:3000 --output=html --output-path=./lighthouse-report.html
```

**目标指标**:
- Performance: ≥ 85
- Accessibility: ≥ 90
- Best Practices: ≥ 90

---

## 📋 执行顺序总览

```
Step 1: P0-1 修复 confirmStrategy     [45min]
Step 2: P0-2 修复 Dashboard Monitor   [30min]
Step 3: P2-1 全链路 E2E 测试验证       [15min]
   ↓ (验证核心链路通过后继续)
Step 4: P1-1 Settings 后端同步        [30min]
Step 5: P1-2 Knowledge MVP            [45min]
Step 6: P1-3 Agents MVP               [45min]
Step 7: P2-2 Lighthouse 测试          [15min]
```

**总计**: 约 4 小时
