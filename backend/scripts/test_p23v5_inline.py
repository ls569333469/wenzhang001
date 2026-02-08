"""
P23v5 快速测试 - 使用内联素材直接调用 short_article_writer
避免爬虫连接问题
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.agents.writer.short_article import short_article_writer
from app.core.config import get_api_key

api_key = get_api_key("doubao")

# 直接用素材文本，不爬取
articles = [
    {
        "title": "NBA球员字母哥投资预测市场Kalshi",
        "content": """据官方公告，NBA球星扬尼斯·安特托昆博（Giannis Antetokounmpo，字母哥）正式成为CFTC监管的预测市场平台Kalshi的投资者和品牌大使。这使他成为首位直接投资预测市场行业的NBA球员。
Kalshi目前估值约110亿美元，字母哥的持股比例不到1%。
值得注意的是，这一投资发生在2026年NBA赌球丑闻曝光约100天后。该丑闻涉及昌西·比卢普斯和特里·罗齐尔等球员。
NBA规定球员可持有博彩类企业不超过1%的被动股份。尽管Kalshi强调自己是受监管的金融交易所而非博彩平台，但该平台允许用户就体育事件进行预测交易。这意味着字母哥的职业生涯本身可以成为Kalshi上的交易标的，从而引发潜在的利益冲突问题。"""
    },
    {
        "title": "Bithumb误发奖励事故110%赔偿",
        "content": """韩国第二大加密货币交易所Bithumb公布了其误发奖励事故的详细补偿方案。此前由于系统错误，大量异常奖励被错误发放给用户，导致部分用户在不知情的情况下以低于市价的价格卖出了持有的加密资产。
Bithumb估计此次事故造成的直接损失约为10亿韩元。补偿方案包括：
1. 对因事故低价卖出资产的用户，赔偿其差价损失的110%
2. 向事故期间在线的所有用户发放2万韩元现金红包
3. 全平台用户享受7天免交易手续费优惠
4. 设立1000亿韩元规模的客户保护基金
Bithumb表示将同步升级内部控制和验证系统，防止类似事故再次发生。"""
    },
    {
        "title": "易理华与BTC OG内幕巨鲸共用地址",
        "content": """链上分析平台Lookonchain监测发现，知名投资人易理华旗下的Trend Research与此前被标记为"BTC OG内幕巨鲸"的地址使用了同一个币安（Binance）存款地址。
具体操作轨迹显示：约一天前，Trend Research将798.9万USDT转入一个中转地址，随后该资金被转入一个币安热钱包。紧接着，被标记为"BTC OG内幕巨鲸"的地址也将约1万枚ETH转入同一中转地址，最终同样流入该币安热钱包。
两个地址共享相同的币安存款地址，且转账路径高度重合，暗示它们可能由同一实体控制或存在紧密的资金关联。"""
    },
]

results = []
for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/3] {art['title']} ({len(art['content'])}字)")
    
    state = {
        "raw_input": art['content'],
        "style": "mimeng",
        "narrative_type": "project_review",
        "api_config": {
            "provider": "volcengine",
            "api_key": api_key,
        },
        "strategy_json": "{}",
    }

    try:
        result = short_article_writer(state)
        draft = result.get("draft_content", "")
        variants = result.get("variants", [])

        article_result = {
            "source_title": art['title'],
            "source_chars": len(art['content']),
            "draft": draft,
            "draft_chars": len(draft),
            "variants": [{
                "label": v.get("label", ""),
                "methods": v.get("methods", []),
                "content": v.get("content", ""),
                "chars": v.get("char_count", 0),
            } for v in variants],
        }
        results.append(article_result)

        print(f"  ✅ {len(draft)} chars | {len(variants)} variants")
        for v in variants:
            print(f"    {v.get('label','')}: {v.get('char_count',0)} 字")
    except Exception as e:
        print(f"  ❌ 生成失败: {e}")

# 保存
with open('scripts/test_p23v5_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

md = "# P23v5 测试报告（群聊反应式 KOL 风格）\n\n"
md += "> 测试时间：2026-02-08\n"
md += "> 核心改变：从\"独立评论人写文章\" → \"老韭菜在群里聊天\"\n"
md += "> 对比基线：P23v4（评论+钩子版）\n\n---\n\n"

for r in results:
    md += f"## {r['source_title']}\n\n"
    md += f"**原文**：{r['source_chars']} 字\n\n"
    for v in r['variants']:
        md += f"### {v['label']}（{v['chars']} 字）\n"
        md += f"方法：{', '.join(v['methods'])}\n\n"
        md += f"{v['content']}\n\n---\n\n"

with open('scripts/test_p23v5_results.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f"\n{'='*60}")
print("P23v5 测试完成！")
print("  JSON: scripts/test_p23v5_results.json")
print("  MD:   scripts/test_p23v5_results.md")
