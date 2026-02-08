"""
测试3种结尾风格 × 2篇素材 = 6个版本
开头也用之前验证过的好风格（冷陈述/反问/随口），不一惊一乍
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import get_api_key
from app.core.llm import generate_text

api_key = get_api_key("doubao")

articles = [
    {
        "name": "NBA/Kalshi",
        "content": """据官方公告，NBA球星字母哥正式成为CFTC监管的预测市场平台Kalshi的投资者和品牌大使。这使他成为首位直接投资预测市场行业的NBA球员。Kalshi目前估值约110亿美元，字母哥的持股比例不到1%。这一投资发生在2026年NBA赌球丑闻曝光约100天后。NBA规定球员可持有博彩类企业不超过1%的被动股份。尽管Kalshi强调自己是受监管的金融交易所而非博彩平台，但该平台允许用户就体育事件进行预测交易。字母哥的职业生涯本身可以成为Kalshi上的交易标的。"""
    },
    {
        "name": "易理华/巨鲸",
        "content": """链上分析平台Lookonchain监测发现，知名投资人易理华旗下的Trend Research与此前被标记为"BTC OG内幕巨鲸"的地址使用了同一个币安存款地址。约一天前，Trend Research将798.9万USDT转入一个中转地址，随后该资金被转入一个币安热钱包。紧接着，"BTC OG内幕巨鲸"的地址也将约1万枚ETH转入同一中转地址，最终同样流入该币安热钱包。两个地址共享相同的币安存款地址，且转账路径高度重合，暗示它们可能由同一实体控制。"""
    },
]

endings = [
    {
        "name": "说完就停",
        "instruction": "结尾：说完最后一个事实或判断就直接停。不总结，不升华，不硬凹金句，不用比喻收尾。像聊天聊到这里自然断了。",
    },
    {
        "name": "留个问题",
        "instruction": "结尾：留一个没有答案的问题或悬念，不回答它。把思考权交给读者，让他们自己琢磨。不要用反问句喊口号。",
    },
    {
        "name": "画面收束",
        "instruction": "结尾：用一个具体的小画面或细节收束，不做任何评价。让画面本身传达情绪。比如具体的时间、数字、动作。",
    },
]

system_prompt = """你是独立内容创作者，风格真实、自然、带感情：像和朋友聊天吐槽、分享感悟或点评时事。
不中立、不端水、不写报告。用你的视角重新讲故事。

核心任务：把输入的媒体文章变成你的原创短评。
- 只提取核心事实和本质。
- 完全抛弃原文结构、句子、语气、视角。
- 用全新角度、画面感、情绪重新创作。

风格：
- 短句为主（5–18字），多用句号。
- 每段1–3句。
- 开头不要喊叫，不要感叹号起手。用冷陈述、反问或随口说的方式开始。

严禁：
- 抄原文任何句子。
- 新闻腔、中立分析。
- 长句、破折号、分号。
- 开头用"我靠""绝了""我去"等夸张词。
- 结尾硬凹金句、硬塞比喻、强行升华。
- 废词：赋能、驱动、至关重要、值得注意、综上。"""

results = []
for art in articles:
    for ending in endings:
        label = f"{art['name']} × {ending['name']}"
        print(f"\n{'='*50}")
        print(f"🎯 {label}")
        
        user_prompt = f"""素材：
{art['content']}

{ending['instruction']}

直接写。200字左右。"""

        try:
            text = generate_text(
                prompt=user_prompt,
                api_key=api_key,
                provider="volcengine",
                temperature=0.88,
                system_prompt=system_prompt,
                max_tokens=500,
            )
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            results.append({"label": label, "ending": ending["name"], "article": art["name"], "text": text, "chars": len(text)})
            print(f"  ✅ {len(text)}字")
            # 打印最后一句（结尾风格关键）
            last_line = [l for l in text.split('\n') if l.strip()][-1] if text else ""
            print(f"  结尾: ...{last_line[-40:]}")
        except Exception as e:
            print(f"  ❌ {e}")
            results.append({"label": label, "ending": ending["name"], "article": art["name"], "text": f"[失败: {e}]", "chars": 0})

# 输出 MD
md = "# 3种结尾风格对比测试\n\n"
md += "> 测试素材：NBA/Kalshi + 易理华/巨鲸\n"
md += "> 开头：不喊叫，冷陈述/反问/随口\n"
md += "> 模型：doubao-seed-1.8 | temperature: 0.88\n\n"

for art_name in ["NBA/Kalshi", "易理华/巨鲸"]:
    md += f"---\n\n## 素材：{art_name}\n\n"
    for r in results:
        if r["article"] == art_name:
            md += f"### {r['ending']}（{r['chars']}字）\n\n"
            md += f"{r['text']}\n\n"

with open('scripts/test_ending_styles.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f"\n{'='*50}")
print("完成！查看: scripts/test_ending_styles.md")
