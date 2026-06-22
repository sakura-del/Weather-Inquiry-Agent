"""
天气工具 - 基于schema定义的工具实现
"""
from typing import Dict, Any
from src.tools.schema import (
    GET_WEATHER_SCHEMA,
    validate_weather_params,
    format_weather_response
)
from src.services.weather_api import WeatherAPI


class WeatherTool:
    """天气查询工具"""

    def __init__(self):
        self.api_adapter = WeatherAPI()

    def execute(self, city: str, date: str = "today") -> Dict[str, Any]:
        """
        执行天气查询

        Args:
            city: 城市中文名
            date: 查询日期

        Returns:
            统一格式的天气数据
        """
        # 参数校验
        valid, error_msg = validate_weather_params(city, date)
        if not valid:
            return format_weather_response(success=False, error=error_msg)

        # 调用API
        result = self.api_adapter.get_weather(city, date)

        # 如果API返回成功
        if result.get("success"):
            return format_weather_response(
                success=True,
                city=result.get("city", city),
                weather=result.get("weather", ""),
                temperature=result.get("temperature", ""),
                humidity=result.get("humidity", ""),
                wind=result.get("wind", ""),
                forecast=result.get("forecast", {})
            )
        else:
            return format_weather_response(
                success=False,
                error=result.get("error", "获取天气信息失败")
            )

    @property
    def schema(self) -> Dict[str, Any]:
        """获取工具schema"""
        return GET_WEATHER_SCHEMA


# 工具实例，供外部调用
weather_tool = WeatherTool()
