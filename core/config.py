"""
配置管理模块
集中管理所有配置参数
"""

import os
from dotenv import load_dotenv


class Config:
    """集中管理所有配置参数"""

    # 模型配置
    MODEL_NAME: str = "gpt-5.4-mini"
    MODEL_PROVIDER: str = "openai"

    # 对话配置
    EXIT_WORD: str = "exit"
    MAX_PAIRS_HISTORY: int = 3

    # 系统提示词
    SYSTEM_PROMPT: str = (
        "你是漂亮小姐姐，滇池学院的数字员工，也是一名耐心、友好的智能助手。"
        "我会用自然、清晰的方式回答用户问题。"
    )

    @classmethod
    def load_env(cls) -> tuple:
        """加载环境变量，返回 (api_key, base_url)"""
        load_dotenv(override=True)
        api_key = os.getenv("CLOSEAI_API_KEY")
        base_url = os.getenv("CLOSEAI_BASE_URL")

        if not api_key:
            raise ValueError("请在 .env 中设置 CLOSEAI_API_KEY")
        return api_key, base_url