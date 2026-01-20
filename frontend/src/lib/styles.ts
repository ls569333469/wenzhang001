// 叙事类型配置 - 决定"讲什么"
export interface NarrativeType {
    id: string
    name: string
    icon: string
    description: string
    structure: string[]  // 内容结构模板
    prompts: {
        intro: string
        body: string
        conclusion: string
    }
}

// 风格配置 - 决定"怎么讲"  
export interface StyleConfig {
    id: string
    name: string
    icon: string
    color: string
    description: string
}

// 叙事类型定义
export const NARRATIVE_TYPES: NarrativeType[] = [
    {
        id: "project_review",
        name: "项目评测",
        icon: "🔬",
        description: "深度分析项目，评估价值与风险",
        structure: ["背景介绍", "核心功能", "优缺点分析", "投资建议"],
        prompts: {
            intro: "以项目最新动态或亮点开场",
            body: "分析技术架构、团队背景、代币经济",
            conclusion: "给出明确的投资建议或评级"
        }
    },
    {
        id: "person_story",
        name: "人物故事",
        icon: "👤",
        description: "讲述人物经历，塑造人物形象",
        structure: ["引子/场景", "经历回顾", "转折/高光", "感悟/金句"],
        prompts: {
            intro: "以一个标志性场景或金句开场",
            body: "讲述关键经历和转折点",
            conclusion: "升华人物精神或价值观"
        }
    },
    {
        id: "market_analysis",
        name: "市场分析",
        icon: "📈",
        description: "解读市场动态，预判行情走势",
        structure: ["现象描述", "数据支撑", "逻辑推演", "趋势预测"],
        prompts: {
            intro: "以最新的市场现象或数据切入",
            body: "用数据和逻辑分析原因",
            conclusion: "给出趋势预测和操作建议"
        }
    },
    {
        id: "industry_critique",
        name: "行业批判",
        icon: "⚔️",
        description: "揭露行业问题，引发深度思考",
        structure: ["问题抛出", "案例揭露", "深层反思", "呼吁行动"],
        prompts: {
            intro: "以一个尖锐的问题或观点开场",
            body: "用案例和证据揭露问题",
            conclusion: "反思根源并呼吁改变"
        }
    },
    {
        id: "tutorial",
        name: "教程干货",
        icon: "📚",
        description: "实用教程，手把手教学",
        structure: ["痛点引入", "步骤详解", "避坑指南", "总结回顾"],
        prompts: {
            intro: "描述目标读者的痛点",
            body: "分步骤详细讲解操作方法",
            conclusion: "总结关键点并给出进阶建议"
        }
    }
]

// 核心风格 (已有)
export const CORE_STYLES: StyleConfig[] = [
    { id: "mimeng", name: "咪蒙体", icon: "🔥", color: "#ef4444", description: "情绪爆点" },
    { id: "banfo", name: "半佛体", icon: "🧠", color: "#8b5cf6", description: "反常识逻辑" },
    { id: "xinshixiang", name: "新世相体", icon: "💫", color: "#ec4899", description: "情感共鸣" },
    { id: "shijuezhi", name: "视觉志体", icon: "👁️", color: "#06b6d4", description: "简洁美学" },
]

// 扩展风格
export const EXTENDED_STYLES: StyleConfig[] = [
    { id: "lianbushou", name: "链捕手体", icon: "🔗", color: "#10b981", description: "专业深度" },
    { id: "lingongzi", name: "临公子体", icon: "💰", color: "#f59e0b", description: "投资干货" },
    { id: "fengqiongzi", name: "风茕子体", icon: "🌙", color: "#6366f1", description: "人性洞察" },
    { id: "chengshian", name: "程十安体", icon: "🌸", color: "#f472b6", description: "生活智慧" },
]

// 所有风格
export const ALL_STYLES = [...CORE_STYLES, ...EXTENDED_STYLES]

// 预设组合 (叙事+风格)
export interface CombinationConfig {
    id: string
    name: string
    description: string
    narrative: string  // 叙事类型 ID
    styles: { id: string; weight: number }[]  // 风格组合
}

export const COMBINATIONS: CombinationConfig[] = [
    {
        id: "project_eval",
        name: "项目评测",
        description: "专业分析 + 情绪点燃",
        narrative: "project_review",
        styles: [{ id: "lianbushou", weight: 60 }, { id: "mimeng", weight: 40 }]
    },
    {
        id: "founder_story",
        name: "创始人故事",
        description: "人物叙事 + 情感共鸣",
        narrative: "person_story",
        styles: [{ id: "xinshixiang", weight: 70 }, { id: "banfo", weight: 30 }]
    },
    {
        id: "market_alpha",
        name: "市场 Alpha",
        description: "数据分析 + FOMO 情绪",
        narrative: "market_analysis",
        styles: [{ id: "lingongzi", weight: 50 }, { id: "mimeng", weight: 50 }]
    },
    {
        id: "industry_roast",
        name: "行业吐槽",
        description: "犀利批判 + 反常识",
        narrative: "industry_critique",
        styles: [{ id: "banfo", weight: 70 }, { id: "fengqiongzi", weight: 30 }]
    },
    {
        id: "defi_tutorial",
        name: "DeFi 教程",
        description: "干货教学 + 接地气",
        narrative: "tutorial",
        styles: [{ id: "chengshian", weight: 60 }, { id: "lianbushou", weight: 40 }]
    }
]

// 辅助函数
export function getStyleById(id: string): StyleConfig | undefined {
    return ALL_STYLES.find(s => s.id === id)
}

export function getCombinationById(id: string): CombinationConfig | undefined {
    return COMBINATIONS.find(c => c.id === id)
}

export function getNarrativeById(id: string): NarrativeType | undefined {
    return NARRATIVE_TYPES.find(n => n.id === id)
}
