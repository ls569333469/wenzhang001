# 🔬 SeekerClaw — 投研报告

> 生成时间: 20260228

# SeekerClaw 项目深度投研分析报告

**报告日期**：2026-02-28  
**数据来源**：基于工具结果，包括网站爬取（seekerclaw.xyz、GitHub）、Twitter 搜索、Solana 链上数据（Solscan.io）、新闻搜索和内部工具反馈。所有数据截至 2026-02-28 UTC。  
**注意**：该项目为极早期开源应用，无主流数据源（如 CoinMarketCap、TokenTerminal）覆盖，部分维度数据缺失或基于社区 meme 代币推断。我的分析直接基于可用数据合成，避免推测；缺失处明确注明局限性。分析过程：首先验证项目真实性（官网、Twitter、GitHub 交叉确认），然后映射到 8 个维度，优先使用量化数据支撑结论。

## 1. 项目概要（定位、核心产品、目标市场）
SeekerClaw 定位为 Solana Seeker 手机的 AI Agent Layer，一个开源的自主 AI 代理应用，旨在将手机转变为 24/7 运行的智能设备，支持钱包监控、自动化任务和 Telegram 集成。核心产品包括：内置 56+ 工具（如 Solana 钱包访问、Jupiter 交易、Telegram 消息处理、GPS/相机控制），由 Claude AI 驱动，支持持久内存和自定义调度；安装简单，通过 dApp Store 下载并配置 Telegram/AI 密钥（官网 seekerclaw.xyz 描述）。目标市场主要为 Solana 生态用户，尤其是 200,000+ Seeker 手机持有者，聚焦 crypto-native AI 应用，如 DeFi 监控和 web 研究。  
**数据支撑**：官网内容显示“200,000+ Seeker Devices, 56+ Built-in Tools, 191+ PRs Shipped”；Twitter 介绍推文（2026-02-27）有 52,091 views，强调“第一款完全运行在 Solana Mobile 上的 AI 代理”。  
**分析过程**：从官网和 Twitter 提取功能列表，确认与 Solana Mobile 官方推广一致（推文 135,792 views），定位为 niche Solana dApp。

## 2. 融资与估值（融资历史、投资方、估值、FDV）
无任何融资历史记录、投资方公告或估值数据。该项目表现为纯开源开发，无 Crunchbase、新闻或 Twitter 提及的融资事件，可能依赖社区贡献或开发者自筹。FDV 无法计算，因无官方代币或估值基准。  
**数据支撑**：工具结果（新闻搜索、web_search、db_internal_data）均显示“无匹配实体”或“无融资记录”；GitHub 和 Twitter 无相关公告。  
**分析过程**：交叉检查多个来源确认空白，局限性在于项目早期（2026-02-27 推出），可能尚未寻求融资；若有隐藏估值，数据不足以推断。

## 3. 团队（核心成员、背景、可信度评分 1-10）
核心成员为 sepivip（GitHub 用户），作为项目创始人，负责代码开发，无公开 LinkedIn 或以往项目历史；团队规模未知，可能为 solo 开发者或小团队。背景限于 GitHub 活动：319 commits 和 191+ PRs 在 4 周内完成，显示高效开发能力，但缺乏透明度。  
可信度评分：6/10（基于活跃开源贡献，但无验证背景或团队扩展，存在单点故障风险）。  
**数据支撑**：GitHub 仓库（github.com/sepivip/SeekerClaw）显示“319 Commits, 191+ PRs”；Twitter @SeekerClaw 提及 sepivip 为创始人，无其他成员披露。  
**分析过程**：从 GitHub 和 Twitter 提取开发者信息，评分考虑开发活跃度（高） vs. 透明度（低），与 Web3 标准比较中等。

## 4. 市场数据（价格、市值、TVL、社交数据）
无官方 TVL 数据（TokenTerminal 查询返回“无匹配项目”）。关联社区 meme 代币 SEEKER（地址 EovP8jsRTJd3pbpdPWvnQ5SDYenUMg7QAtctY2SEEKER）当前价格 0.00000280277 USD，24h 变化未知，市值 2,802.69 USD，24h 交易量 334,224 USD。社交数据：Twitter @SeekerClaw 有 1,270 followers，近期推文平均 3,000-52,000 views，Solana Mobile 推广推文 135,792 views 和 976 likes；dApp Store 评分 4.4/5（2d ago 更新）。  
**数据支撑**：链上数据（Solscan.io）显示价格/市值/volume；Twitter 搜索显示 followers 和 engagement；seekertracker.com/apps 列出评分。  
**分析过程**：使用链上工具填充 meme 代币数据（官方无 token），社交从 Twitter 结果量化，TVL 缺失注明为局限性；整体热度低，依赖 Solana Mobile 曝光。

## 5. 代币经济学（总量、分配、解锁计划）
无官方代币。社区 meme 代币 SEEKER 总量 999,968,195,410,519,400（约 1 万亿），分配高度集中（顶级持有者占 71.38%，前 20 持有者占 ~95%）；无解锁计划记录或 DeFi 活动表明官方设计，最近转移主要是 DEX swap（如 Jupiter，2026-02-28）。  
**数据支撑**：链上元数据（Solscan.io）显示供应和持有者分布（rank 1: 71.38%）；DeFi 活动工具返回 20+ swap 事件，无解锁迹象。  
**分析过程**：基于链上验证确认非官方，分配从 holders 表计算集中度，解锁缺失视为高风险信号；局限性：若官方 token 存在，数据未覆盖。

## 6. 竞品对比（同赛道 2-3 个竞品）
同赛道为 Solana Seeker dApp 中的 AI/代理工具。  
- **MoltSentinel**：情报层 AI，聚焦以上 AI 情报，dApp Store 评分 3.3/5（2w ago），差异：SeekerClaw 更注重 24/7 钱包集成，而 MoltSentinel 强调情报聚合，无类似 Telegram 深度。  
- **Flashback AI**：生活时刻捕捉 AI，dApp Store 评分未知（BETA），差异：聚焦 NFT-based 媒体备份，SeekerClaw 更 crypto-native（如 Jupiter swap），但 Flashback 有加密备份优势。  
- **Alchemy Merch**（备选）：AI 自定义商品工具，评分未知，差异：商业化导向 vs. SeekerClaw 的开源代理自动化。SeekerClaw 独特于设备原生运行和 56+ 工具，潜在优势在 Solana 生态集成，但竞品有更高评分或特定功能（如 MoltSentinel 的情报）。  
**数据支撑**：seekertracker.com/apps 列出竞品评分和描述；工具反馈确认 Solana Seeker 生态类似 dApps。  
**分析过程**：从 dApp Store 数据选取 2-3 个 AI 相关竞品，比较功能/评分，突出 SeekerClaw 的差异化。

## 7. 风险与机会（关键风险点、投资机会窗口）
**关键风险点**：(1) 团队不透明（solo 开发者，背景有限，可信度 6/10）；(2) 无官方 token，高 meme 代币集中风险（71% 单一持有者，易操纵）；(3) 早期阶段，无融资/TVL，依赖 Solana Mobile 推广（若生态衰退，增长停滞）；(4) 链上活动有限（仅 swap，无 DeFi 深度），潜在 rug pull 风险。  
**投资机会窗口**：Solana Seeker 生态扩张（200k+ 设备），若项目获更多官方支持（如 Solana Mobile 推文 135k views），可能在 2026 Q1 成为 AI dApp 热点；开源性质（319 commits）吸引开发者社区，机会在 meme 代币短期炒作（24h volume 334k USD）。窗口：短期（1-3 月），监控 Twitter 活跃。  
**数据支撑**：持有者分布（Solscan.io）和 Twitter engagement；新闻搜索无负面，但早期性质隐含风险。  
**分析过程**：风险从数据空白和集中度量化，机会基于社交热度和生态规模推断，平衡客观。

## 8. 总结评级（1-10 分 + 一句话结论）
**评级**：5/10（开源创新和 Solana 集成有潜力，但数据缺失、团队不透明和 meme 风险拉低分数）。  
**一句话结论**：SeekerClaw 作为 Solana Seeker 的早期 AI 代理项目显示技术承诺，但缺乏融资和官方 token 支持使其更适合观察而非投资。