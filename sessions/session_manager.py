"""
多用户会话管理模块
为每个用户维护独立的对话历史
"""

import json
import os
from typing import Dict, List, Optional

from core import Config, ChatHistoryManager


class MultiUserSessionManager:
    """
    多用户会话管理器
    为每个用户维护独立的对话历史
    """

    def __init__(self, system_prompt: str = None, persist_dir: str = "data/sessions"):
        self.system_prompt = system_prompt or Config.SYSTEM_PROMPT
        self.persist_dir = os.path.abspath(persist_dir) if persist_dir else persist_dir
        self.sessions: Dict[str, ChatHistoryManager] = {}

        # 确保持久化目录存在
        if self.persist_dir:
            os.makedirs(self.persist_dir, exist_ok=True)
            self._load_all_sessions()

    def get_or_create_session(self, user_id: str) -> ChatHistoryManager:
        """获取或创建用户的会话"""
        if user_id not in self.sessions:
            # 尝试从文件加载
            session = self._load_session_from_file(user_id)
            if session is None:
                session = ChatHistoryManager(self.system_prompt)
            self.sessions[user_id] = session
        return self.sessions[user_id]

    def delete_session(self, user_id: str) -> bool:
        """删除用户会话"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            # 同时删除持久化文件
            self._delete_session_file(user_id)
            return True
        return False

    def get_all_sessions(self) -> List[str]:
        """获取所有活跃用户 ID"""
        return list(self.sessions.keys())

    def save_all_sessions(self) -> None:
        """保存所有会话到文件"""
        if not self.persist_dir:
            return
        for user_id, history_mgr in self.sessions.items():
            self._save_session_to_file(user_id, history_mgr)

    def _get_session_file_path(self, user_id: str) -> str:
        """获取用户会话文件的路径"""
        return os.path.join(self.persist_dir, f"{user_id}_history.json")

    def _save_session_to_file(self, user_id: str, history_mgr: ChatHistoryManager) -> None:
        """保存单个用户的会话到文件"""
        file_path = self._get_session_file_path(user_id)
        data = history_mgr.to_dict()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_session_from_file(self, user_id: str) -> Optional[ChatHistoryManager]:
        """从文件加载单个用户的会话"""
        file_path = self._get_session_file_path(user_id)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ChatHistoryManager.from_dict(data, self.system_prompt)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def _load_all_sessions(self) -> None:
        """从文件加载所有用户的会话"""
        if not os.path.exists(self.persist_dir):
            return
        for filename in os.listdir(self.persist_dir):
            if filename.endswith("_history.json"):
                user_id = filename.replace("_history.json", "")
                session = self._load_session_from_file(user_id)
                if session is not None:
                    self.sessions[user_id] = session

    def _delete_session_file(self, user_id: str) -> None:
        """删除用户会话文件"""
        file_path = self._get_session_file_path(user_id)
        if os.path.exists(file_path):
            os.remove(file_path)

    def __del__(self):
        """析构时自动保存所有会话"""
        try:
            self.save_all_sessions()
        except Exception:
            pass