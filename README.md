# 天气查询 Agent (Weather Inquiry Agent)

基于大模型 Function Calling 机制实现的智能天气查询 Agent，支持自然语言交互，用户无需记忆指令，通过口语化提问即可获取天气信息。

## 功能特性

- **自然语言交互**：支持口语化提问，如"北京天气怎么样"、"贵阳明天天气"
- **Function Calling 集成**：完整实现"模型决策-工具执行-结果生成"三段式闭环
- **多轮对话支持**：上下文参数继承，用户无需重复输入城市信息
- **多种天气API支持**：支持和风天气、高德天气等多种数据源
- **错误处理机制**：完善的参数校验、API异常降级处理
- **可扩展架构**：预留 MCP、A2A 协议扩展能力

## 技术栈

- **大模型**：支持 DeepSeek-V3、通义千问、GPT-4o Mini 等支持原生 Function Calling 的模型
- **框架**：Python + OpenAI SDK
- **天气API**：和风天气 / 高德天气
- **依赖管理**：uv / pip

## 快速开始

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM 配置
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# 天气API配置
WEATHER_API_KEY=your_weather_api_key
WEATHER_API_PROVIDER=qweather  # qweather 或 amap

# 上下文配置
MAX_CONTEXT_LENGTH=10
MAX_TOKEN_PER_REQUEST=4000
```

### 运行

```bash
python main.py
```

### 使用示例

```
天气查询Agent (Function Calling)
==================================================
支持城市天气查询，例如：
  - 北京天气怎么样
  - 贵阳明天天气
  - 上海后天温度

输入 '退出' 结束对话
==================================================

用户: 北京天气怎么样
助手: 北京今天晴，气温22~30℃，东北风2级，湿度65%

用户: 明天呢
助手: 北京明天多云转晴，气温20~28℃，南风3级
```

## 项目结构

```
.
├── main.py                    # 入口文件
├── config/                    # 配置管理
│   └── settings.py            # 配置类
├── src/
│   ├── agent/                 # Agent核心层
│   │   ├── core.py           # Agent核心逻辑
│   │   ├── context.py        # 上下文管理器
│   │   └── dispatcher.py     # Function Calling调度器
│   ├── tools/                 # 工具能力层
│   │   ├── schema.py         # 工具Schema定义
│   │   └── weather.py        # 天气工具实现
│   ├── services/              # 外部服务层
│   │   ├── weather_api.py    # 天气API适配器
│   │   └── city_map.py       # 城市映射表
│   └── interaction/           # 交互层
│       └── cli.py            # 命令行交互界面
├── tests/                     # 单元测试
│   └── test_weather_agent.py
├── .env.example               # 环境变量模板
├── .gitignore
└── requirements.txt           # 依赖列表
```

## 核心模块说明

### Agent 核心层

- **core.py**：Agent 核心逻辑，组装提示词、调用 LLM、处理 Function Calling 流程
- **context.py**：对话上下文管理器，维护对话历史、支持参数继承
- **dispatcher.py**：Function Calling 调度器，解析工具调用指令并分发执行

### 工具能力层

- **schema.py**：工具 JSON Schema 定义，包含参数校验逻辑
- **weather.py**：天气工具实现，调用 API 适配器获取数据

### 外部服务层

- **weather_api.py**：天气 API 适配器，支持和风天气、高德天气
- **city_map.py**：城市名称与 ID 的映射表

## API 支持

### 和风天气 (qweather)

- API 文档：https://dev.qweather.com/
- 免费额度：每日 1000 次调用

### 高德天气 (amap)

- API 文档：https://lbs.amap.com/api/webservice/guide/api/weatherinfo
- 免费额度：每日 1000 次调用

## 测试

运行单元测试：

```bash
python -m pytest tests/ -v
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
