# ChatBot V3 — 多用户会话管理（高级版）

基于 LangChain 的多用户多轮对话机器人，采用模块化包结构，支持独立用户会话与 JSON 持久化存储。

## 项目结构

```text
chatbot_v3_multi_user/
│
├── .env                              # 环境变量配置文件
├── requirements.txt                  # 项目依赖
├── README.md                         # 项目说明文档
├── main.py                           # 程序入口（启动文件）
│
├── core/                             # 核心模块目录
│   ├── __init__.py                   # 模块初始化，导出核心类
│   ├── config.py                     # Config 类 - 配置管理
│   ├── model_manager.py              # ModelManager 类 - 模型管理
│   └── chat_history_manager.py       # ChatHistoryManager 类 - 对话历史管理
│
├── sessions/                         # 会话管理模块目录
│   ├── __init__.py                   # 模块初始化，导出会话类
│   └── session_manager.py            # MultiUserSessionManager 类 - 多用户会话管理
│
├── chatbot/                          # 聊天机器人模块目录
│   ├── __init__.py                   # 模块初始化，导出机器人类
│   └── multi_user_chatbot.py         # MultiUserChatBot 类 - 多用户聊天机器人
│
└── data/                             # 数据存储目录（运行时生成）
    └── sessions/                     # 会话持久化目录
        ├── user_a_history.json       # 用户A的对话历史
        └── user_b_history.json       # 用户B的对话历史
```

## 功能特性

- **多用户独立会话**：每个用户拥有独立的对话历史，互不干扰
- **会话自动持久化**：对话历史自动保存为 JSON 文件，程序重启后自动恢复
- **流式 / 非流式双模式**：支持 `stream_chat()` 流式输出和 `chat()` 非流式调用
- **模块化包结构**：按功能拆分为 `core/`、`sessions/`、`chatbot/` 三个包，每个类独立文件
- **交互式 CLI**：支持用户切换、历史查看、流式对话等命令
- **滑动窗口上下文**：保留 System 消息 + 最近 N 轮对话，控制 Token 成本

## 架构设计

### 模块依赖关系

```text
main.py
  │
  └── chatbot/multi_user_chatbot.py  (MultiUserChatBot)
        ├── core/model_manager.py    (ModelManager)
        │     └── core/config.py     (Config)
        └── sessions/session_manager.py  (MultiUserSessionManager)
              └── core/chat_history_manager.py  (ChatHistoryManager)
                    └── core/config.py          (Config)
```

### 数据流

```text
用户输入(user_id + content)
  → MultiUserSessionManager.get_or_create_session(user_id)
  → ChatHistoryManager.add_user_message()
  → ChatHistoryManager.get_optimized_messages(max_pairs)
  → ModelManager.stream_response() / invoke_response()
  → ChatHistoryManager.add_ai_message()
  → MultiUserSessionManager.save_all_sessions()  (持久化到 JSON)
  → 返回回复
```

### 核心类职责

| 类 | 文件 | 职责 |
| --- | --- | --- |
| `Config` | `core/config.py` | 集中管理模型名称、提示词、历史轮数等配置 |
| `ModelManager` | `core/model_manager.py` | 封装 LLM 初始化与流式/非流式调用 |
| `ChatHistoryManager` | `core/chat_history_manager.py` | 管理单用户消息列表，支持 JSON 序列化/反序列化 |
| `MultiUserSessionManager` | `sessions/session_manager.py` | 管理所有用户会话，负责持久化读写 |
| `MultiUserChatBot` | `chatbot/multi_user_chatbot.py` | 主控类，协调各模块完成多用户对话 |

## 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
cd chatbot_v3_multi_user

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 配置

编辑 `.env` 文件，填入 API 密钥和代理地址：

```env
CLOSEAI_API_KEY=your-api-key-here
CLOSEAI_BASE_URL=https://api.openai-proxy.org/v1
```

### 运行

```bash
python main.py
```

### 交互命令

| 命令 | 说明 |
| --- | --- |
| 直接输入文本 | 与 AI 对话（流式输出） |
| `exit` | 退出程序（自动保存会话） |
| `switch:用户ID` | 切换到指定用户 |
| `history` | 查看当前用户的对话历史 |
| `users` | 列出所有活跃用户 |

## 配置说明

在 `core/config.py` 的 `Config` 类中可调整以下参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `MODEL_NAME` | `"gpt-5.4-mini"` | LLM 模型名称 |
| `MODEL_PROVIDER` | `"openai"` | 模型提供商 |
| `EXIT_WORD` | `"exit"` | 退出对话的关键词 |
| `MAX_PAIRS_HISTORY` | `3` | 每次发送给 LLM 的最大对话轮数 |
| `SYSTEM_PROMPT` | 滇池学院数字员工 | 系统提示词 |

## 会话持久化

对话历史自动保存在 `data/sessions/` 目录下，每个用户一个 JSON 文件：

```json
[
  {"role": "system", "content": "你是漂亮小姐姐..."},
  {"role": "human", "content": "你好"},
  {"role": "ai", "content": "你好呀~ 有什么可以帮你的吗？"}
]
```

- 程序退出时自动保存所有会话
- 程序启动时自动加载已有会话
- 删除用户时会同时删除对应的持久化文件

## 与 v1、v2 的区别

| 维度 | v1 (basic) | v2 (oop) | v3 (multi_user) |
| --- | --- | --- | --- |
| 设计范式 | 面向过程 | 面向对象 | 面向对象 + 模块化 |
| 文件数量 | 1 个 | 1 个 | 9 个 |
| 多用户支持 | ❌ | ❌ | ✅ |
| 会话持久化 | ❌ | ❌ | ✅ (JSON) |
| 包结构 | 无 | 无 | core / sessions / chatbot |
| 可扩展性 | 低 | 中 | 高 |
| 适合场景 | 快速验证 | 项目开发 | 生产环境 / 团队协作 |

## 演示模式

`main.py` 中提供了 4 种演示模式，可按需取消注释运行：

| 函数 | 说明 |
| --- | --- |
| `demo_streaming()` | 流式输出演示 |
| `demo_multi_user()` | 多用户独立会话演示 |
| `demo_persistence()` | 会话持久化演示（模拟程序重启恢复） |
| `interactive_mode()` | 交互模式（默认） |

## 依赖说明

核心依赖：

- `langchain` — LLM 应用框架
- `langchain-core` — 消息类型、Prompt 模板
- `openai` — OpenAI SDK
- `python-dotenv` — 环境变量加载

## 许可证

仅供学习与实验使用。
