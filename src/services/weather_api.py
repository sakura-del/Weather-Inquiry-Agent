"""
天气API适配器 - 对接和风天气API（新版）
文档: https://dev.qweather.com/docs/api/
"""
import requests
from typing import Dict, Any
from config import settings
from src.services.city_map import CITY_ID_MAP


class WeatherAPI:
    """和风天气API适配器"""

    def __init__(self):
        self.api_host = settings.WEATHER_API_HOST
        self.api_key = settings.WEATHER_API_KEY
        self._headers = {"X-QW-Api-Key": self.api_key}

    def _get(self, path: str, params: dict = None) -> dict:
        """统一请求方法"""
        url = f"https://{self.api_host}{path}"
        resp = requests.get(url, params=params or {}, headers=self._headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_weather(self, city: str, date: str = "today") -> Dict[str, Any]:
        """
        调用和风天气API获取天气数据

        Args:
            city: 城市中文名
            date: 查询日期（today/明天/后天）

        Returns:
            统一格式的天气数据
        """
        try:
            # 1. 查询城市ID（优先本地映射表）
            city_id = self._get_city_id(city)
            if not city_id:
                return {"success": False, "error": f"未找到城市「{city}」，请确认城市名称"}

            # 2. 查询天气
            if date == "today":
                weather_data = self._get_now_weather(city_id)
            else:
                weather_data = self._get_forecast_weather(city_id, date)

            if not weather_data:
                return {"success": False, "error": "获取天气数据失败"}

            weather_data["success"] = True
            weather_data["city"] = city
            return weather_data

        except Exception as e:
            return {"success": False, "error": f"天气查询异常: {str(e)}"}

    def _get_city_id(self, city: str) -> str:
        """根据城市名查询城市ID（优先本地映射表）"""
        # 先查本地映射
        if city in CITY_ID_MAP:
            return CITY_ID_MAP[city]
        # 备用：查在线API（需要订阅含geo的套餐）
        try:
            data = self._get("/v2/city/lookup", {"location": city})
            if data.get("code") == "200" and data.get("location"):
                return data["location"][0]["id"]
        except Exception:
            pass
        return ""

    def _get_now_weather(self, city_id: str) -> Dict[str, Any]:
        """获取实时天气"""
        try:
            data = self._get("/v7/weather/now", {"location": city_id})
            if data.get("code") == "200" and data.get("now"):
                now = data["now"]
                return {
                    "weather": now.get("text", ""),
                    "temperature": f"{now.get('temp', '')}°C",
                    "humidity": f"{now.get('humidity', '')}%",
                    "wind": f"{now.get('windDir', '')}{now.get('windScale', '')}级",
                    "feels_like": f"{now.get('feelsLike', '')}°C",
                    "visibility": f"{now.get('vis', '')}km",
                    "forecast": {}
                }
        except Exception:
            pass
        return {}

    def _get_forecast_weather(self, city_id: str, date: str) -> Dict[str, Any]:
        """获取预报天气（明天/后天）"""
        date_map = {"明天": 1, "后天": 2}
        day_index = date_map.get(date, 0)

        try:
            data = self._get("/v7/weather/3d", {"location": city_id})
            if data.get("code") == "200" and data.get("daily"):
                daily = data["daily"]
                if day_index < len(daily):
                    day = daily[day_index]
                    return {
                        "weather": day.get("textDay", ""),
                        "temperature": f"{day.get('tempMin', '')}°C ~ {day.get('tempMax', '')}°C",
                        "humidity": f"{day.get('humidity', '')}%",
                        "wind": f"{day.get('windDirDay', '')}{day.get('windScaleDay', '')}级",
                        "forecast": {
                            "date": day.get("fxDate", ""),
                            "sunrise": day.get("sunrise", ""),
                            "sunset": day.get("sunset", ""),
                            "moonPhase": day.get("moonPhase", "")
                        }
                    }
        except Exception:
            pass
        return {}
