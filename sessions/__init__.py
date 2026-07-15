"""
会话管理模块初始化
导出会话管理类
"""

from sessions.session_manager import MultiUserSessionManager

__all__ = [
    "MultiUserSessionManager",
]