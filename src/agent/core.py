"""
Agent核心逻辑 - 组装提示词、调用LLM、处理Function Calling流程
"""
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import settings
from src.agent.context import ContextManager
from src.agent.dispatcher import Dispatcher, ToolCall
from src.tools.schema import TOOLS


class WeatherAgent:
    """天气查询Agent核心"""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.context = ContextManager()
        self.dispatcher = Dispatcher()
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

        # 初始化系统提示词
        self.context.add_system_message(settings.SYSTEM_PROMPT)

    def chat(self, user_input: str) -> str:
        """
        处理用户输入，返回自然语言回复

        Args:
            user_input: 用户输入

        Returns:
            Agent的自然语言回复
        """
        # 1. 添加用户消息到上下文
        self.context.add_user_message(user_input)

        # 2. 调用LLM
        response = self._call_llm()

        # 3. 检查是否需要工具调用
        tool_calls = self.dispatcher.parse_tool_calls(response)

        if tool_calls:
            # 添加 assistant 的 tool_calls 消息到上下文
            raw_tool_calls = response.get("tool_calls", [])
            self.context.add_assistant_tool_calls_message(raw_tool_calls)
            # 4. 执行工具调用
            return self._handle_tool_calls(tool_calls)
        else:
            # 5. 直接返回LLM回复
            reply = response.get("content", "")
            self.context.add_assistant_message(reply)
            return reply

    def _call_llm(self) -> Dict[str, Any]:
        """调用LLM"""
        messages = self.context.get_context()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.model_dump()

    def _handle_tool_calls(self, tool_calls: List[ToolCall]) -> str:
        """处理工具调用"""
        # 执行所有工具调用
        for tool_call in tool_calls:
            result = self.dispatcher.dispatch(tool_call)

            # 添加工具结果到上下文（带上 tool_call_id）
            import json
            tool_result_str = json.dumps(result, ensure_ascii=False)
            self.context.add_tool_message(tool_result_str, tool_call_id=tool_call.id)

            # 如果是天气查询，更新上下文中的城市参数
            if tool_call.name == "get_weather":
                city = tool_call.arguments.get("city", "")
                if city:
                    self.context.update_last_city(city)

        # 再次调用LLM生成最终回复
        response = self._call_llm()
        reply = response.get("content", "")
        self.context.add_assistant_message(reply)

        return reply

    def reset(self):
        """重置Agent"""
        self.context.clear()
        self.context.add_system_message(settings.SYSTEM_PROMPT)