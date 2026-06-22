# Tasks - 天气查询Agent（Function Calling实现）

## 前置准备
- [x] Task 1: 初始化项目结构，创建目录和基础文件

## 核心实现

### 外部服务层
- [x] Task 2: 实现天气API适配器
  - [x] Task 2.1: 创建API请求封装
  - [x] Task 2.2: 实现响应数据清洗为统一格式
  - [x] Task 2.3: 添加错误处理和降级逻辑

### 工具能力层
- [x] Task 3: 定义天气工具Schema
  - [x] Task 3.1: 定义get_weather工具的JSON Schema
  - [x] Task 3.2: 实现参数校验逻辑
  - [x] Task 3.3: 定义统一返回格式

- [x] Task 4: 实现天气工具函数
  - [x] Task 4.1: 实现get_weather工具函数
  - [x] Task 4.2: 实现错误处理和异常返回

### Agent核心层
- [x] Task 5: 实现上下文管理器
  - [x] Task 5.1: 管理对话历史
  - [x] Task 5.2: 实现上下文参数继承
  - [x] Task 5.3: 实现上下文长度控制

- [x] Task 6: 实现Function Calling调度器
  - [x] Task 6.1: 解析LLM返回的工具调用指令
  - [x] Task 6.2: 调用对应的工具函数
  - [x] Task 6.3: 将工具结果追加到对话上下文

- [x] Task 7: 实现Agent核心逻辑
  - [x] Task 7.1: 组装提示词（系统指令+历史+当前输入+工具定义）
  - [x] Task 7.2: 调用LLM进行推理
  - [x] Task 7.3: 处理LLM返回结果（直接回复或工具调用）

### 交互层
- [x] Task 8: 实现命令行交互界面
  - [x] Task 8.1: 实现用户输入接收
  - [x] Task 8.2: 实现自然语言回复展示
  - [x] Task 8.3: 实现多轮对话循环

### 配置管理
- [x] Task 9: 配置管理
  - [x] Task 9.1: 配置LLM API密钥和端点
  - [x] Task 9.2: 配置天气API密钥
  - [x] Task 9.3: 配置模型参数（temperature、max_tokens等）

## 扩展能力（可选）
- [ ] Task 10: MCP协议兼容实现
- [ ] Task 11: A2A协议扩展实现

## 验证
- [x] Task 12: 单元测试
  - [x] Task 12.1: 天气工具单元测试
  - [x] Task 12.2: 调度器单元测试
  - [x] Task 12.3: 上下文管理单元测试

---

## Task Dependencies
- Task 2 必须在 Task 3 之前完成（API适配器是工具的基础）
- Task 5、Task 6 必须在 Task 7 之前完成（上下文和调度器是Agent核心的基础）
- Task 3、Task 5、Task 6 完成后才能实现 Task 7
- Task 7 完成后才能实现 Task 8
- Task 9 与其他任务无依赖，可并行完成
