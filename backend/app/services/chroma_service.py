"""
ChromaDB 向量引擎服务
P34: 三个 Collection — style_samples / published_posts / content_history
P35: 第 4 个 Collection — research_reports (策略官报告入库 + 48h 去重)

用途:
    1. style_samples: 风格样本语义匹配 (替代 random sampling)
    2. published_posts: 声调锚定 (召回用户最近发布的帖子)
    3. content_history: 嘴撸模式每日去重 (防止高频模式下重复)

部署:
    - 本地开发: PersistentClient (数据保存在 ./chroma_db/)
    - 服务器: 改一行代码切 HttpClient
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Chroma 数据目录 (相对于 backend/ 根目录)
CHROMA_DB_PATH = os.environ.get(
    "CHROMA_DB_PATH",
    str(Path(__file__).parent.parent.parent / "chroma_db")
)


class ChromaService:
    """ChromaDB 向量引擎封装"""

    # 四个 Collection 名称
    STYLE_SAMPLES = "style_samples"
    PUBLISHED_POSTS = "published_posts"
    CONTENT_HISTORY = "content_history"
    RESEARCH_REPORTS = "research_reports"  # P35 F2

    def __init__(self, db_path: Optional[str] = None):
        self._client = None
        self._db_path = db_path or CHROMA_DB_PATH
        self._collections = {}

    @property
    def client(self):
        """懒初始化 Chroma 客户端"""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=self._db_path)
                logger.info(f"[Chroma] ✅ 初始化成功, 数据目录: {self._db_path}")
            except Exception as e:
                logger.error(f"[Chroma] ❌ 初始化失败: {e}")
                raise
        return self._client

    def _get_collection(self, name: str):
        """获取或创建 Collection (带缓存)"""
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}  # 余弦相似度
            )
        return self._collections[name]

    # ==================== 风格样本 ====================

    def add_style_samples(self, samples: list[dict]) -> int:
        """
        批量添加风格样本到 style_samples Collection

        Args:
            samples: [{"id": "...", "content": "...", "metadata": {...}}]

        Returns:
            添加的样本数量
        """
        if not samples:
            return 0

        collection = self._get_collection(self.STYLE_SAMPLES)
        ids = [s["id"] for s in samples]
        documents = [s["content"] for s in samples]
        metadatas = [s.get("metadata", {}) for s in samples]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"[Chroma] style_samples: +{len(samples)} 条")
        return len(samples)

    def get_semantic_samples(
        self,
        query_text: str,
        n_results: int = 3,
        style_filter: Optional[str] = None,
        logic_pattern: Optional[str] = None,
    ) -> list[dict]:
        """
        语义匹配风格样本 (替代 random sampling)

        Args:
            query_text: 搜索文本 (素材内容)
            n_results: 返回数量
            style_filter: 风格过滤 (如 "半佛", "咪蒙")
            logic_pattern: 逻辑结构过滤 (如 "对比反转")

        Returns:
            [{"id", "content", "metadata", "distance"}]
        """
        collection = self._get_collection(self.STYLE_SAMPLES)

        if collection.count() == 0:
            logger.warning("[Chroma] style_samples 为空, 回退到随机采样")
            return []

        # 构建 metadata 过滤条件
        where = {}
        if style_filter:
            where["style"] = style_filter
        if logic_pattern:
            where["logic_pattern"] = logic_pattern

        query_params = {
            "query_texts": [query_text],
            "n_results": min(n_results, collection.count()),
        }
        if where:
            query_params["where"] = where

        try:
            results = collection.query(**query_params)
        except Exception as e:
            logger.warning(f"[Chroma] 语义匹配失败 (可能 metadata 不匹配): {e}")
            # 去掉 where 重试
            query_params.pop("where", None)
            results = collection.query(**query_params)

        # 转换为标准格式
        output = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return output

    # ==================== 已发布帖子 (声调锚定) ====================

    def add_published_post(self, post_id: str, content: str, metadata: dict = None):
        """
        存储已发布的内容 (用于声调锚定)

        Args:
            post_id: 唯一 ID (如 "2026-03-07_MIRA_01")
            content: 帖子全文
            metadata: {"project", "platform", "date", "mode", ...}
        """
        collection = self._get_collection(self.PUBLISHED_POSTS)
        collection.upsert(
            ids=[post_id],
            documents=[content],
            metadatas=[metadata or {}]
        )
        logger.info(f"[Chroma] published_posts: +1 ({post_id})")

    def get_recent_posts(
        self,
        query_text: str,
        n_results: int = 3,
        project: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> list[dict]:
        """
        召回最近发布的帖子 (声调锚定)

        Args:
            query_text: 当前素材
            n_results: 返回数量
            project: 项目过滤
            platform: 平台过滤 ("binance_square" / "kaito")
        """
        collection = self._get_collection(self.PUBLISHED_POSTS)

        if collection.count() == 0:
            return []

        where = {}
        if project:
            where["project"] = project
        if platform:
            where["platform"] = platform

        query_params = {
            "query_texts": [query_text],
            "n_results": min(n_results, collection.count()),
        }
        if where:
            query_params["where"] = where

        try:
            results = collection.query(**query_params)
        except Exception:
            query_params.pop("where", None)
            results = collection.query(**query_params)

        output = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return output

    # ==================== 内容历史 (去重) ====================

    def add_content_history(self, content_id: str, content: str, metadata: dict = None):
        """存储生成的内容 (用于去重检查)"""
        collection = self._get_collection(self.CONTENT_HISTORY)
        collection.upsert(
            ids=[content_id],
            documents=[content],
            metadatas=[metadata or {}]
        )

    def check_dedup(
        self,
        content: str,
        threshold: float = 0.15,
        project: Optional[str] = None,
    ) -> dict:
        """
        检查内容是否与历史内容重复

        Args:
            content: 待检查内容
            threshold: 距离阈值 (越小越相似, 0=完全相同, <0.15=高度重复)
            project: 项目过滤

        Returns:
            {"is_duplicate": bool, "most_similar": {...}, "distance": float}
        """
        collection = self._get_collection(self.CONTENT_HISTORY)

        if collection.count() == 0:
            return {"is_duplicate": False, "most_similar": None, "distance": 1.0}

        where = {"project": project} if project else None
        query_params = {
            "query_texts": [content],
            "n_results": 1,
        }
        if where:
            query_params["where"] = where

        try:
            results = collection.query(**query_params)
        except Exception:
            query_params.pop("where", None)
            results = collection.query(**query_params)

        if results and results["documents"] and results["documents"][0]:
            distance = results["distances"][0][0]
            is_dup = distance < threshold
            return {
                "is_duplicate": is_dup,
                "most_similar": {
                    "id": results["ids"][0][0],
                    "content": results["documents"][0][0][:200],  # 截取前200字
                    "metadata": results["metadatas"][0][0] if results["metadatas"] else {},
                },
                "distance": distance,
            }

        return {"is_duplicate": False, "most_similar": None, "distance": 1.0}

    # ==================== P35 F2: 投研报告 ====================

    def add_research_report(
        self,
        twitter: str,
        date: str,
        name: str,
        content: str,
        metadata: dict = None,
    ):
        """
        入库一份策略官报告
        ID: {twitter}_{date}，upsert 防重复
        """
        collection = self._get_collection(self.RESEARCH_REPORTS)
        report_id = f"{twitter.lstrip('@')}_{date}"
        meta = {
            "project_name": name,
            "twitter": twitter,
            "date": date,
            "ingested_at": datetime.now().isoformat(),
            **(metadata or {}),
        }
        collection.upsert(
            ids=[report_id],
            documents=[content],
            metadatas=[meta],
        )
        logger.info(f"[Chroma] research_reports: +1 ({report_id})")

    def get_recent_reports(self, hours: int = 48) -> list[str]:
        """
        返回近 N 小时内已分析的 twitter handle 列表（用于 48h 去重）
        """
        collection = self._get_collection(self.RESEARCH_REPORTS)
        if collection.count() == 0:
            return []

        cutoff = (datetime.now() - timedelta(hours=hours)).strftime("%Y%m%d")
        try:
            # 获取所有 metadata，筛选 date >= cutoff
            all_data = collection.get(include=["metadatas"])
            recent = set()
            for meta in (all_data.get("metadatas") or []):
                if meta.get("date", "") >= cutoff:
                    tw = meta.get("twitter", "")
                    if tw:
                        recent.add(tw.lower().lstrip("@"))
            logger.info(f"[Chroma] 近{hours}h已分析: {len(recent)} 个项目")
            return list(recent)
        except Exception as e:
            logger.warning(f"[Chroma] get_recent_reports 失败: {e}")
            return []

    def get_project_history(self, twitter: str, limit: int = 10) -> list[dict]:
        """
        返回指定项目的历史报告列表
        """
        collection = self._get_collection(self.RESEARCH_REPORTS)
        if collection.count() == 0:
            return []

        handle = twitter.lower().lstrip("@")
        try:
            all_data = collection.get(
                where={"twitter": {"$eq": twitter}},
                include=["metadatas", "documents"],
            )
            # fallback: 如果 where 条件不匹配，用 ID 前缀匹配
            if not all_data.get("ids"):
                all_data = collection.get(include=["metadatas", "documents"])
                results = []
                for i, rid in enumerate(all_data.get("ids") or []):
                    if rid.lower().startswith(handle):
                        results.append({
                            "id": rid,
                            "metadata": (all_data["metadatas"] or [])[i] if all_data.get("metadatas") else {},
                            "content_preview": ((all_data["documents"] or [])[i] or "")[:300],
                        })
                return results[:limit]

            results = []
            for i, rid in enumerate(all_data.get("ids") or []):
                results.append({
                    "id": rid,
                    "metadata": (all_data["metadatas"] or [])[i] if all_data.get("metadatas") else {},
                    "content_preview": ((all_data["documents"] or [])[i] or "")[:300],
                })
            return results[:limit]
        except Exception as e:
            logger.warning(f"[Chroma] get_project_history 失败: {e}")
            return []

    # ==================== 工具方法 ====================

    def get_stats(self) -> dict:
        """获取各 Collection 的统计信息"""
        stats = {}
        for name in [self.STYLE_SAMPLES, self.PUBLISHED_POSTS, self.CONTENT_HISTORY, self.RESEARCH_REPORTS]:
            try:
                collection = self._get_collection(name)
                stats[name] = collection.count()
            except Exception:
                stats[name] = 0
        return stats

    def clear_collection(self, name: str):
        """清空指定 Collection"""
        try:
            self.client.delete_collection(name)
            self._collections.pop(name, None)
            logger.info(f"[Chroma] 已清空: {name}")
        except Exception as e:
            logger.warning(f"[Chroma] 清空 {name} 失败: {e}")


# 全局单例
_chroma_instance: Optional[ChromaService] = None


def get_chroma_service() -> ChromaService:
    """获取 ChromaService 全局单例"""
    global _chroma_instance
    if _chroma_instance is None:
        _chroma_instance = ChromaService()
    return _chroma_instance
