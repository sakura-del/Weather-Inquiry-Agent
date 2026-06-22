# 天气查询Agent（Function Calling实现）规格文档

## Why
基于大模型Function Calling机制，实现支持自然语言交互的天气查询Agent，使用户无需记忆指令即可通过口语化提问获取天气信息；同时严格遵循工具设计规范，预留MCP、A2A协议扩展能力。

## What Changes
- 新建天气查询Agent项目，实现四层分层架构
- 实现Function Calling核心调度逻辑
- 对接外部天气API（高德/和风天气）
- 预留MCP协议兼容和A2A协议扩展能力

## Impact
- 新增能力：自然语言天气查询、多轮对话上下文管理、标准化工具定义
- 新增代码：Agent核心层、天气工具、外部服务适配层

---

## ADDED Requirements

### Requirement: 四层分层架构
系统应采用以下四层架构：
1. **交互层**：接收用户自然语言输入，返回自然语言回复
2. **Agent核心层**：LLM推理引擎、Function Calling调度器、上下文管理器
3. **工具能力层**：天气查询工具的标准化定义、参数校验、错误处理
4. **外部服务层**：第三方天气API对接、请求封装、数据清洗

#### Scenario: 架构初始化
- **WHEN** 系统启动
- **THEN** 四层架构组件应正确初始化并建立层级调用关系

---

### Requirement: 天气工具定义
工具应遵循描述清晰、参数规范、返回标准化的原则。

#### Scenario: 工具调用成功
- **WHEN** 用户请求查询天气
- **THEN** 系统返回统一结构化数据，包含code、msg、data字段

**工具名称**: `get_weather`

**工具描述**: 查询中国境内指定城市的天气信息，支持实时天气、未来3天预报，仅可用于天气查询相关的用户请求。

**参数Schema**:
```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "需要查询天气的城市中文名称，如北京、贵阳、上海"
    },
    "date": {
      "type": "string",
      "description": "查询日期，可选值：today/明天/后天，默认值为today"
    }
  },
  "required": ["city"]
}
```

**返回格式**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "city": "贵阳",
    "date": "2026-06-22",
    "weather": "晴",
    "temperature": "22~28℃",
    "wind": "东北风2级",
    "humidity": "65%"
  }
}
```

---

### Requirement: Function Calling调度逻辑
完整实现「模型决策-工具执行-结果生成」三段式闭环。

#### Scenario: 意图判断与参数提取
- **WHEN** 用户输入「贵阳明天天气怎么样」
- **THEN** LLM返回工具调用指令 `{"name":"get_weather","parameters":{"city":"贵阳","date":"明天"}}`

#### Scenario: 非天气相关问题
- **WHEN** 用户提问与天气无关
- **THEN** LLM直接生成自然语言回复，不触发工具调用

#### Scenario: 工具执行与结果生成
- **WHEN** 工具返回结构化天气数据
- **THEN** 系统将结果追加到对话历史，LLM生成自然语言回复

---

### Requirement: 对话上下文管理
维护多轮对话历史，支持上下文参数继承。

#### Scenario: 上下文参数继承
- **WHEN** 用户先问「北京天气怎么样」，再问「明天呢」
- **THEN** 模型自动继承城市参数「北京」，无需用户重复说明

#### Scenario: 上下文长度控制
- **WHEN** 对话历史超过预设阈值
- **THEN** 系统自动压缩或截断早期对话，避免token溢出

---

### Requirement: 错误处理机制
覆盖全链路异常场景，返回友好的错误信息。

#### Scenario: 参数异常
- **WHEN** 城市名为空或不存在
- **THEN** 返回错误码和明确错误信息，由LLM引导用户修正

#### Scenario: API异常
- **WHEN** 网络超时、接口限流、配额耗尽
- **THEN** 返回统一降级提示，不暴露原始错误

#### Scenario: 结果为空
- **WHEN** 超出查询日期范围或无对应城市数据
- **THEN** 告知用户支持的查询范围，引导有效提问

---

### Requirement: MCP协议兼容（扩展能力）
将天气查询工具封装为标准MCP Tool Server。

#### Scenario: MCP工具发现
- **WHEN** MCP客户端请求工具列表
- **THEN** 返回天气查询工具的标准化描述

#### Scenario: MCP工具调用
- **WHEN** MCP客户端调用天气工具
- **THEN** 返回标准化MCP格式结果

---

### Requirement: A2A协议扩展（扩展能力）
支持Agent间的能力调用。

#### Scenario: A2A天气查询请求
- **WHEN** 其他Agent（如行程规划Agent）请求天气信息
- **THEN** 返回标准化A2A格式的天气响应

---

## 技术选型
- **大模型**: DeepSeek-V3 / 通义千问 / GPT-4o Mini（支持原生Function Calling）
- **天气API**: 高德天气API 或 和风天气API
- **开发框架**: 可基于LangChain/LlamaIndex，也可直接调用SDK原生实现

---

## 项目结构
```
weather-query-agent/
├── src/
│   ├── interaction/          # 交互层
│   │   └── cli.py            # 命令行交互
│   ├── agent/                # Agent核心层
│   │   ├── core.py           # Agent核心逻辑
│   │   ├── dispatcher.py     # Function Calling调度器
│   │   └── context.py        # 上下文管理器
│   ├── tools/                # 工具能力层
│   │   ├── weather.py        # 天气工具定义
│   │   └── schema.py         # 工具参数Schema
│   └── services/             # 外部服务层
│       └── weather_api.py    # 天气API适配器
├── config/
│   └── settings.py           # 配置管理
├── tests/                    # 单元测试
├── requirements.txt
└── main.py                   # 入口文件
```
