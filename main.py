"""
程序入口
多用户聊天机器人演示
"""

import os
import time
from core import Config
from chatbot import MultiUserChatBot

# 基于入口脚本所在目录计算项目根路径，确保持久化文件始终落在项目内
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(PROJECT_ROOT, "data", "sessions")


def demo_streaming():
    """流式输出演示"""
    print("\n" + "=" * 50)
    print("流式输出演示")
    print("=" * 50 + "\n")

    bot = MultiUserChatBot(persist_dir=PERSIST_DIR)
    user_id = "demo_user"

    print(f"用户 [{user_id}] 开始对话\n")

    questions = [
        "你好，请介绍一下自己",
        "你能帮我做什么？",
        "谢谢你的回答"
    ]

    for i, question in enumerate(questions, 1):
        print(f"第 {i} 轮：{question}")
        print("AI: ", end="", flush=True)

        for chunk in bot.stream_chat(user_id, question):
            print(chunk, end="", flush=True)
            time.sleep(0.02)  # 模拟流式效果

        print("\n")


def demo_multi_user():
    """多用户独立会话演示"""
    print("\n" + "=" * 50)
    print("多用户独立会话演示")
    print("=" * 50 + "\n")

    bot = MultiUserChatBot(persist_dir=PERSIST_DIR)

    # 用户A 对话
    print("--- 用户A ---")
    reply = bot.chat("user_a", "你好，我叫小明，我今年18岁")
    print(f"AI: {reply}\n")

    reply = bot.chat("user_a", "我叫什么名字？今年几岁？")
    print(f"AI: {reply}\n")

    # 用户B 对话（独立会话）
    print("--- 用户B ---")
    reply = bot.chat("user_b", "你好，我叫小红，我喜欢打篮球")
    print(f"AI: {reply}\n")

    reply = bot.chat("user_b", "我叫什么名字？我喜欢什么？")
    print(f"AI: {reply}\n")

    # 用户A 继续（记得之前的对话）
    print("--- 用户A 继续 ---")
    reply = bot.chat("user_a", "我的名字和年龄是什么？")
    print(f"AI: {reply}\n")

    # 打印活跃用户列表
    print(f"活跃用户：{bot.get_active_users()}")


def demo_persistence():
    """会话持久化演示"""
    print("\n" + "=" * 50)
    print("会话持久化演示（重启后仍能恢复）")
    print("=" * 50 + "\n")

    # 第一次启动
    print("--- 第一次启动 ---")
    bot1 = MultiUserChatBot(persist_dir=PERSIST_DIR)
    reply = bot1.chat("persist_user", "我的名字是王五，我是一名程序员")
    print(f"AI: {reply}\n")
    bot1.save_all()
    print("会话已保存到 data/sessions/ 目录\n")

    # 模拟程序重启（重新创建机器人实例）
    print("--- 模拟程序重启 ---")
    bot2 = MultiUserChatBot(persist_dir=PERSIST_DIR)
    reply = bot2.chat("persist_user", "我叫什么名字？我的职业是什么？")
    print(f"AI: {reply}\n")

    # 查看用户历史
    print("--- 用户对话历史 ---")
    bot2.print_user_history("persist_user")


def interactive_mode():
    """交互模式（命令行）"""
    print("\n" + "=" * 50)
    print("多用户聊天机器人 - 交互模式")
    print("输入 'exit' 退出，输入 'switch:用户ID' 切换用户")
    print("输入 'history' 查看当前对话历史")
    print("=" * 50 + "\n")

    bot = MultiUserChatBot(persist_dir=PERSIST_DIR)
    current_user = "default_user"
    print(f"当前用户：{current_user}\n")

    while True:
        try:
            user_input = input(f"[{current_user}] 请输入：")

            if user_input.lower() == "exit":
                break

            if user_input.lower().startswith("switch:"):
                current_user = user_input.split(":", 1)[1].strip()
                print(f"已切换到用户：{current_user}\n")
                continue

            if user_input.lower() == "history":
                bot.print_user_history(current_user)
                continue

            if user_input.lower() == "users":
                print(f"活跃用户：{bot.get_active_users()}\n")
                continue

            # 流式输出回复
            print(f"[{current_user}] AI: ", end="", flush=True)
            for chunk in bot.stream_chat(current_user, user_input):
                print(chunk, end="", flush=True)
                time.sleep(0.02)
            print("\n")

        except KeyboardInterrupt:
            print("\n\n对话已中断")
            break

    print("保存会话数据...")
    bot.save_all()
    print("欢迎下次再来！")


if __name__ == "__main__":
    # 可以选择运行不同的演示
    # demo_streaming()
    # demo_multi_user()
    # demo_persistence()
    interactive_mode()