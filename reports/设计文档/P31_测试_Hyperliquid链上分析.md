# Surf API 投研测试：Hyperliquid 链上数据分析

**时间**: 2026-02-25 12:46:03 | **模型**: surf-1.5-instant | **耗时**: 86.4s | **Tokens**: 11,231

---

# Hyperliquid 分析报告

> 本报告基于 CoinGecko 和 TokenTerminal 数据综合分析。数据截至 2026-02-25 04:45 UTC。
> 注意：Hyperliquid 协议级数据（TVL、收入、OI、费率等）在 TokenTerminal 中缺失，是本报告的主要局限。

## 一、当前价格与变动

| 指标 | 数据 |
|------|------|
| 当前价格 | **$27.24** |
| 24h 涨幅 | **+4.30%** |
| 市值 | **$64.93 亿** |
| 7d / 30d 变动 | ⚠️ 暂无数据（仅有 24h 数据） |

## 二、日交易量

**24h 交易量: $2.087 亿**

- 来源：CoinGecko 代币级数据，可能包含所有交易所的现货和部分衍生品
- ⚠️ 无法区分现货 vs 永续合约（协议级交易量数据在 TokenTerminal 中为空）
- 交易量/市值比：约 3.21%

## 三、TVL 与协议收入

> ⚠️ **无数据** — TokenTerminal 明确表示不提供 Hyperliquid 的 TVL、收入或用户数据。这是重大局限。

## 四、持仓量与资金费率

> ⚠️ **无数据** — 工具结果中不包含持仓量（OI）或资金费率数据。这些是永续合约平台的关键指标，缺失导致无法评估市场杠杆率和多空情绪。

## 五、活跃地址与交易量

> ⚠️ **无数据** — 缺乏日活用户（DAU）和链上交易数据。

## 六、竞品对比表

| 协议 | 价格 | 市值 | TVL | 24h 收入 | 日活用户 | 24h 交易量 |
|------|------|------|-----|----------|----------|-----------|
| **Hyperliquid** | **$27.24** | **$64.9 亿** | N/A | N/A | N/A | **$2.087 亿** |
| GMX | N/A | N/A | **$2.405 亿** | **$64,619** | **1,763** | **$3.313 亿** |
| dYdX | N/A | N/A | **$2.180 亿** | $11,481 | 1,678 | N/A |
| Vertex | N/A | N/A | $5.6 万 | $0 | N/A | N/A |
| Jupiter | N/A | N/A | N/A | N/A | N/A | $2,576 万 |

### 关键洞察
- Hyperliquid 市值 ($64.9 亿) 远超竞品，但缺乏协议级数据支撑
- GMX 的交易量 ($3.31 亿) 和 TVL ($2.4 亿) 数据较为完整
- dYdX 的 TVL 接近 GMX 但收入较低
- Vertex TVL 极低 ($5.6 万)，可能处于早期阶段

## 七、融资与团队

> ⚠️ 无数据（工具返回结果中未包含）

## 八、社交情绪

> ⚠️ 无数据（工具返回结果中未包含 Twitter 提及量或情绪评分）

## 九、主要风险

- **数据缺口与波动性**: 缺乏 TVL 和持仓量数据，难以评估协议健康度；+4.3% 的 24h 涨幅暗示动能，但缺乏长期数据背景
- **竞争压力**: GMX 交易量 ($3.31 亿) 和 TVL ($2.40 亿) 高于 Hyperliquid；$64.9 亿市值在无配套协议数据支撑下可能存在高估
- **监管与运营风险**: 作为永续合约交易所，面临资金费率操纵和连锁清算的风险
- **评估局限**: 链上指标整体缺失，建议补充 DefiLlama、Dune Analytics 等数据源

---

> 💡 **总结**: Hyperliquid 市值领先但 Surf API 对其链上数据覆盖有限。建议使用 **Grok + DefiLlama** 补充 TVL、OI、费率等关键指标，实现交叉验证。

**数据来源**: [CoinGecko](https://www.coingecko.com/en/coins/hyperliquid) | [TokenTerminal (Hyperliquid)](https://tokenterminal.com/explorer/projects/hyperliquid) | [TokenTerminal (GMX)](https://tokenterminal.com/explorer/projects/gmx) | [TokenTerminal (dYdX)](https://tokenterminal.com/explorer/projects/dydx)
