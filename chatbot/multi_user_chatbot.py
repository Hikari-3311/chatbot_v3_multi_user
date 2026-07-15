"""
多用户聊天机器人模块
协调各模块完成多用户对话功能
"""

from typing import List, Optional
from langchain_core.messages import BaseMessage

from core import Config, ModelManager
from sessions import MultiUserSessionManager


class MultiUserChatBot:
    """支持多用户的多轮对话聊天机器人"""

    def __init__(self, config: Optional[Config] = None, persist_dir: str = "data/sessions"):
        self.config = config or Config()
        self.model_mgr = ModelManager(self.config)
        self.session_mgr = MultiUserSessionManager(
            system_prompt=self.config.SYSTEM_PROMPT,
            persist_dir=persist_dir
        )

    def chat(self, user_id: str, user_input: str) -> str:
        """
        处理单次对话请求
        返回 AI 回复
        """
        # 1. 获取用户会话
        history_mgr = self.session_mgr.get_or_create_session(user_id)

        # 2. 添加用户消息
        history_mgr.add_user_message(user_input)

        # 3. 优化历史
        memory_messages = history_mgr.get_optimized_messages(
            max_pairs=self.config.MAX_PAIRS_HISTORY
        )

        # 4. 调用模型（使用非流式，便于返回完整内容）
        response = self.model_mgr.invoke_response(memory_messages)
        reply_content = response.content

        # 5. 保存 AI 回复
        history_mgr.add_ai_message(reply_content)

        # 6. 自动持久化
        self.session_mgr.save_all_sessions()

        return reply_content

    def stream_chat(self, user_id: str, user_input: str):
        """
        流式对话（生成器）
        逐块返回 AI 回复
        """
        # 1. 获取用户会话
        history_mgr = self.session_mgr.get_or_create_session(user_id)

        # 2. 添加用户消息
        history_mgr.add_user_message(user_input)

        # 3. 优化历史
        memory_messages = history_mgr.get_optimized_messages(
            max_pairs=self.config.MAX_PAIRS_HISTORY
        )

        # 4. 流式调用模型
        reply_content = ""
        for chunk in self.model_mgr.stream_response(memory_messages):
            if chunk.content:
                reply_content += chunk.content
                yield chunk.content

        # 5. 保存 AI 回复
        history_mgr.add_ai_message(reply_content)

        # 6. 自动持久化
        self.session_mgr.save_all_sessions()

    def get_user_history(self, user_id: str) -> List[BaseMessage]:
        """获取用户的完整对话历史"""
        history_mgr = self.session_mgr.get_or_create_session(user_id)
        return history_mgr.get_all_messages()

    def print_user_history(self, user_id: str) -> None:
        """打印用户的对话历史（调试用）"""
        history_mgr = self.session_mgr.get_or_create_session(user_id)
        history_mgr.print_history()

    def delete_user(self, user_id: str) -> bool:
        """删除用户及其所有数据"""
        return self.session_mgr.delete_session(user_id)

    def get_active_users(self) -> List[str]:
        """获取所有活跃用户"""
        return self.session_mgr.get_all_sessions()

    def save_all(self) -> None:
        """保存所有会话数据"""
        self.session_mgr.save_all_sessions()