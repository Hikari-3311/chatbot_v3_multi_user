"""
模型管理模块
负责模型的初始化与调用
"""

from typing import List, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel

from core.config import Config


class ModelManager:
    """负责模型的初始化与调用"""

    def __init__(self, config: Config):
        self.config = config
        self._model: Optional[BaseChatModel] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """初始化聊天模型"""
        api_key, base_url = self.config.load_env()
        self._model = init_chat_model(
            model=self.config.MODEL_NAME,
            model_provider=self.config.MODEL_PROVIDER,
            api_key=api_key,
            base_url=base_url
        )

    @property
    def model(self) -> BaseChatModel:
        """获取模型实例"""
        if self._model is None:
            self._initialize_model()
        return self._model

    def stream_response(self, messages: List[BaseMessage]):
        """流式调用模型，返回生成器"""
        return self.model.stream(messages)

    def invoke_response(self, messages: List[BaseMessage]):
        """非流式调用模型，返回完整响应"""
        return self.model.invoke(messages)