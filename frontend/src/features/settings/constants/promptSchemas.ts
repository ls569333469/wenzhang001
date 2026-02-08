export const OUTPUT_FORMATS: Record<string, string> = {
    hot_take: `
## 📤 输出格式
\`\`\`json
{
  "candidates": [
    {"id": 1, "content": "锐评内容...", "word_count": 85},
    {"id": 2, "content": "锐评内容...", "word_count": 92},
    {"id": 3, "content": "锐评内容...", "word_count": 78}
  ]
}
\`\`\``,
    short_article: `
## 📤 输出
直接输出完整短文，无需JSON格式。字数贴近目标值 (50-300字)。`,
    mid_article: `
## 📤 输出
直接输出完整文章，包含标题。无需JSON格式。`,
    long_article: `
## 📤 输出
直接输出完整文章，包含标题。请确保使用 Markdown 格式优化排版。`,
    tutorial: `
## 📤 输出
直接输出完整教程，包含标题。请确保步骤清晰，代码块格式正确。`,
    rewrite: `
## 📤 输出
直接输出改写后的内容。`,
    strategist: `
## 📤 Output Format (JSON only)
\`\`\`json
{
    "info_anchors": {
        "must_mention": ["list of entities/facts that MUST appear"],
        "key_data": ["important numbers, dates, or statistics"],
        "can_extend": ["topics the writer can elaborate on"]
    },
    "title_candidates": [
        {
            "title": "[Unique Title 1]",
            "formula_tags": ["Formula Name"],
            "hook_score": 85,
            "rationale": "[Why it works]"
        }
        // ... exactly 3 titles
    ],
    "options": [
        {
            "id": "option_1",
            "title": "Strategy Title 1",
            "hook_angle": "Angle 1",
            "pain_point": "Target Pain Point",
            "target_audience": "Audience",
            "outline": ["Point 1", "Point 2", "Point 3"],
            "viral_score": {
                "emotion_resonance": 85,
                "info_density": 70,
                "call_to_action": 80,
                "social_currency": 75,
                "overall": 78
            }
        },
        // ... option_2, option_3
    ],
    "style_notes": "Style observations"
}
\`\`\``
};
