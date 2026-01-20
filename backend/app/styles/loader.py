"""
风格库加载器
支持单一风格和组合风格的加载
"""
import yaml
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class StyleConfig:
    """单个风格配置"""
    id: str
    name: str
    icon: str
    color: str
    description: str
    data_dir: str
    max_samples: int
    traits: Dict[str, str]
    forbidden_words: List[str] = field(default_factory=list)
    temperature: float = 0.7


@dataclass
class CombinationConfig:
    """组合风格配置"""
    id: str
    name: str
    description: str
    styles: List[Dict[str, Any]]  # [{id, weight}, ...]
    recommended_for: List[str] = field(default_factory=list)


class StyleLoader:
    """
    风格库加载器
    支持：
    1. 加载单个风格
    2. 加载组合风格
    3. 读取风格素材样本
    4. 构建 Prompt 片段
    """
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        # 解析风格配置
        self.styles: Dict[str, StyleConfig] = {}
        for style_id, style_data in self.config.get("styles", {}).items():
            self.styles[style_id] = StyleConfig(**style_data)
        
        # 解析组合配置
        self.combinations: Dict[str, CombinationConfig] = {}
        for combo_id, combo_data in self.config.get("combinations", {}).items():
            self.combinations[combo_id] = CombinationConfig(**combo_data)
    
    def get_style(self, style_id: str) -> Optional[StyleConfig]:
        """获取单个风格配置"""
        return self.styles.get(style_id)
    
    def get_all_styles(self) -> List[StyleConfig]:
        """获取所有风格列表"""
        return list(self.styles.values())
    
    def get_combination(self, combo_id: str) -> Optional[CombinationConfig]:
        """获取组合配置"""
        return self.combinations.get(combo_id)
    
    def get_all_combinations(self) -> List[CombinationConfig]:
        """获取所有组合列表"""
        return list(self.combinations.values())
    
    def load_samples(self, style_id: str, max_chars: int = 2000) -> str:
        """
        加载风格素材样本
        
        Args:
            style_id: 风格ID
            max_chars: 每个样本最大字符数
            
        Returns:
            格式化的样本文本
        """
        style = self.get_style(style_id)
        if not style:
            return f"[风格 {style_id} 不存在]"
        
        # 定位素材目录
        base_dir = Path(__file__).parent.parent.parent  # backend/
        data_dir = base_dir / style.data_dir
        
        if not data_dir.exists():
            return f"[{style.name}风格库目录不存在: {data_dir}]"
        
        # 查找素材文件
        files = list(data_dir.glob("*.txt")) + list(data_dir.glob("*.md"))
        # 排除 README.md
        files = [f for f in files if f.name.lower() != "readme.md"]
        
        if not files:
            return f"[{style.name}风格库为空，请在 {data_dir} 添加素材文件]"
        
        # 随机选择样本
        selected = random.sample(files, min(style.max_samples, len(files)))
        
        samples = []
        for i, file_path in enumerate(selected, 1):
            try:
                content = file_path.read_text(encoding="utf-8")
                # 截断过长内容
                if len(content) > max_chars:
                    content = content[:max_chars] + "...(截断)"
                samples.append(f"--- 样本 {i}: {file_path.name} ---\n{content}")
            except Exception as e:
                samples.append(f"--- 样本 {i}: {file_path.name} [读取失败: {e}] ---")
        
        return "\n\n".join(samples)
    
    def load_combination_samples(self, combo_id: str) -> Dict[str, str]:
        """
        加载组合风格的所有样本
        
        Returns:
            {style_id: samples_text, ...}
        """
        combo = self.get_combination(combo_id)
        if not combo:
            return {}
        
        result = {}
        for style_ref in combo.styles:
            style_id = style_ref["id"]
            result[style_id] = self.load_samples(style_id)
        
        return result
    
    def build_style_prompt(self, style_id: str) -> str:
        """
        构建单个风格的 Prompt 片段
        """
        style = self.get_style(style_id)
        if not style:
            return ""
        
        traits = style.traits
        forbidden = ", ".join(style.forbidden_words) if style.forbidden_words else "无"
        
        return f"""
## 写作风格: {style.name} {style.icon}

### 风格特征
- **情绪基调**: {traits.get('tone', '')}
- **结构特征**: {traits.get('structure', '')}
- **句式特点**: {traits.get('sentence_style', '')}

### 禁忌词汇
{forbidden}
"""
    
    def build_combination_prompt(self, combo_id: str) -> str:
        """
        构建组合风格的 Prompt 片段
        """
        combo = self.get_combination(combo_id)
        if not combo:
            return ""
        
        lines = [f"## 组合风格: {combo.name}", f"**描述**: {combo.description}", ""]
        
        for style_ref in combo.styles:
            style_id = style_ref["id"]
            weight = style_ref["weight"]
            style = self.get_style(style_id)
            if style:
                lines.append(f"### {style.name} ({weight}%)")
                lines.append(f"- 情绪基调: {style.traits.get('tone', '')}")
                lines.append(f"- 结构特征: {style.traits.get('structure', '')}")
                lines.append("")
        
        lines.append("### 融合策略")
        lines.append("- 开头: 采用权重更高的风格")
        lines.append("- 正文: 两种风格交替融合")
        lines.append("- 结尾: 根据内容类型选择情感升华或逻辑收尾")
        
        return "\n".join(lines)
    
    def get_blended_temperature(self, combo_id: str) -> float:
        """
        获取组合风格的混合温度
        按权重加权平均
        """
        combo = self.get_combination(combo_id)
        if not combo:
            return 0.7
        
        total_weight = 0
        weighted_temp = 0
        
        for style_ref in combo.styles:
            style_id = style_ref["id"]
            weight = style_ref["weight"]
            style = self.get_style(style_id)
            if style:
                weighted_temp += style.temperature * weight
                total_weight += weight
        
        return weighted_temp / total_weight if total_weight > 0 else 0.7


# 全局单例
_loader: Optional[StyleLoader] = None


def get_style_loader() -> StyleLoader:
    """获取全局风格加载器实例"""
    global _loader
    if _loader is None:
        _loader = StyleLoader()
    return _loader
