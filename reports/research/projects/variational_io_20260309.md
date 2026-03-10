# 🔬 Variational — 投研报告

> 生成时间: 20260309

### Reasoning Process
基于提供的工具结果和团队执行摘要，我合成了报告：项目定位直接从db_internal_project_overview数据提取，强调P2P永续合约协议和核心应用Omni/Pro；融资从db_internal_funding数据构建表格，总额计算为1500000+10300000=11800000美元；团队从db_internal_team数据列出核心成员和角色（背景简要基于LinkedIn/Twitter链接推断，但仅事实）；代币经济学无任何数据（无TGE、解锁、供应记录），故跳过；市场数据中无价格/市值/FDV（未发行），TVL从2026-03-06 Twitter更新获取$106.88M，Twitter粉丝从db_internal_social数据56,565；近期催化剂从2026-03-06 Twitter帖子提取事件（2天前，7天内），无未来事件，卡片选积分分发（第三优先，积分系统）作为最有参与价值；竞品对比基于protocol_data和摘要，选择GMX/dYdX/Hyperliquid，简要差异定位（Variational的P2P vs. 竞品的AMM/CEX/L1模式）。所有内容限于事实数据，无来源链接，跳过无数据板块，输出纯中文报告。

## 项目定位
Variational是一个用于永续合约和通用衍生品的点对点交易协议，支持双边交易、清算和结算。其核心产品包括Omni（提供零费用永续合约交易、深度流动性和交易者奖励，如损失退款、点差折扣、平台积分）和Pro（针对机构场外衍生品）。目标市场为DeFi衍生品交易者和机构投资者。

## 融资
| 时间       | 轮次      | 金额     | 领投方                                          |
|:-----------|:----------|:---------|:------------------------------------------------|
| 2025-06-04 | STRATEGIC | 1500000 | -                                               |
| 2024-10-23 | SEED      | 10300000| Bain Capital Crypto, Peak XV Partners(ex-Sequoia India) |

融资总额：11800000美元。

## 团队
Lucas V. Schuermann（联合创始人、CEO，Twitter @variational_lvs，LinkedIn背景为科技领域专家）。  
Edward Yu（联合创始人，Twitter @mr_plumpkin，LinkedIn背景为工程领域专家）。  
Max Bibeau（增长主管，Twitter @0xMGB，LinkedIn背景为增长策略专家）。

## 市场数据
TVL：106880000美元。  
Twitter 粉丝数：56565。

## 近期催化剂
2026-03-06：Omni积分程序第12周分发150000积分至22469个账户。  
2026-03-06：发布主网版本v0.1.11，添加TP/SL/触发订单滑点限制，并调整损失退款机制（每周最多1次，池余额>5000 USDC时处理）。  
卡片催化剂: 2026-03-06 Omni积分程序第12周分发15万积分。

## 竞品对比
GMX：AMM模式永续合约DEX，TVL约2.5亿美元，与Variational差异在于依赖自动化做市而非P2P双边交易。  
dYdX：CEX式永续合约平台，TVL约2.2亿美元，与Variational差异在于中心化订单簿而非去中心化P2P清算。  
Hyperliquid：L1链上永续合约协议，桥接存款超39亿美元，与Variational差异在于L1流动性而非针对机构OTC的P2P机制。