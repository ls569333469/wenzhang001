"""
P25 全面 AI 词汇审计 — 对 batch_test_results.md 中 30 篇文章做 7 类检查
覆盖 P25 禁止列表清单的全部类别
"""
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

# ===== 数据源 =====
REPORT_PATH = Path(__file__).parent.parent / "reports" / "batch_test_results.md"
OUTPUT_PATH = Path(__file__).parent.parent / "reports" / "ai_audit_report.md"

# ===== P25 禁止词完整清单（七大类） =====

# 一、标点禁止
CAT1_PUNCTUATION = {
    "——": "破折号（AI书面语标志）",
    "；": "分号（AI书面语标志）",
}

# 二、废话文学
CAT2_FILLER = {
    # 正确的废话
    "加密市场充满不确定性": "正确废话",
    "区块链技术正在快速发展": "正确废话",
    "在当前市场环境下": "正确废话",
    # 万能结尾
    "让我们拭目以待": "万能结尾",
    "后续值得关注": "万能结尾",
    "时间会给出答案": "万能结尾",
    "这会是": "万能结尾疑问",
    # 假装思考
    "这不禁让人思考": "假装思考",
    "值得深思": "假装思考",
    "引人深省": "假装思考",
    "不禁令人": "假装思考",
    # 骑墙表态
    "机遇与挑战并存": "骑墙表态",
    "有人看多有人看空": "骑墙表态",
    "各有利弊": "骑墙表态",
    # 注水过渡
    "众所周知": "注水过渡",
    "说到这里不得不提": "注水过渡",
    "事实上": "注水过渡",
    "值得一提的是": "注水过渡",
    "综上所述": "注水过渡",
    "不可否认": "注水过渡",
    "毋庸置疑": "注水过渡",
    # 科普
    "所谓": "科普常识",
}

# 三、商业咨询腔
CAT3_BIZ_HIGH = {
    "赛道": "高频AI商业词",
    "生态": "高频AI商业词",
    "布局": "高频AI商业词",
    "核心竞争力": "高频AI商业词",
    "底层逻辑": "高频AI商业词",
    "驱动": "高频AI商业词",
    "破局": "高频AI商业词",
    "差异化": "高频AI商业词",
    "治理错位": "高频AI商业词",
    "迫在眉睫": "高频AI商业词",
    "技术迭代": "高频AI商业词",
    "说白了": "AI伪口语",
    "从来都不是": "AI反转句式",
}

CAT3_BIZ_MID = {
    "圈层": "中频AI词",
    "触达": "中频AI词",
    "链接": "中频AI词",
    "精准": "中频AI词",
    "适配": "中频AI词",
    "核心价值": "中频AI词",
    "顶层设计": "中频AI词",
    "战略布局": "中频AI词",
    "赋能": "中频AI词",
    "解锁": "中频AI词",
    "精准匹配": "中频AI词",
    "本质是": "中频AI词",
    "自循环协作网络": "AI造词",
    "价值兑现路径": "AI造词",
    "隐性的网络扩张": "AI造词",
}

CAT3_BIZ_ENDINGS = [
    r"未来.{2,8}的竞争.{0,4}核心是.{2,8}的争夺",
    r"这给行业提了醒",
    r"这意味着.{2,10}的范式正在转变",
    r".{2,8}正在重新定义.{2,8}",
    r"答案会自己浮出来",
    r"别做.{2,8}里的被动者",
    r"能不能成为破局密钥",
]

# 四、结构禁止
CAT4_STRUCTURE = [
    (r"首先.{5,60}其次.{5,60}最后", "首先…其次…最后… 排列模板"),
    (r"首先.{5,60}其次.{5,60}第三", "首先…其次…第三… 排列模板"),
    (r"第一.{5,60}第二.{5,60}第三", "第一…第二…第三… 排列模板"),
    (r"一方面.{5,60}另一方面", "一方面…另一方面… 对称模板"),
]

# 五、思维禁止
CAT5_THINKING = {
    "分析显示": "分析师点评语气",
    "从数据来看": "分析师点评语气",
    "数据表明": "分析师点评语气",
    "研究表明": "分析师点评语气",
    "有分析人士指出": "分析师点评语气",
    "业内人士表示": "分析师点评语气",
}

# 七、屏蔽词（硬性）
CAT7_HARD_BAN = {
    "庄哥": "硬性屏蔽",
    "庄家": "硬性屏蔽",
    "币圈": "硬性屏蔽",
    "韭菜": "硬性屏蔽",
    "割韭菜": "硬性屏蔽",
    "凸显": "硬性屏蔽",
    "至关重要": "硬性屏蔽",
}

# 额外 AI 痕迹检测（补充）
CAT_EXTRA = {
    "深入探讨": "AI动词",
    "不可或缺": "AI形容词",
    "值得注意的是": "AI过渡",
    "需要指出的是": "AI过渡",
    "总而言之": "AI总结",
    "换言之": "AI过渡",
    "不言而喻": "AI过渡",
    "毫无疑问": "AI过渡",
    "显而易见": "AI过渡",
    "由此可见": "AI过渡",
    "与此同时": "AI过渡",
    "一言以蔽之": "AI总结",
    "归根结底": "AI总结",
    "无论如何": "AI过渡",
    "不难发现": "AI过渡",
    "进一步": "AI动词",
    "深度赋能": "AI动词",
    "助力": "AI动词",
    "引领": "AI动词",
    "聚焦": "AI动词",
    "探索": "AI动词",
    "打造": "AI动词",
    "构建": "AI动词",
    "全方位": "AI形容词",
    "多维度": "AI形容词",
    "高质量": "AI形容词",
    "可持续": "AI形容词",
    "一站式": "AI形容词",
    "新篇章": "AI修辞",
    "新征程": "AI修辞",
    "里程碑": "AI修辞",
    "风口": "AI修辞",
    "蓝海": "AI修辞",
    "红海": "AI修辞",
    "护城河": "AI修辞",
    "天花板": "AI修辞",
    "组合拳": "AI修辞",
    "杀手锏": "AI修辞",
}


def parse_articles(text: str) -> list:
    """从 batch_test_results.md 中提取每篇文章"""
    articles = []
    # 按 "## 第 N 次生成" 拆分
    runs = re.split(r"## 第 (\d+) 次生成", text)
    # runs[0] 是 header, 之后 [run_id, content, run_id, content, ...]
    for i in range(1, len(runs) - 1, 2):
        run_id = int(runs[i])
        block = runs[i + 1]

        # 提取 "### 内容" 到 "### AI词汇检查" 之间的文本
        m = re.search(r"### 内容\s*\n(.*?)(?=\n### AI词汇检查|\Z)", block, re.DOTALL)
        if not m:
            continue
        content = m.group(1).strip()

        # 进一步拆分 3 个版本
        versions = re.split(r"## 版本(\d+)：(.+?)（(\d+)字）", content)
        for j in range(1, len(versions) - 3, 4):
            ver_num = int(versions[j])
            ver_label = versions[j + 1]
            ver_text = versions[j + 3].strip().rstrip("---").strip()
            articles.append({
                "run_id": run_id,
                "version": ver_num,
                "label": ver_label,
                "text": ver_text,
                "char_count": len(ver_text)
            })

    return articles


def audit_article(article: dict) -> dict:
    """对单篇文章进行全面审计"""
    text = article["text"]
    findings = []

    # 一、标点禁止
    for word, desc in CAT1_PUNCTUATION.items():
        count = text.count(word)
        if count:
            findings.append(("一.标点", word, desc, count, "🔴严禁"))

    # 二、废话文学
    for word, desc in CAT2_FILLER.items():
        count = text.count(word)
        if count:
            findings.append(("二.废话", word, desc, count, "🟡警告"))

    # 三、商业咨询腔 — 高频
    for word, desc in CAT3_BIZ_HIGH.items():
        count = text.count(word)
        if count:
            findings.append(("三.商业高频", word, desc, count, "🔴严禁"))

    # 三、商业咨询腔 — 中频
    for word, desc in CAT3_BIZ_MID.items():
        count = text.count(word)
        if count:
            findings.append(("三.商业中频", word, desc, count, "🟡警告"))

    # 三、商业咨询腔 — 结尾模板
    for pattern in CAT3_BIZ_ENDINGS:
        m = re.search(pattern, text)
        if m:
            findings.append(("三.结尾模板", m.group(), "咨询报告结尾", 1, "🔴严禁"))

    # 四、结构禁止
    for pattern, desc in CAT4_STRUCTURE:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            findings.append(("四.结构", desc, "AI模板结构", 1, "🟡警告"))

    # 五、思维禁止
    for word, desc in CAT5_THINKING.items():
        count = text.count(word)
        if count:
            findings.append(("五.思维", word, desc, count, "🟡警告"))

    # 七、屏蔽词
    for word, desc in CAT7_HARD_BAN.items():
        count = text.count(word)
        if count:
            findings.append(("七.屏蔽词", word, desc, count, "🔴严禁"))

    # 额外 AI 痕迹
    for word, desc in CAT_EXTRA.items():
        count = text.count(word)
        if count:
            findings.append(("补充.AI痕迹", word, desc, count, "🟠注意"))

    # 评分
    red_count = sum(1 for f in findings if f[4] == "🔴严禁")
    yellow_count = sum(1 for f in findings if f[4] == "🟡警告")
    orange_count = sum(1 for f in findings if f[4] == "🟠注意")

    if red_count >= 3:
        grade = "🚨 不合格"
    elif red_count >= 1:
        grade = "❌ 需重写"
    elif yellow_count + orange_count >= 3:
        grade = "⚠️ 需润色"
    elif yellow_count + orange_count >= 1:
        grade = "⚠️ 可接受（有瑕疵）"
    else:
        grade = "✅ 合格"

    return {
        **article,
        "findings": findings,
        "red": red_count,
        "yellow": yellow_count,
        "orange": orange_count,
        "total_issues": len(findings),
        "grade": grade
    }


def main():
    # 读取
    raw = REPORT_PATH.read_text(encoding="utf-8")
    articles = parse_articles(raw)
    print(f"📄 解析到 {len(articles)} 篇文章")

    # 审计
    results = [audit_article(a) for a in articles]

    # ===== 生成报告 =====
    lines = []
    lines.append("# P25 AI 词汇全面审计报告\n")
    lines.append(f"> 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 审计范围: {len(articles)} 篇文章 (10轮×3版本)")
    lines.append(f"> 审计依据: P25 禁止列表清单 7大类 + 补充AI痕迹词库\n")
    lines.append("---\n")

    # == 总体汇总 ==
    grade_counter = Counter(r["grade"] for r in results)
    total_red = sum(r["red"] for r in results)
    total_yellow = sum(r["yellow"] for r in results)
    total_orange = sum(r["orange"] for r in results)

    lines.append("## 📊 总体评分\n")
    lines.append("| 评级 | 篇数 | 占比 |")
    lines.append("|---|---|---|")
    for grade in ["✅ 合格", "⚠️ 可接受（有瑕疵）", "⚠️ 需润色", "❌ 需重写", "🚨 不合格"]:
        count = grade_counter.get(grade, 0)
        pct = f"{count / len(results) * 100:.0f}%"
        lines.append(f"| {grade} | {count} | {pct} |")

    lines.append(f"\n**总命中数**: 🔴严禁 {total_red} | 🟡警告 {total_yellow} | 🟠注意 {total_orange}\n")
    lines.append("---\n")

    # == 按类别统计 ==
    cat_hits = defaultdict(lambda: Counter())
    for r in results:
        for cat, word, desc, count, level in r["findings"]:
            cat_hits[cat][word] += count

    lines.append("## 📋 按类别命中统计\n")
    for cat in sorted(cat_hits.keys()):
        hits = cat_hits[cat]
        lines.append(f"### {cat}\n")
        lines.append("| 词/模式 | 总命中次数 | 出现轮次 |")
        lines.append("|---|---|---|")
        # 收集出现轮次
        for word, total in hits.most_common():
            runs_hit = sorted(set(r["run_id"] for r in results if any(f[1] == word for f in r["findings"])))
            runs_str = ", ".join(str(r) for r in runs_hit)
            lines.append(f"| {word} | {total} | 轮{runs_str} |")
        lines.append("")

    lines.append("---\n")

    # == 全词频统计 Top 20 ==
    all_words = Counter()
    for r in results:
        for cat, word, desc, count, level in r["findings"]:
            all_words[word] += count

    lines.append("## 🔥 全词频 Top 20\n")
    lines.append("| 排名 | 词汇 | 总次数 | 类别 | 严重度 |")
    lines.append("|---|---|---|---|---|")
    for rank, (word, count) in enumerate(all_words.most_common(20), 1):
        # find category and level
        cat_info = ""
        level_info = ""
        for r in results:
            for cat, w, desc, c, level in r["findings"]:
                if w == word:
                    cat_info = cat
                    level_info = level
                    break
            if cat_info:
                break
        lines.append(f"| {rank} | **{word}** | {count} | {cat_info} | {level_info} |")
    lines.append("")

    lines.append("---\n")

    # == 逐篇详细审计 ==
    lines.append("## 📝 逐篇审计详情\n")

    for r in results:
        header = f"### 轮{r['run_id']}-版本{r['version']}「{r['label']}」{r['char_count']}字 → {r['grade']}\n"
        lines.append(header)

        if not r["findings"]:
            lines.append("✅ 无任何命中\n")
        else:
            lines.append("| 类别 | 词/模式 | 说明 | 次数 | 严重度 |")
            lines.append("|---|---|---|---|---|")
            for cat, word, desc, count, level in r["findings"]:
                # 长文本截断
                word_disp = word[:20] + "…" if len(word) > 20 else word
                lines.append(f"| {cat} | {word_disp} | {desc} | {count} | {level} |")
            lines.append("")

    lines.append("---\n")

    # == 建议 ==
    lines.append("## 💡 审计结论与建议\n")

    # 分析哪些词需要加入禁止
    new_candidates = []
    for word, count in all_words.most_common():
        # 找到类别
        for r in results:
            for cat, w, desc, c, level in r["findings"]:
                if w == word and level in ("🟠注意", "🟡警告") and count >= 3:
                    new_candidates.append((word, count, cat))
                    break
            else:
                continue
            break

    if new_candidates:
        lines.append("### 建议升级为严禁的词汇\n")
        lines.append("| 词汇 | 命中次数 | 当前类别 | 建议 |")
        lines.append("|---|---|---|---|")
        for word, count, cat in new_candidates:
            lines.append(f"| {word} | {count} | {cat} | → 升级为高频严禁 |")
        lines.append("")

    # 写入
    report = "\n".join(lines)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    # 终端输出
    print(f"\n{'='*60}")
    print(f"📊 审计完成: {len(articles)} 篇文章")
    print(f"{'='*60}")
    print(f"✅ 合格: {grade_counter.get('✅ 合格', 0)}")
    print(f"⚠️ 可接受: {grade_counter.get('⚠️ 可接受（有瑕疵）', 0)}")
    print(f"⚠️ 需润色: {grade_counter.get('⚠️ 需润色', 0)}")
    print(f"❌ 需重写: {grade_counter.get('❌ 需重写', 0)}")
    print(f"🚨 不合格: {grade_counter.get('🚨 不合格', 0)}")
    print(f"\n🔴严禁命中: {total_red} | 🟡警告: {total_yellow} | 🟠注意: {total_orange}")
    print(f"\n🔥 Top5: {', '.join(f'{w}({c})' for w, c in all_words.most_common(5))}")
    print(f"\n📝 报告: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
