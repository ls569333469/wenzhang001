"""
测试5种不同开头风格，用同一篇素材生成5个版本
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import get_api_key
from app.core.llm import generate_text

api_key = get_api_key("doubao")

# 用NBA素材测试
article = """据官方公告，NBA球星扬尼斯·安特托昆博（Giannis Antetokounmpo，字母哥）正式成为CFTC监管的预测市场平台Kalshi的投资者和品牌大使。这使他成为首位直接投资预测市场行业的NBA球员。
Kalshi目前估值约110亿美元，字母哥的持股比例不到1%。
值得注意的是，这一投资发生在2026年NBA赌球丑闻曝光约100天后。该丑闻涉及昌西·比卢普斯和特里·罗齐尔等球员。
NBA规定球员可持有博彩类企业不超过1%的被动股份。尽管Kalshi强调自己是受监管的金融交易所而非博彩平台，但该平台允许用户就体育事件进行预测交易。这意味着字母哥的职业生涯本身可以成为Kalshi上的交易标的，从而引发潜在的利益冲突问题。"""

# 5种开头风格
styles = [
    {
        "name": "冷陈述",
        "instruction": "开头直接用最荒谬的事实平铺直叙，不加感叹号，不喊叫。用反差感制造讽刺。例如：'字母哥刚投了个预测市场。他自己的比赛就是上面的交易标的。'",
    },
    {
        "name": "反问切入",
        "instruction": "开头用一个反问句，让读者自己感受荒谬，不用感叹号。例如：'NBA球员投资一个能赌自己比赛的平台，联盟觉得没问题？'",
    },
    {
        "name": "类比开场",
        "instruction": "开头用一个日常生活的类比/比喻，让复杂的事情秒懂。例如：'这就好比裁判买了赌场的股份，然后说放心，我不会偏哨。'",
    },
    {
        "name": "轻描淡写反讽",
        "instruction": "开头越淡越好，把两个关键事实并列放在一起，讽刺感自己出来。例如：'字母哥成了第一个投资预测市场的NBA球员。距离上次赌球丑闻，刚好100天。'",
    },
    {
        "name": "随口爆料",
        "instruction": "像跟朋友随口说个事，不喊不叫，语气自然。例如：'说个事，易理华的地址和那个内幕巨鲸，用的同一个币安存款地址。'",
    },
]

system_prompt = """你是独立内容创作者，风格真实、自然、带感情：像和朋友聊天吐槽、分享感悟或点评时事。
不中立、不端水、不写报告。用你的视角重新讲故事。

核心任务：
把输入的媒体文章彻底变成你的原创短评。
- 只提取核心事实和本质。
- 完全抛弃原文结构、句子、语气、视角。
- 用全新角度、画面感、情绪重新创作：可以吐槽、感慨、自嘲、讽刺、联想历史、脑洞未来。
- 读起来必须有血有肉、有温度，像真人写的，而不是AI或新闻复述。

风格强制：
- 短句为主（5–18字），多用句号，换行自然。
- 至少1–2个生动比喻、场景描述或情绪爆发。
- 每段1–3句，节奏感强。
- 不要用感叹号开头，不要一惊一乍。

严禁：
- 抄原文任何句子/短语，哪怕改一个字。
- 新闻腔、中立分析、首先其次最后。
- 长句、破折号、分号。
- 废词：赋能、驱动、至关重要、值得注意、综上。
- 开头用"我靠""绝了""我去"等夸张感叹词。"""

results = []
for i, style in enumerate(styles, 1):
    print(f"\n{'='*60}")
    print(f"[{i}/5] {style['name']}")
    
    user_prompt = f"""素材：
{article}

开头风格：{style['instruction']}

直接写。200字左右。第一句就是上述风格的开头，别铺垫，别喊叫。"""

    try:
        text = generate_text(
            prompt=user_prompt,
            api_key=api_key,
            provider="volcengine",
            temperature=0.88,
            system_prompt=system_prompt,
            max_tokens=500,
        )
        # 简单后处理
        import re
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = text.strip()
        results.append({"name": style["name"], "text": text, "chars": len(text)})
        print(f"  ✅ {len(text)}字")
        print(f"  开头: {text[:60]}...")
    except Exception as e:
        print(f"  ❌ {e}")
        results.append({"name": style["name"], "text": f"[失败: {e}]", "chars": 0})

# 输出 MD
md = "# 5种开头风格对比测试\n\n"
md += "> 素材：NBA球员字母哥投资预测市场Kalshi\n"
md += "> 模型：doubao-seed-1.8 | temperature: 0.88\n\n---\n\n"

for r in results:
    md += f"## {r['name']}（{r['chars']}字）\n\n"
    md += f"{r['text']}\n\n---\n\n"

with open('scripts/test_opening_styles.md', 'w', encoding='utf-8') as f:
    f.write(md)

print(f"\n{'='*60}")
print("完成！查看: scripts/test_opening_styles.md")
