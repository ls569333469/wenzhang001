"""
跨篇重复词汇审计 — 找出30篇文章中多篇重复出现的词汇/短语
目的：发现 AI 写作的「模板指纹」，即 LLM 反复使用的固定搭配
"""
import re
import jieba
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

REPORT_PATH = Path(__file__).parent.parent / "reports" / "batch_test_results.md"
OUTPUT_PATH = Path(__file__).parent.parent / "reports" / "ai_repetition_audit.md"

# 停用词：常见中文虚词、连词、介词、代词等（不算重复）
STOPWORDS = set("""
的 了 在 是 和 也 都 就 不 有 对 把 被 从 到 所 以 但 而 与 或
这 那 其 它 他 她 我 你 们 自 之 于 为 上 下 中 内 外 前 后 个
一 二 三 四 五 六 七 八 九 十 百 千 万 亿
啊 吧 呢 嘛 吗 呀 哦 嗯 哈 哎 嘿 啦
的话 这个 那个 什么 怎么 如何 多少 哪个 哪些 为什么
没有 不是 不会 可以 能够 已经 正在 可能 应该 需要
因为 所以 如果 虽然 但是 然而 而且 并且 或者 还是
比较 非常 特别 相当 尤其 实在 确实 简直
只是 只有 只要 除了 关于 对于 通过 根据 按照
一个 一种 一些 这些 那些 这种 那种
开始 进行 出现 成为 认为 表示 包括 属于 实现 提供
现在 目前 这次 这里 那里 还有 同时 另外 此外
整个 所有 任何 每个 各种
可能 一定 必须 应该 需要
最终 最后 其实 毕竟 反正
就是 不过 然后 所以 因此 于是
比如 例如 譬如
甚至 尤其 特别 尤为
以及 还有 同时 另外
之前 之后 以前 以后
虽然 尽管 即使 哪怕
如果 假如 万一 无论 不管
又 再 还 已 正 将 要 会 能 得
而 且 却 倒 偏 竟 居然
让 给 向 往 朝 跟 把 被
才 更 最 太 很 好 真
做 说 看 想 去 来 走
大 小 多 少 新 老 长 短 高 低 好 坏
人 事 时 年 天 地 方 面
里 间 回 次
等 等等 之类
""".split())

# 额外停用：加密/Web3行业通用词（高频但不算AI模板词）
DOMAIN_COMMON = set("""
比特币 以太坊 加密 加密货币 区块链 代币 项目 市场 行业
散户 机构 资金 价格 交易 投资 用户 平台 钱包
美元 流动性 筹码 ETF ETH BTC
""".split())


def parse_articles(text: str) -> list:
    """从 batch_test_results.md 中提取每篇文章"""
    articles = []
    runs = re.split(r"## 第 (\d+) 次生成", text)
    for i in range(1, len(runs) - 1, 2):
        run_id = int(runs[i])
        block = runs[i + 1]
        m = re.search(r"### 内容\s*\n(.*?)(?=\n### AI词汇检查|\Z)", block, re.DOTALL)
        if not m:
            continue
        content = m.group(1).strip()
        versions = re.split(r"## 版本(\d+)：(.+?)（(\d+)字）", content)
        for j in range(1, len(versions) - 3, 4):
            ver_num = int(versions[j])
            ver_label = versions[j + 1]
            ver_text = versions[j + 3].strip().rstrip("---").strip()
            articles.append({
                "id": f"轮{run_id}-V{ver_num}",
                "run_id": run_id,
                "version": ver_num,
                "label": ver_label,
                "text": ver_text,
            })
    return articles


def extract_words(text: str) -> list:
    """jieba 分词，过滤停用词和短词"""
    words = jieba.lcut(text)
    result = []
    for w in words:
        w = w.strip()
        if len(w) < 2:
            continue
        if w in STOPWORDS or w in DOMAIN_COMMON:
            continue
        # 排除纯ASCII/数字/标点
        if re.match(r'^[a-zA-Z0-9\s\.\,\!\?\-\—\…\：\、\"\"\'\'\（\）\[\]\d]+$', w):
            continue
        result.append(w)
    return result


def extract_bigrams(text: str) -> list:
    """提取双词组合 (bigram)"""
    words = extract_words(text)
    return [f"{words[i]}+{words[i+1]}" for i in range(len(words)-1)]


def extract_phrases(text: str) -> list:
    """提取 3-8 字连续短语（基于原文滑动窗口）"""
    # 按句子拆分
    sentences = re.split(r'[。！？\n]', text)
    phrases = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 4:
            continue
        # 3-8字滑动窗口
        for length in range(3, min(9, len(sent) + 1)):
            for start in range(len(sent) - length + 1):
                phrase = sent[start:start+length]
                # 排除纯标点/数字
                if re.match(r'^[\d\s\.\,\!\?\-\—\…\：\、\"\"\'\'\（\）]+$', phrase):
                    continue
                phrases.append(phrase)
    return phrases


def main():
    raw = REPORT_PATH.read_text(encoding="utf-8")
    articles = parse_articles(raw)
    print(f"📄 解析到 {len(articles)} 篇文章")

    # ===== 1. 单词文档频率 (DF) =====
    word_df = defaultdict(set)           # word -> set of article IDs
    word_tf_total = Counter()            # word -> total count across all
    article_words = {}                   # article_id -> set of words

    for a in articles:
        words = extract_words(a["text"])
        unique_words = set(words)
        article_words[a["id"]] = unique_words
        for w in unique_words:
            word_df[w].add(a["id"])
        word_tf_total.update(words)

    # ===== 2. 短语跨篇重复 =====
    phrase_df = defaultdict(set)         # phrase -> set of article IDs
    for a in articles:
        seen = set()
        phrases = extract_phrases(a["text"])
        for p in phrases:
            if p not in seen:
                phrase_df[p].add(a["id"])
                seen.add(p)

    # ===== 3. 双词组合 (bigram) 跨篇重复 =====
    bigram_df = defaultdict(set)
    for a in articles:
        bigrams = set(extract_bigrams(a["text"]))
        for b in bigrams:
            bigram_df[b].add(a["id"])

    # ===== 生成报告 =====
    lines = []
    lines.append("# 跨篇重复词汇审计报告\n")
    lines.append(f"> 审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 审计范围: {len(articles)} 篇文章 | 检测维度: 单词DF + 短语重复 + 双词组合")
    lines.append(f"> 说明: 找出AI反复使用的「模板指纹」词汇和固定搭配\n")
    lines.append("---\n")

    # == 高DF单词 (出现在5+篇以上) ==
    lines.append("## 🔴 高频重复词（出现在5篇以上）\n")
    lines.append("> 这些词被AI在多篇不同素材的文章中反复使用，可能是AI的「默认词汇库」\n")
    high_df = [(w, ids) for w, ids in word_df.items() if len(ids) >= 5]
    high_df.sort(key=lambda x: -len(x[1]))

    if high_df:
        lines.append("| 词汇 | 出现篇数 | 总次数 | 出现在 |")
        lines.append("|---|---|---|---|")
        for word, ids in high_df:
            runs = sorted(set(aid.split("-")[0] for aid in ids))
            lines.append(f"| **{word}** | {len(ids)}/{len(articles)} | {word_tf_total[word]} | {', '.join(runs)} |")
    else:
        lines.append("✅ 无词汇出现在5篇以上\n")
    lines.append("")

    # == 中频重复词 (3-4篇) ==
    lines.append("## 🟡 中频重复词（出现在3-4篇）\n")
    mid_df = [(w, ids) for w, ids in word_df.items() if 3 <= len(ids) <= 4]
    mid_df.sort(key=lambda x: -len(x[1]))

    if mid_df:
        lines.append("| 词汇 | 出现篇数 | 总次数 | 出现在 |")
        lines.append("|---|---|---|---|")
        for word, ids in mid_df:
            runs = sorted(set(aid.split("-")[0] for aid in ids))
            lines.append(f"| {word} | {len(ids)}/{len(articles)} | {word_tf_total[word]} | {', '.join(runs)} |")
    else:
        lines.append("✅ 无\n")
    lines.append("")

    # == 跨篇重复短语 (3+篇) ==
    lines.append("## 🔥 跨篇重复短语（3篇以上出现完全相同的3-8字短语）\n")
    lines.append("> 这些是AI在不同文章中使用了完全相同的表达，是最强的模板指纹\n")
    repeat_phrases = [(p, ids) for p, ids in phrase_df.items() if len(ids) >= 3 and len(p) >= 3]
    # 去重：如果一个短语是另一个更长短语的子串且覆盖相同文章，保留长的
    repeat_phrases.sort(key=lambda x: (-len(x[1]), -len(x[0])))

    # 简单去重：只保留不被更长短语完全包含的
    filtered = []
    for p, ids in repeat_phrases:
        is_sub = False
        for fp, fids in filtered:
            if p in fp and ids <= fids:
                is_sub = True
                break
        if not is_sub:
            filtered.append((p, ids))

    if filtered[:30]:
        lines.append("| 短语 | 出现篇数 | 出现在 |")
        lines.append("|---|---|---|")
        for phrase, ids in filtered[:30]:
            runs = sorted(set(aid.split("-")[0] for aid in ids))
            lines.append(f"| 「{phrase}」 | {len(ids)} | {', '.join(runs)} |")
    else:
        lines.append("✅ 无跨篇重复短语\n")
    lines.append("")

    # == 跨篇重复双词组合 (5+篇) ==
    lines.append("## 🧩 高频双词组合（5篇以上）\n")
    lines.append("> 两个词连续出现在5+篇文章中，暴露AI的固定搭配习惯\n")
    high_bigrams = [(b, ids) for b, ids in bigram_df.items() if len(ids) >= 5]
    high_bigrams.sort(key=lambda x: -len(x[1]))

    if high_bigrams:
        lines.append("| 双词组合 | 出现篇数 | 出现在 |")
        lines.append("|---|---|---|")
        for bigram, ids in high_bigrams[:20]:
            w1, w2 = bigram.split("+")
            runs = sorted(set(aid.split("-")[0] for aid in ids))
            lines.append(f"| {w1} {w2} | {len(ids)} | {', '.join(runs)} |")
    else:
        lines.append("✅ 无\n")
    lines.append("")

    # == 按轮次的词汇多样性 ==
    lines.append("## 📈 各轮词汇多样性\n")
    lines.append("> TTR = 不重复词数 / 总词数，越高越多样\n")
    lines.append("| 轮次 | V1 TTR | V2 TTR | V3 TTR | 三版本重叠词占比 |")
    lines.append("|---|---|---|---|---|")

    for run_id in range(1, 11):
        run_articles = [a for a in articles if a["run_id"] == run_id]
        ttrs = []
        word_sets = []
        for a in sorted(run_articles, key=lambda x: x["version"]):
            words = extract_words(a["text"])
            ttr = len(set(words)) / max(len(words), 1)
            ttrs.append(f"{ttr:.2f}")
            word_sets.append(set(words))

        if len(word_sets) == 3:
            overlap = word_sets[0] & word_sets[1] & word_sets[2]
            total_unique = word_sets[0] | word_sets[1] | word_sets[2]
            overlap_pct = f"{len(overlap) / max(len(total_unique), 1) * 100:.0f}%"
        else:
            overlap_pct = "N/A"

        lines.append(f"| 轮{run_id} | {' | '.join(ttrs)} | {overlap_pct} |")
    lines.append("")

    # == 三版本间的同义重复（同一轮内） ==
    lines.append("## 🔄 同轮三版本共用词汇 Top 15\n")
    lines.append("> 同一轮的3个版本都使用了相同的词，说明AI在不同角度间缺乏词汇变化\n")

    intra_overlap = Counter()
    for run_id in range(1, 11):
        run_arts = [a for a in articles if a["run_id"] == run_id]
        if len(run_arts) < 3:
            continue
        sets = [set(extract_words(a["text"])) for a in sorted(run_arts, key=lambda x: x["version"])]
        common = sets[0] & sets[1] & sets[2]
        for w in common:
            intra_overlap[w] += 1

    lines.append("| 词汇 | 出现在几轮的3版本中 | 说明 |")
    lines.append("|---|---|---|")
    for word, count in intra_overlap.most_common(15):
        note = "⚠️ 高频模板词" if count >= 5 else ""
        lines.append(f"| **{word}** | {count}/10轮 | {note} |")
    lines.append("")

    lines.append("---\n")
    lines.append("## 💡 结论\n")
    lines.append("以上词汇如果在不相关的素材中反复出现，说明是AI的「默认词汇库」而非素材需要。")
    lines.append("建议将最高频的跨篇重复词加入 P25 禁止列表进行下一轮测试。\n")

    report = "\n".join(lines)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")

    print(f"\n📝 报告: {OUTPUT_PATH}")
    print(f"🔴 高DF词: {len(high_df)} 个")
    print(f"🟡 中DF词: {len(mid_df)} 个")
    print(f"🔥 重复短语: {len(filtered[:30])} 个")
    if high_df:
        print(f"   Top5: {', '.join(f'{w}({len(ids)}篇)' for w, ids in high_df[:5])}")


if __name__ == "__main__":
    main()
