"""
P27 创作保存服务
================
本地 Markdown 文件存储，带 YAML frontmatter 元数据。
"""

import os
import re
import uuid
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class CreationStore:
    """本地文件创作存储"""

    def __init__(self, base_dir: str = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent.parent.parent / "data" / "creations"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict) -> dict:
        """
        保存创作到本地 Markdown 文件。
        
        Args:
            data: {
                title: str,
                content: str (Markdown),
                mode: str,
                input_topic: str,
                source_material: str (optional),
                critic_score: int (optional),
                critic_verdict: str (optional),
                word_count: int (optional),
            }
        
        Returns:
            { id, path, created_at }
        """
        now = datetime.now()
        short_id = uuid.uuid4().hex[:6]
        creation_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{short_id}"

        # Monthly subdirectory
        month_dir = self.base_dir / now.strftime("%Y-%m")
        month_dir.mkdir(parents=True, exist_ok=True)

        # Build frontmatter
        frontmatter = {
            "id": creation_id,
            "title": data.get("title", "无标题"),
            "mode": data.get("mode", "unknown"),
            "input_topic": data.get("input_topic", ""),
            "critic_score": data.get("critic_score", 0),
            "critic_verdict": data.get("critic_verdict", ""),
            "word_count": data.get("word_count", 0),
            "created_at": now.isoformat(),
        }

        # Optional fields
        if data.get("source_material"):
            frontmatter["source_material"] = data["source_material"]

        # Compose file
        content = data.get("content", "")
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
        file_content = f"---\n{yaml_str}---\n\n{content}\n"

        # Write
        file_path = month_dir / f"{creation_id}.md"
        file_path.write_text(file_content, encoding="utf-8")

        print(f"[CreationStore] Saved: {file_path}")

        return {
            "id": creation_id,
            "path": str(file_path),
            "created_at": now.isoformat(),
        }

    def list_all(self, month: str = None, page: int = 1, page_size: int = 20) -> dict:
        """
        列出所有创作（只返回 frontmatter 摘要）。
        
        Args:
            month: 可选，格式 "2026-02"
            page: 页码
            page_size: 每页数量
        
        Returns:
            { items: [...], total, page, page_size }
        """
        items = []

        # Determine which directories to scan
        if month:
            dirs = [self.base_dir / month]
        else:
            dirs = sorted(self.base_dir.iterdir(), reverse=True) if self.base_dir.exists() else []

        for d in dirs:
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.md"), reverse=True):
                meta = self._parse_frontmatter(f)
                if meta:
                    # Add content preview (first 100 chars of body)
                    body = self._read_body(f)
                    meta["preview"] = body[:100] + "..." if len(body) > 100 else body
                    items.append(meta)

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get(self, creation_id: str) -> Optional[dict]:
        """按 ID 读取完整创作内容。"""
        file_path = self._find_file(creation_id)
        if not file_path:
            return None

        meta = self._parse_frontmatter(file_path)
        if not meta:
            return None

        meta["content"] = self._read_body(file_path)
        return meta

    def delete(self, creation_id: str) -> bool:
        """按 ID 删除创作。"""
        file_path = self._find_file(creation_id)
        if not file_path:
            return False

        file_path.unlink()
        print(f"[CreationStore] Deleted: {file_path}")

        # Clean up empty month directories
        parent = file_path.parent
        if parent != self.base_dir and not any(parent.iterdir()):
            parent.rmdir()

        return True

    # ------ Internal helpers ------

    def _find_file(self, creation_id: str) -> Optional[Path]:
        """Search for a file by creation ID across all month dirs."""
        for d in self.base_dir.iterdir():
            if not d.is_dir():
                continue
            candidate = d / f"{creation_id}.md"
            if candidate.exists():
                return candidate
        return None

    def _parse_frontmatter(self, file_path: Path) -> Optional[dict]:
        """Extract YAML frontmatter from a markdown file."""
        try:
            text = file_path.read_text(encoding="utf-8")
            match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
            if not match:
                return None
            return yaml.safe_load(match.group(1))
        except Exception as e:
            print(f"[CreationStore] Parse error {file_path}: {e}")
            return None

    def _read_body(self, file_path: Path) -> str:
        """Read the body content after frontmatter."""
        try:
            text = file_path.read_text(encoding="utf-8")
            match = re.match(r'^---\n.*?\n---\n\n?(.*)', text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return text.strip()
        except Exception:
            return ""


# Singleton instance
creation_store = CreationStore()
