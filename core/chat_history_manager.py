"""
对话历史管理模块
管理单个用户的对话历史（消息列表）
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from core.config import Config


class ChatHistoryManager:
    """管理对话历史（消息列表）"""

    def __init__(self, system_prompt: str = None):
        self.messages: List[BaseMessage] = []
        self._init_system_message(system_prompt or Config.SYSTEM_PROMPT)

    def _init_system_message(self, system_prompt: str) -> None:
        """初始化系统消息"""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt)
        ])
        self.messages = prompt_template.format_messages()

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str) -> None:
        """添加 AI 回复"""
        self.messages.append(AIMessage(content=content))

    def get_optimized_messages(self, max_pairs: int = 3) -> List[BaseMessage]:
        """
        获取优化后的消息列表（保留 System + 最近 N 轮）
        """
        # 分离 system 消息和对话消息
        system_msgs = [m for m in self.messages if isinstance(m, SystemMessage)]
        conversation_msgs = [m for m in self.messages if not isinstance(m, SystemMessage)]

        # 只保留最近的 N 轮（每轮 2 条消息）
        recent_msgs = conversation_msgs[-(max_pairs * 2):]

        return system_msgs + recent_msgs

    def get_all_messages(self) -> List[BaseMessage]:
        """获取完整消息列表"""
        return self.messages.copy()

    def get_message_count(self) -> int:
        """获取消息总数"""
        return len(self.messages)

    def to_dict(self) -> List[dict]:
        """将对话历史转换为字典列表（用于 JSON 序列化）"""
        result = []
        for msg in self.messages:
            role = type(msg).__name__.replace("Message", "").lower()
            result.append({"role": role, "content": msg.content})
        return result

    @classmethod
    def from_dict(cls, data: List[dict], system_prompt: str = None) -> "ChatHistoryManager":
        """从字典列表恢复对话历史（用于 JSON 反序列化）"""
        manager = cls(system_prompt)
        manager.messages = []
        for item in data:
            role = item.get("role")
            content = item.get("content", "")
            if role == "system":
                manager.messages.append(SystemMessage(content=content))
            elif role == "human" or role == "user":
                manager.messages.append(HumanMessage(content=content))
            elif role == "ai" or role == "assistant":
                manager.messages.append(AIMessage(content=content))
        return manager

    def print_history(self) -> None:
        """打印对话历史（调试用）"""
        print("\n--- 对话历史 ---")
        for msg in self.messages:
            role = type(msg).__name__.replace("Message", "")
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            print(f"  [{role}] {content}")
        print("--- 结束 ---\n")