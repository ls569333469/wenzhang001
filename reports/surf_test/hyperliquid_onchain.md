# Surf API Test: hyperliquid_onchain

**Time**: 2026-02-25 12:46:03

**Model**: surf-1.5-instant

**Elapsed**: 86.4s

**Tokens**: prompt=6593, completion=1880, total=11231

---

# Hyperliquid Analysis Report

As a professional crypto research analyst, this report synthesizes the available data on Hyperliquid (HYPE token) and its competitors based on the provided tool results. I'll explain my reasoning step-by-step throughout, highlighting how conclusions are drawn from the data. Note that the data is limited: for Hyperliquid, we primarily have token-level metrics from CoinGecko (as of last updated timestamp 2026-02-25 around 04:45 UTC, inferred from tool IDs and current time), but protocol-specific metrics like TVL, revenue, open interest, funding rates, active addresses, and transaction volumes are missing or noted as unavailable in TokenTerminal results. Competitor data is more robust for some (e.g., GMX, dYdX) but incomplete for others. Where data is absent, I'll explicitly state limitations and avoid speculation. No funding history, team background, or social sentiment data is provided, so these sections will note the gaps. All timestamps are in UTC.

The report focuses on the user's requested metrics, with additional required sections (e.g., market cap, risks). Comparisons are based on the most recent available data points (e.g., up to 2026-02-23 for competitors).

## 1. Current Price and Changes
Based on CoinGecko data (last updated at UNIX timestamp 1771994677, which converts to approximately 2026-02-25 04:44 UTC), Hyperliquid's HYPE token price is $27.2435 USD. The 24h change is +4.30389%. 

Reasoning: This is directly pulled from the table in the token_trading_data_HYPE_price result. However, the data does not include 7d or 30d changes—only 24h metrics are available. I cannot calculate longer-term changes without historical price data, which is absent here. As a limitation, I'll note that 7d/30d trends cannot be assessed from the provided sources.

- **Market Cap**: $6,492,730,000 USD (reasoning: Directly from the same table; this is a key metric I must include per instructions).
- **24h Change**: +4.30% (positive momentum, but no context for longer periods).

## 2. Daily Trading Volume (Spot + Perps)
The 24h trading volume for HYPE is $208,697,000 USD.

Reasoning: This is the volume_24h_USD from CoinGecko data, which likely includes spot and some derivatives trading across exchanges. However, the query specifies "spot + perps," and TokenTerminal's token_trading_data_hyperliquid_trading_volumn result shows an empty table with no volume metrics for Hyperliquid's protocol-level trading (e.g., perpetuals on the platform). This suggests data unavailability; the CoinGecko figure is token-specific, not necessarily protocol-wide. No breakdown by spot vs. perps is provided, limiting deeper analysis. For context, this volume represents about 3.21% of the market cap (calculated as volume / market cap).

## 3. TVL and Protocol Revenue
No data available for TVL or protocol revenue.

Reasoning: The protocol_data_hyperliquid_tvl_revenue_users result explicitly states that TokenTerminal does not have data for TVL, revenue, or users for Hyperliquid. This is a significant limitation—no alternative sources are provided in the results. Without this, I cannot quantify locked value or earnings. Hyperliquid is a decentralized perpetuals exchange, so TVL would typically represent collateral in the system, but we lack metrics here.

## 4. Open Interest and Funding Rates
No data available.

Reasoning: None of the tool results include open interest (total value of outstanding derivatives contracts) or funding rates (periodic payments between long/short positions). These are critical for perps platforms but absent, preventing analysis. This gap means we can't assess market leverage or sentiment through these lenses.

## 5. Active Addresses and Transaction Volume
No data available for active addresses or transaction volume.

Reasoning: Protocol data from TokenTerminal notes missing user metrics (e.g., no user_dau for daily active users, which could proxy active addresses). No on-chain transaction data is provided. This limits insights into user engagement or network activity.

## 6. Top 5 Competitors Comparison Table
I've compared Hyperliquid with GMX, dYdX, Vertex, and Jupiter using available metrics like price (only for HYPE), market cap (only for HYPE), TVL, revenue, daily active users (DAU), and trading volume. For consistency, I used the most recent data points (e.g., 2026-02-23 where available) from TokenTerminal and CoinGecko.

Reasoning: Hyperliquid data is sparse, so its columns reflect what's available (e.g., price/volume from CoinGecko; others marked N/A). For competitors:
- GMX: Robust data from protocol_data_gmx and token_trading_data_gmx; latest TVL/revenue from 2026-02-23, volume as notional_trading_volume (proxy for spot + perps).
- dYdX: Similar from protocol_data_dydx; latest metrics from 2026-02-23, but trading volume empty in results.
- Vertex: Truncated data; TVL very low (e.g., 0.056 from 2026-02-12), no volume.
- Jupiter: Only token_trading_volume from token_trading_data_jupiter (latest 2026-02-23); no TVL/revenue/users.
I prioritized comparable metrics; where missing, noted N/A. This table highlights Hyperliquid's strong market cap but data gaps in protocol metrics compared to GMX and dYdX.

| Protocol       | Price (USD) | Market Cap (USD) | TVL (USD)      | 24h Revenue (USD) | Daily Active Users | 24h Trading Volume (USD) |
|----------------|-------------|------------------|----------------|-------------------|--------------------|--------------------------|
| Hyperliquid   | 27.24      | 6.49B           | N/A           | N/A              | N/A               | 208.7M                  |
| GMX           | N/A        | N/A             | 240.46M       | 64,619           | 1,763             | 331.33M (notional)      |
| dYdX          | N/A        | N/A             | 218.04M       | 11,481           | 1,678             | N/A                     |
| Vertex        | N/A        | N/A             | 0.056M        | 0                | N/A               | N/A                     |
| Jupiter       | N/A        | N/A             | N/A           | N/A              | N/A               | 25.76M (token)          |

## Funding History
No data available.

Reasoning: The provided results do not include any funding details (e.g., VC rounds, raises). Hyperliquid may have raised funds as a DeFi project, but without sources, this cannot be detailed.

## Team Background
No data available.

Reasoning: No information on founders, team members, or backgrounds is in the results. Typically, I'd research key figures, but limitations prevent this.

## Social Sentiment
No data available.

Reasoning: Results lack social metrics (e.g., Twitter mentions, sentiment scores). The citation rules mention X.com for sentiment, but no such data is provided here.

## Key Risks
Based on available data and general knowledge of perps platforms, key risks include:

- **Data Gaps and Volatility**: With missing metrics like TVL and open interest, it's hard to gauge protocol health; the +4.3% 24h price gain suggests momentum, but without longer-term data, volatility risk is high (reasoning: Inferred from partial price data).
- **Competition**: GMX shows higher trading volume (331M vs. Hyperliquid's 209M) and TVL (240M), indicating stronger adoption; Hyperliquid's large market cap (6.49B) could be overvalued without supporting protocol data (reasoning: Direct comparison from table).
- **Regulatory and Operational Risks**: As a perps exchange, risks include funding rate manipulations or liquidation cascades, but no specific data confirms this.
- **Limited Insights**: Overall, the absence of on-chain metrics raises risks of incomplete evaluation—users should seek additional sources.

This report is constrained by data availability; for a fuller picture, more comprehensive sources are recommended. All figures are as of ~2026-02-25 04:45 UTC. [coingecko](https://www.coingecko.com/en/coins/hyperliquid). [tokenterminal](https://tokenterminal.com/explorer/projects/hyperliquid). [tokenterminal](https://tokenterminal.com/explorer/projects/gmx). [tokenterminal](https://tokenterminal.com/explorer/projects/dydx). [tokenterminal](https://tokenterminal.com/explorer/projects/vertex-protocol).