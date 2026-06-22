"""
工具Schema定义 - 定义工具参数校验和Schema
"""
from typing import Tuple


# 天气查询工具的Schema定义
GET_WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": "查询指定城市的天气信息",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称"
            },
            "date": {
                "type": "string",
                "description": "查询日期，today/tomorrow/week",
                "enum": ["today", "tomorrow", "week"]
            }
        },
        "required": ["city"]
    }
}


def validate_weather_params(city: str, date: str = "today") -> Tuple[bool, str]:
    """
    校验天气查询参数
    
    Args:
        city: 城市名称
        date: 查询日期
        
    Returns:
        (是否有效, 错误消息)
    """
    # 校验城市参数
    if not city or not city.strip():
        return (False, "城市参数不能为空")
    
    city = city.strip()
    
    # 校验日期参数
    valid_dates = ["today", "tomorrow", "week"]
    if date not in valid_dates:
        return (False, f"日期参数无效，支持: {', '.join(valid_dates)}")
    
    return (True, "")
