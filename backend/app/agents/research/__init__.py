"""
P31: 投研模块 (Research Agents)

包含选题发现 (Scout) 等投研专用智能体。
Surf API 调用通过 services.surf_service.SurfService 进行。
"""
from .scout import scout_agent

__all__ = ["scout_agent"]
