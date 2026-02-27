# 🔬 Kyber Network — 投研报告

> 生成时间: 20260227

# Kyber Network 项目投研分析报告

**报告日期：** 2026-02-27 UTC  
**分析依据：** 本报告基于工具结果和团队执行总结中的数据合成，包括内部数据库、CoinGecko、DefiLlama、Token Terminal、Twitter搜索、新闻搜索等来源。数据时效性为2026-02-27，确保每个维度有具体数据支撑。如果数据不足，将明确说明。推理过程将在每个维度后简要说明，以展示如何从可用信息得出结论。

## 1. 项目概要（定位、核心产品、目标市场）
Kyber Network 定位为多链流动性中心和协议，专注于聚合 DEX 和做市商流动性，提供即时代币交换、最优路由和资本高效的流动性池。核心产品包括 KyberSwap（去中心化交易所和聚合器，支持 16 条链，如 Ethereum、Polygon 和 Avalanche，提供限价单、流动性挖矿和发现工具）和开发者 API，用于无缝集成代币交换。目标市场是 DeFi 用户、流动性提供者和开发者，涵盖跨链桥、开发者工具以及 DEX & AMM 领域，旨在简化 DeFi 交易并优化流动性（例如，通过动态市场制造商 DMM 协议调整费用以应对波动）。  
**数据支撑：** 从内部数据库（db_internal_project_overview_kyber_network），项目标签为“Cross-Chain & Bridge, Developer Tooling, DEX & AMM”；新闻搜索（TradingView，2026-02-26）确认整合 Supernova 以提升流动性；Twitter 搜索显示最近推文聚焦产品更新，如 Smart Exit 和中国语言支持。  
**推理过程：** 通过聚合项目描述、标签和最近新闻/推文，得出定位和产品焦点；目标市场基于支持链数（16 条）和工具功能（如 API），无冲突数据。

## 2. 融资与估值（融资历史、投资方、估值、FDV）
Kyber Network 总融资额 8620 万美元，包括 2017-09-15 ICO 2500 万美元、2017-09-19 undisclosed 轮 6000 万美元（投资方：Kenetic Capital、Fenbushi Capital、Hashed、Fundamental Labs、IOSG Ventures 等）和 2023-10-13 grant 120 万美元（Arbitrum Foundation）。当前估值基于市值 2335 万美元，FDV（完全稀释估值）为 3225 万美元（基于总供应量 2.523 亿 KNC 和价格 0.137 美元）。无近期估值更新，但 2026 年整合如 Supernova 可能提升潜在价值。  
**数据支撑：** 从内部数据库（db_internal_funding_kyber_network），融资历史详尽列出；DefiLlama（kyberswap 数据）提供 FDV 3225 万美元；市场数据（CoinGecko）支持当前市值。  
**推理过程：** 直接汇总融资记录计算总额，FDV 通过总供应 * 当前价格计算；投资方列表完整，无需推测；估值基于实时市场数据，避免过时假设。

## 3. 团队（核心成员、背景、可信度评分 1-10）
核心成员包括 Loi Luu（联合创始人兼 CEO，Twitter @loi_luu，LinkedIn：计算机科学背景，曾创办 Smart Pool 去中心化挖矿池）；Victor Tran（联合创始人兼 CEO，Twitter @vutran54，LinkedIn：越南国家工程大学计算机科学毕业，曾任 Clixy CTO，构建 C2C 广告基础设施，并与 Loi 共同创办 Smart Pool）；Tu Nguyen（工程主管，LinkedIn：工程背景）。团队有区块链创业经验，如 Smart Pool 的成功和 Kyber 的 ICO 表现。团队可信度评分：8/10（基于过往项目成功和专业背景，但无 2026 年更新，可能存在执行风险）。  
**数据支撑：** 从内部数据库（db_internal_team_kyber_network），成员 LinkedIn 和 Twitter 链接；Medium 和 MEXC Wiki 确认 Loi 和 Victor 的背景，包括 Smart Pool 和 Kyber 早起成功。  
**推理过程：** 背景从 LinkedIn 和历史文章交叉验证；评分基于项目历史（如 2017 ICO 成功）和无负面事件（8 分反映可靠但非顶级，如无 Vitalik 级别影响力），数据覆盖完整。

## 4. 市场数据（价格、市值、TVL、社交数据）
KNC 当前价格 0.137 美元，24h 变化 +1.49%，市值 2335 万美元，24h 成交量 410 万美元。TVL 为 117 万美元（Ethereum 占比 61 万美元，聚合器累计交易量 1320 亿美元，最近 30 天聚合交易量 93.83 亿美元）。社交数据：Twitter @KyberNetwork 粉丝 29.3 万，最近推文活跃（35 条，2026-02 期间，焦点产品如 Limit Orders 和 MegaETH 整合，平均互动 1-2k 查看/10-20 点赞）。  
**数据支撑：** CoinGecko（token_trading_data_KNC_price）提供价格/市值/成交；DefiLlama（kyberswap 和 kyberswap-aggregator）确认 TVL 和交易量；内部数据库/Twitter 搜索显示粉丝和推文数据。  
**推理过程：** 价格/TVL 直接从实时快照获取；社交热度通过粉丝数和推文互动量化；数据一致，TVL 低但交易量高表明聚合器强势。

## 5. 代币经济学（总量、分配、解锁计划）
KNC 总量（最大供应）2.523 亿，流通供应 1.70 亿（占 67.44%）。分配：社区投资者 52.3%（1.32 亿）、公司运营储备 16.7%（4210 万）、创始人/顾问/早期投资者 16.7%（4210 万）、KyberDAO 生态增长基金 14.3%（3600 万）。解锁计划：已完全解锁（ICO 后线性归属结束于 2023 年，迁移后无新锁定），历史包括 ICO 后烧毁 537 万 KNCL 和 2021 年增发 4200 万用于生态基金。  
**数据支撑：** Tokenomist 和 Dropstab 确认总量/分配/解锁（2023 年完全解锁）；DefiLlama 支持流通供应；官方文档（kyberswap docs）描述 KNC 用于治理、质押和费用机制。  
**推理过程：** 总量/分配从 vesting 图表直接提取；解锁基于时间表确认“fully unlocked”；流通比例计算为 1.70亿 / 2.523亿，无数据冲突。

## 6. 竞品对比（同赛道 2-3 个竞品）
Kyber Network 同属 DEX & AMM/聚合器赛道。竞品 1：Uniswap（TVL 30.73 亿美元，年化收入 2165 万美元，最近 30 天交易量 22.19 亿美元，社交 mindshare 高，位居顶级）；竞品 2：1inch（TVL 292 万美元，最近 30 天聚合交易量 49.79 亿美元，支持多链但 TVL 低于 Kyber）；Kyber TVL 117 万美元较低，但交易量 2.35 亿美元（排名第7），聚合量累计 1320 亿美元，优势在多链支持（16 条 vs Uniswap 主 Ethereum）。  
**数据支撑：** Token Terminal（recommend_data_top_dex_volume）排名 Kyber 第7；DefiLlama 提供 Uniswap/1inch TVL/交易量；mindshare 数据（asksurf.ai）显示 Uniswap 排名第5。  
**推理过程：** 选择 Uniswap/1inch 作为顶级竞品，通过 TVL/交易量直接对比；Kyber 优势从链支持和聚合量推导，数据覆盖 2026 年。

## 7. 风险与机会（关键风险点、投资机会窗口）
关键风险点：历史黑客事件（2023 年 KyberSwap Elastic 损失 4800 万美元，通过协议逻辑漏洞，已恢复但影响声誉）；持有者集中（前 25 地址持 52.55% 供应，可能导致价格操纵）；TVL 低（117 万美元 vs 竞品数十亿），表明流动性不足和市场份额丢失；无近期 TVL 数据（Token Terminal 缺失），可能隐藏波动风险。投资机会窗口：多链扩展（2026 年整合 Supernova 和 MegaETH，支持 16 链）提供增长潜力；FairFlow 流动性挖矿和中文支持瞄准亚洲市场；交易量强劲（排名前10），2026 年中国社区构建和共识香港活动可作为入场窗口（短期 3-6 月内）。  
**数据支撑：** Hacken 和 DefiLlama 确认 2023 hack；链上数据（token_onchain_data）显示持有集中；Twitter/新闻搜索突出 2026 机会如 Supernova 整合。  
**推理过程：** 风险从历史事件和持有分布量化；机会基于最近推文/新闻的时间线推断窗口，平衡正面扩展与潜在问题。

## 8. 总结评级（1-10 分 + 一句话结论）
评级：7/10。Kyber Network 作为成熟的多链 DEX 聚合器，在交易量和扩展机会上表现强劲，但 TVL 低和历史安全风险限制了其长期潜力。  
**推理过程：** 评分基于整体数据平衡（团队8分、市场交易量高+7，风险/TVL 低-3），得出7分；结论浓缩优势（交易量/扩展）和劣势（TVL/风险），数据驱动无主观偏见。