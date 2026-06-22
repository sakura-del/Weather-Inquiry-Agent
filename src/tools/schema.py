"""
天气工具Schema定义 - 遵循工具设计原则
"""

from typing import Any


# get_weather工具的JSON Schema定义
GET_WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询中国境内指定城市的天气信息，支持实时天气、未来3天预报，仅可用于天气查询相关的用户请求。",
        "parameters": {
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
    }
}

# 工具列表 - 用于传递给LLM
TOOLS = [GET_WEATHER_SCHEMA]


def validate_weather_params(city: str, date: str = "today") -> tuple[bool, str]:
    """
    校验天气查询参数

    Args:
        city: 城市名称
        date: 查询日期，默认值为today

    Returns:
        tuple[bool, str]: (是否校验通过, 错误信息)
    """
    if not city or not isinstance(city, str):
        return False, "城市名称不能为空"

    if len(city.strip()) == 0:
        return False, "城市名称不能为空或仅包含空白字符"

    valid_dates = {"today", "明天", "后天"}
    if date and date not in valid_dates:
        return False, f"日期参数无效，仅支持: {', '.join(valid_dates)}"

    return True, ""


# 返回格式定义 - 统一结构
class WeatherResult:
    """天气查询结果统一返回格式"""

    def __init__(
        self,
        success: bool,
        city: str = "",
        weather: str = "",
        temperature: str = "",
        humidity: str = "",
        wind: str = "",
        forecast: dict = None,
        error: str = ""
    ):
        self.success = success
        self.city = city
        self.weather = weather
        self.temperature = temperature
        self.humidity = humidity
        self.wind = wind
        self.forecast = forecast or {}
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "city": self.city,
            "weather": self.weather,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind": self.wind,
            "forecast": self.forecast,
            "error": self.error
        }


def format_weather_response(
    success: bool,
    city: str = "",
    weather: str = "",
    temperature: str = "",
    humidity: str = "",
    wind: str = "",
    forecast: dict = None,
    error: str = ""
) -> dict[str, Any]:
    """
    格式化天气响应数据

    Args:
        success: 请求是否成功
        city: 城市名称
        weather: 天气状况
        temperature: 温度
        humidity: 湿度
        wind: 风力风向
        forecast: 预报数据
        error: 错误信息

    Returns:
        dict[str, Any]: 统一格式的响应字典
    """
    return WeatherResult(
        success=success,
        city=city,
        weather=weather,
        temperature=temperature,
        humidity=humidity,
        wind=wind,
        forecast=forecast,
        error=error
    ).to_dict()
