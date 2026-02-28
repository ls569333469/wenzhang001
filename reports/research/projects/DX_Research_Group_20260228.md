# 🔬 DX Research Group — 投研报告

> 生成时间: 20260228

# DX Research Group 项目投研分析报告

**报告日期：** 2026-02-28（基于当前时间和数据新鲜度）  
**分析来源：** 本报告基于内部数据库、Twitter搜索、官网（dxrg.ai、terminal.markets）、白皮书（docs.terminal.markets）、新闻报道（PRNewswire、Blockflow.news）、RootData、OpenSea、DeFiLlama等多源数据合成。数据主要聚焦2026年2月后事件（如DX Terminal Pro推出），但某些维度（如融资和团队）存在信息缺失，我将在对应部分明确说明局限性。TVL数据存在冲突（官方声明 vs DeFiLlama），已交叉验证但无法完全化解，将客观呈现。

以下从用户指定的8个维度进行分析，每个维度均以可用数据支撑，结合推理过程说明结论来源。

## 1. 项目概要（定位、核心产品、目标市场）
DX Research Group定位为一家R&D主导的研究实验室，专注于AI与crypto的交汇点，通过大规模多代理模拟实验加速创新（来源：官网dxrg.ai和内部数据库db_internal_project_overview）。核心产品是DX Terminal Pro，一个在Base网络上的“Onchain Agentic Market”实验平台，于2026-02-24推出，用户通过NFT（DX Terminal NFT）创建AI代理，这些代理自主交易真实ETH（无人类手动干预），平台涉及16个Genesis Tokens竞争机制，最终仅一token“毕业”进入公开市场（来源：白皮书docs.terminal.markets/whitepaper和PRNewswire新闻）。目标市场主要是Web3 AI爱好者和crypto交易者，强调开发者工具、NFT收藏和AI代理模拟，热度原因源于AI趋势（如1500+代理控制3000+ ETH，首小时生成$4.5M交易量，来源：Twitter @DXRGai和PR公告）。  
**推理过程：** 数据来源于官方文档和社交，定位清晰但实验性强，目标市场基于标签（Developer Tooling, NFT, Web3 AI）和用户参与度（1500+参与者）推断，覆盖AI-crypto交叉领域。

## 2. 融资与估值（融资历史、投资方、估值、FDV）
无公开融资历史记录。Crunchbase、RootData和Pitchbook搜索均无匹配项目，疑似自筹或未披露模式（来源：web_fetch结果和RootData项目页）。无已知投资方、估值或FDV数据；项目通过NFT销售和用户存款（约$6.1M ETH，来源：PRNewswire）生成资金，但非传统融资。  
**推理过程：** 多轮搜索确认无记录，如果存在隐秘融资，可能为种子轮但未公开；局限性：数据缺失导致无法量化估值，基于TVL推算潜在FDV可能在数百万美元级别，但无支撑数据。

## 3. 团队（核心成员、背景、可信度评分 1-10）
团队高度匿名，仅在白皮书中提及“DXRG Team”（邮箱hello@dxrg.ai），无具体成员名单或LinkedIn背景（来源：白皮书和RootData）。疑似核心人物包括Timothy Barton（PR中提及为Group Founder）和@poof_eth（Twitter/Tweet中讨论平台演示），但无详细背景验证（无教育/工作经历）。可信度评分：5/10（中等偏低），理由：匿名性常见于crypto实验项目，但缺乏透明度增加不确定性；过去实验（如DX Terminal 1模拟36,651代理）显示技术能力，但无公开履历支撑。  
**推理过程：** 基于Twitter/PR交叉验证，匿名团队常见于Web3但降低可信度；评分考虑执行历史（成功推出DX Terminal Pro）平衡信息缺失。

## 4. 市场数据（价格、市值、TVL、社交数据）
无主代币价格/市值（项目非token发行，而是实验Genesis Tokens）。NFT（DX Terminal collection）地板价约0.0153 ETH（来源：OpenSea collection数据）。TVL存在冲突：官方PR报道$6.1M（1500+用户存款，2026-02-26数据，来源：PRNewswire和Twitter）；DeFiLlama显示$1.29M（仅Ethereum预存款，来源：defillama.com/protocol/terminal-finance-pre-deposits），可能因Base链追踪不全或定义差异（on-chain验证未找到峰值活动，来源：get_evm_block_by_timestamp块42671527标准活动）。社交数据：Twitter @DXRGai有11,776 followers，最近推文互动高（如Tweet 10：53,953 views、203 likes，来源：twitter_search）；Discord活跃但无精确数字。  
**推理过程：** 数据多源交叉（官方>DeFiLlama>on-chain），TVL冲突注明为局限（可能官方包括未追踪vaults）；社交指标显示中等热度，NFT价格低反映实验阶段。

## 5. 代币经济学（总量、分配、解锁计划）
无主项目代币，经济学聚焦16个Genesis Tokens的竞争机制（来源：白皮书）。每个token固定Genesis价格预售（无总量细节，分配基于用户通过AI代理订阅ETH，1500+代理控制约3000 ETH）；21天内，通过“Reaping”淘汰最低市值token，其流动性迁移至顶级token，持有者获补偿（来源：docs.terminal.markets/quick-start）。最终一token“毕业”进入Uniswap V4公开池，无明确解锁计划（事件驱动，2026-03-19毕业）。经济模型依赖NFT（一NFT一代理）和用户存款，非通胀型。  
**推理过程：** 白皮书提供核心机制，但无总量/FDV细节（局限：实验性设计非标准tokenomics）；分配推断为用户驱动，强调AI协调而非传统vesting。

## 6. 竞品对比（同赛道 2-3 个竞品）
同赛道为Web3 AI（代理/交易实验）。  
- **SingularityNET**（AGIX token，MC ~$1B，来源：RootData类似项目）：定位AI市场平台，用户上传/交易AI服务；对比DX：SingularityNET更注重去中心化AI基础设施，市场份额大（社交mindshare高），但DX独特于纯onchain代理真实资本交易（DX更实验，SingularityNET更成熟）。  
- **Numerai**（NMR token，MC ~$100M，来源：RootData）：AI驱动对冲基金，用户提交模型预测股票；对比DX：Numerai聚焦金融预测，TVL/volume稳定，但DX强调多代理模拟和token竞争（DX更创新但风险高，Numerai有实际收益记录）。  
- **Tilted**（无token，mindshare排名2，来源：get_projects_by_industry数据）：AI游戏资产NFT平台；对比DX：Tilted目标游戏创作者，社交热度高（@tiltedxyz），但DX更专注crypto交易实验（DX TVL $6.1M vs Tilted N/A，DX更前沿）。  
**推理过程：** 选自mindshare数据和RootData类似项目，比较基于产品机制、市场数据；DX差异化在于代理自主性，但竞品有更高MC/TVL。

## 7. 风险与机会（关键风险点、投资机会窗口）
**关键风险点：** (1) 实验性高，用户同意代理不可预测行为，真实资本损失风险（来源：白皮书警告和PR）；(2) 团队匿名和无融资记录增加信任风险（可信度低）；(3) TVL数据冲突和on-chain未验证可能隐藏流动性问题（来源：DeFiLlama vs 官方）；(4) 监管不确定（AI+crypto实验可能引合规问题，来源：新闻中无提及但赛道共性）。  
**投资机会窗口：** (1) AI-Web3热点（mindshare数据显示Web3 AI项目如Bertram MC $10M），DX数据价值潜力（生成1万亿token行为数据集，来源：PR）；(2) 短期窗口：2026年Q1事件后（毕业token公开发行），若代理表现优异，可捕获注意力（来源：Twitter趋势）；(3) 长期：多代理模拟前沿，潜在R&D合作。  
**推理过程：** 风险基于官方警告和数据缺失，机会从热度原因和竞品mindshare推断；窗口考虑事件时间表（2026-03-19）。

## 8. 总结评级（1-10 分 + 一句话结论）
**评级：6/10**。DX Research Group作为创新AI-crypto实验项目有独特代理机制和热度潜力，但团队匿名、数据冲突和实验风险限制整体吸引力。