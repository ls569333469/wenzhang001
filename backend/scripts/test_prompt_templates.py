"""
测试 4 种业界主流提示词模板：长文→短篇内容提炼
对比我们的 short_article writer vs 4 种外部模板

模板1: 结构化提炼 + 输出格式锁死
模板2: 钩子优先 + 情绪放大法
模板3: Chain of Density 密度链法
模板4: 暴力懒人版
"""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests
from bs4 import BeautifulSoup
from app.core.llm import generate_text

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ============================================================
# 4 种提示词模板
# ============================================================

TEMPLATE_1_STRUCTURED = """你是一位顶级内容提炼专家，擅长把长文浓缩成高传播力的短内容。
核心任务：从下面文章中提取最有价值、最具冲击力/共鸣/争议/实用性的部分，压缩成短篇推文。

严格遵守以下规则：
- 只保留3–7个最核心点（多余的全部砍掉）
- 每个点必须独立可传播，能单独截图转发
- 优先选择：反常识、数据惊人、情绪共鸣、实用干货、可打脸、可争议、可 meme 化、可引发争论的内容
- 禁止写"值得思考""见仁见智""综合来看"等端水废话
- 语言要短、狠、抓眼球，第一句必须是钩子
- 语气：犀利/毒舌/专业但不枯燥

输出格式（必须严格遵守，不要多加任何废话）：
1. 先输出标题/钩子句（≤20字，最抓人）
2. 然后输出3–6条短内容（每条≤140字，最好≤100字）
3. 最后加1句挑衅/提问句，刺激互动

文章内容：
{article}"""

TEMPLATE_2_VIRAL = """任务：把这篇长文浓缩成能在X/小红书/朋友圈刷屏的短内容。
第一步：用一句话总结全文最炸裂/最反直觉/最能引发情绪的点，作为钩子（必须≤18字，能单独成条推文）
第二步：围绕这个钩子，提炼4–6个支撑/反转/例子/金句，每条独立成推文或笔记卡片
第三步：每条都要带情绪（震惊/愤怒/羡慕/心酸/打脸/偷笑等），禁止平淡叙述

输出结构：
【钩子】一句话
然后
1. 
2. 
3. 
...
最后加一句能引发大量回复的问题或挑衅

文章：
{article}"""

# 密度链法需要 2 步
TEMPLATE_3_COD_STEP1 = """阅读这篇文章，用5个 increasingly dense（越来越浓缩）的摘要逐步提炼核心信息。
每个摘要都要比上一个更短、更密集，但保留关键洞见。
格式：
摘要1（最长，≈100字）：
摘要2（≈70字）：
摘要3（≈50字）：
摘要4（≈30字）：
摘要5（最精华，≈15–20字）：

文章：
{article}"""

TEMPLATE_3_COD_STEP2 = """以下是一篇文章的5层递进浓缩摘要：

{step1_output}

摘要5是最浓缩的核心。现在基于它，创作一条极具传播力的短推文/笔记（≤280字），必须包含：
- 强钩子开头
- 1–2个最抓人的数据/例子/反转
- 情绪化语言
- 结尾带互动问题
目标：让人看完想立刻转发或评论。"""

TEMPLATE_4_BRUTEFORCE = """你是互联网最会做短内容的账号。用最大信息密度、最抓眼球的方式，把这篇文章浓缩成3条能独立刷屏的短推文/笔记。每条开头都要是炸裂钩子，直接输出，不要解释。

文章：
{article}"""


def scrape_article(url):
    """Scrape a wublock123 article"""
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    title_tag = soup.title
    title = title_tag.string if title_tag else ''
    title = re.sub(r'\s*-\s*(深度|行情|矿业|监管|交易所|DeFi|NFT)\s*-\s*吴说.*$', '', title).strip()
    
    content_el = soup.select_one('.entry-content')
    if not content_el:
        return None
    
    for tag in content_el.find_all(['script', 'style', 'nav']):
        tag.decompose()
    
    raw_text = content_el.get_text(separator='\n')
    lines = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line or len(line) < 5:
            continue
        if '根据央行等部门发布' in line:
            break
        if '风险提示' in line:
            break
        if line.startswith('声明：'):
            continue
        if line.startswith('原文链接：'):
            continue
        lines.append(line)
    
    return {
        'title': title,
        'url': url,
        'content': '\n'.join(lines),
    }


def call_llm(prompt, max_tokens=800):
    """Direct LLM call using app config"""
    from app.core.config import get_api_key
    api_key = get_api_key("doubao")
    result = generate_text(
        prompt=prompt,
        api_key=api_key,
        provider="volcengine",
        max_tokens=max_tokens,
        temperature=0.8
    )
    return result


def run_template_1(article_text):
    """结构化提炼 + 输出格式锁死"""
    prompt = TEMPLATE_1_STRUCTURED.format(article=article_text)
    return call_llm(prompt, max_tokens=600)


def run_template_2(article_text):
    """钩子优先 + 情绪放大"""
    prompt = TEMPLATE_2_VIRAL.format(article=article_text)
    return call_llm(prompt, max_tokens=600)


def run_template_3(article_text):
    """Chain of Density 密度链法（2步）"""
    # Step 1: 生成5层摘要
    prompt1 = TEMPLATE_3_COD_STEP1.format(article=article_text)
    step1_result = call_llm(prompt1, max_tokens=500)
    
    # Step 2: 基于最精华摘要创作
    prompt2 = TEMPLATE_3_COD_STEP2.format(step1_output=step1_result)
    step2_result = call_llm(prompt2, max_tokens=400)
    
    return f"=== 密度链 Step1（5层摘要）===\n{step1_result}\n\n=== 密度链 Step2（最终输出）===\n{step2_result}"


def run_template_4(article_text):
    """暴力懒人版"""
    prompt = TEMPLATE_4_BRUTEFORCE.format(article=article_text)
    return call_llm(prompt, max_tokens=500)


if __name__ == '__main__':
    # 使用 batch2 中内容最丰富的 3 篇文章
    urls = [
        "https://www.wublock123.com/article/6/56363",  # NBA球员投资 Kalshi (393字)
        "https://www.wublock123.com/article/6/56359",  # Bithumb 110% 赔偿 (284字)
        "https://www.wublock123.com/article/6/56355",  # 易理华巨鲸同地址 (264字)
    ]
    
    templates = [
        ("模板1_结构化提炼", run_template_1),
        ("模板2_钩子情绪", run_template_2),
        ("模板3_密度链", run_template_3),
        ("模板4_暴力版", run_template_4),
    ]
    
    print("=" * 60)
    print("提示词模板对比测试")
    print("=" * 60)
    
    all_results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"[文章 {i}/3] 正在爬取: {url}")
        article = scrape_article(url)
        if not article:
            print("  ❌ 爬取失败")
            continue
        
        print(f"  标题: {article['title']}")
        print(f"  字数: {len(article['content'])} 字")
        
        article_results = {
            "title": article['title'],
            "url": url,
            "source_chars": len(article['content']),
            "templates": {}
        }
        
        for name, func in templates:
            print(f"\n  --- 运行 {name} ---")
            try:
                output = func(article['content'])
                print(f"  ✅ 完成 ({len(output)} 字)")
                article_results["templates"][name] = output
            except Exception as e:
                print(f"  ❌ 错误: {e}")
                article_results["templates"][name] = f"ERROR: {e}"
        
        all_results.append(article_results)
    
    # 保存 JSON
    with open('scripts/test_prompt_templates.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown 报告
    md = "# 提示词模板对比测试报告\n\n"
    md += "> 测试时间：2026-02-08\n"
    md += "> 素材来源：吴说区块链\n"
    md += "> 测试模板：4种业界主流提示词模板\n\n---\n\n"
    
    for r in all_results:
        md += f"## {r['title']}\n\n"
        md += f"**原文字数**：{r['source_chars']} 字 | **来源**：{r['url']}\n\n"
        
        for tname, output in r['templates'].items():
            md += f"### {tname}（{len(output)} 字）\n\n"
            md += f"{output}\n\n---\n\n"
    
    with open('scripts/test_prompt_templates.md', 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"\n{'='*60}")
    print("完成！报告已保存:")
    print("  JSON: scripts/test_prompt_templates.json")
    print("  MD:   scripts/test_prompt_templates.md")
    print(f"{'='*60}")
