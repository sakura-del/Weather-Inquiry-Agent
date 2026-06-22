"""
工具调用调度器 - 解析LLM返回的函数调用并分发执行
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.tools.schema import GET_WEATHER_SCHEMA


@dataclass
class ToolCall:
    """工具调用信息"""
    id: str
    name: str
    arguments: Dict[str, Any]


class Dispatcher:
    """工具调用调度器"""

    def __init__(self):
        self.tools = {GET_WEATHER_SCHEMA["function"]["name"]: self._get_weather}

    def parse_tool_calls(self, response: Dict[str, Any]) -> List[ToolCall]:
        """
        从LLM响应中解析工具调用

        Args:
            response: LLM返回的响应字典

        Returns:
            List[ToolCall]: 工具调用列表
        """
        tool_calls = []

        # 检查是否有tool_calls字段
        if "tool_calls" in response and response["tool_calls"]:
            for tc in response["tool_calls"]:
                tool_call = ToolCall(
                    id=tc.get("id", ""),
                    name=tc.get("function", {}).get("name", ""),
                    arguments=self._parse_arguments(
                        tc.get("function", {}).get("arguments", "{}")
                    )
                )
                tool_calls.append(tool_call)

        return tool_calls

    def _parse_arguments(self, arguments_str: str) -> Dict[str, Any]:
        """解析JSON字符串为参数字典"""
        import json
        try:
            return json.loads(arguments_str)
        except json.JSONDecodeError:
            return {}

    def dispatch(self, tool_call: ToolCall) -> Any:
        """
        分发并执行工具调用

        Args:
            tool_call: 工具调用信息

        Returns:
            执行结果
        """
        tool_name = tool_call.name
        if tool_name not in self.tools:
            return {"error": f"未知工具: {tool_name}"}

        return self.tools[tool_name](**tool_call.arguments)

    def _get_weather(self, city: str, date: str = "today") -> Dict[str, Any]:
        """
        执行天气查询

        Args:
            city: 城市名称
            date: 查询日期

        Returns:
            天气查询结果
        """
        try:
            from src.services.weather_api import WeatherAPI

            api = WeatherAPI()
            result = api.get_weather(city, date)
            return result
        except Exception as e:
            return {"error": str(e)}