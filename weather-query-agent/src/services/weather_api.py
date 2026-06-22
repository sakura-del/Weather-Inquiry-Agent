"""
天气API适配器 - 对接第三方天气API（和风天气/高德天气）
"""
import sys
import os
from datetime import datetime, timedelta

import requests
from typing import Dict, Any, Optional

# 添加项目根目录到路径以导入config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config'))
from settings import settings


class WeatherAPIError(Exception):
    """天气API异常基类"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class WeatherAPIAdapter:
    """天气API适配器，支持和风天气和高德天气"""
    
    # 和风天气API基础URL
    QWEATHER_BASE_URL = "https://api.qweather.com/v7/weather"
    # 高德天气API基础URL
    AMAP_BASE_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    # 和风天气API超时时间（秒）
    QWEATHER_TIMEOUT = 10
    # 高德天气API超时时间（秒）
    AMAP_TIMEOUT = 10
    
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.provider = settings.WEATHER_API_PROVIDER
    
    def get_weather(self, city: str, date: str = "today") -> Dict[str, Any]:
        """
        查询天气
        
        Args:
            city: 城市中文名
            date: 日期 today/明天/后天
            
        Returns:
            统一格式: {"code": 200, "msg": "success", "data": {...}}
        """
        # 参数校验
        if not city or not city.strip():
            return self._error_response(400, "城市名称不能为空")
        
        city = city.strip()
        
        # 日期转换
        target_date = self._convert_date(date)
        if target_date is None:
            return self._error_response(400, f"不支持的日期格式: {date}，支持的格式: today/明天/后天")
        
        # 如果API密钥为空，返回模拟数据
        if not self.api_key:
            return self._get_mock_data(city, target_date)
        
        # 根据提供商调用对应的API
        if self.provider == "qweather":
            return self._query_qweather(city, target_date, date)
        elif self.provider == "amap":
            return self._query_amap(city, target_date, date)
        else:
            return self._error_response(500, f"不支持的API提供商: {self.provider}")
    
    def _convert_date(self, date: str) -> Optional[str]:
        """
        将日期字符串转换为标准日期格式
        
        Args:
            date: today/明天/后天
            
        Returns:
            标准日期格式 YYYY-MM-DD 或 None（无效格式）
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date == "today":
            return today.strftime("%Y-%m-%d")
        elif date == "明天":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date == "后天":
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            return None
    
    def _query_qweather(self, city: str, target_date: str, original_date: str) -> Dict[str, Any]:
        """和风天气API"""
        try:
            # 和风天气API参数
            params = {
                "key": self.api_key,
                "location": city,
                "lang": "zh"
            }
            
            # 和风天气3天预报API
            response = requests.get(
                f"{self.QWEATHER_BASE_URL}/3d",
                params=params,
                timeout=self.QWEATHER_TIMEOUT
            )
            
            # 处理HTTP错误
            response.raise_for_status()
            
            result = response.json()
            
            # 检查和风天气API返回的错误码
            if result.get("code") != "200":
                code = result.get("code", "")
                # 和风天气错误码处理
                error_messages = {
                    "401": "API密钥无效",
                    "402": "API密钥已过期",
                    "403": "该服务权限不足",
                    "429": "请求过于频繁，请稍后重试",
                    "500": "和风天气服务器内部错误",
                    "601": "城市不存在",
                }
                message = error_messages.get(code, f"和风天气API错误: {result.get('msg', '未知错误')}")
                return self._error_response(int(code) if code.isdigit() else 500, message)
            
            # 解析和风天气响应数据
            data = self._parse_qweather_response(result, target_date, original_date)
            return {
                "code": 200,
                "msg": "success",
                "data": data
            }
            
        except requests.exceptions.Timeout:
            return self._error_response(504, "和风天气API请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            return self._error_response(503, "无法连接到和风天气服务器，请检查网络连接")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return self._error_response(429, "和风天气API请求过于频繁，请稍后重试")
            elif e.response.status_code == 403:
                return self._error_response(403, "和风天气API权限不足，请检查API密钥")
            else:
                return self._error_response(e.response.status_code, f"和风天气API HTTP错误: {str(e)}")
        except WeatherAPIError:
            raise
        except Exception as e:
            return self._error_response(500, f"和风天气API调用失败: {str(e)}")
    
    def _parse_qweather_response(self, response: Dict[str, Any], target_date: str, original_date: str) -> Optional[Dict[str, Any]]:
        """
        解析和风天气API响应数据，转换为统一格式
        
        Args:
            response: 和风天气API原始响应
            target_date: 目标日期
            original_date: 原始日期字符串
            
        Returns:
            统一格式的天气数据或None
        """
        try:
            daily_list = response.get("daily", [])
            
            # 查找目标日期的天气数据
            target_data = None
            for day in daily_list:
                if day.get("fxDate") == target_date:
                    target_data = day
                    break
            
            # 如果没找到精确日期，取第一天或最后一天
            if target_data is None and daily_list:
                if original_date == "明天" and len(daily_list) >= 2:
                    target_data = daily_list[1]
                elif original_date == "后天" and len(daily_list) >= 3:
                    target_data = daily_list[2]
                else:
                    target_data = daily_list[0]
            
            if target_data is None:
                return None
            
            # 转换为统一格式
            return {
                "city": response.get("location", {}).get("name", ""),
                "date": target_data.get("fxDate", ""),
                "date_str": original_date,
                "weather": target_data.get("textDay", ""),
                "weather_night": target_data.get("textNight", ""),
                "temperature": {
                    "max": int(target_data.get("tempMax", 0)),
                    "min": int(target_data.get("tempMin", 0))
                },
                "wind": {
                    "direction": target_data.get("windDirDay", ""),
                    "speed": target_data.get("windSpeedDay", ""),
                    "scale": target_data.get("windScaleDay", "")
                },
                "humidity": int(target_data.get("humidity", 0)),
                "precipitation": float(target_data.get("precip", 0)),
                "uv_index": target_data.get("uvIndex", ""),
                "visibility": target_data.get("vis", ""),
                "pressure": target_data.get("pressure", ""),
                "cloud": target_data.get("cloud", ""),
                "provider": "qweather"
            }
            
        except Exception as e:
            raise WeatherAPIError(500, f"解析和风天气数据失败: {str(e)}")
    
    def _query_amap(self, city: str, target_date: str, original_date: str) -> Dict[str, Any]:
        """高德天气API"""
        try:
            # 高德天气API参数
            params = {
                "key": self.api_key,
                "city": city,
                "extensions": "all"  # 获取多天预报
            }
            
            response = requests.get(
                self.AMAP_BASE_URL,
                params=params,
                timeout=self.AMAP_TIMEOUT
            )
            
            # 处理HTTP错误
            response.raise_for_status()
            
            result = response.json()
            
            # 检查高德API返回状态
            if result.get("status") != "1":
                error_info = result.get("info", "未知错误")
                # 高德错误码处理
                error_code = result.get("infocode", "")
                if error_code == "1001":
                    return self._error_response(401, "高德API密钥无效")
                elif error_code == "1002":
                    return self._error_response(403, "高德API签名错误")
                elif error_code == "1003":
                    return self._error_response(403, "高德API服务权限不足")
                elif error_code == "1004":
                    return self._error_response(429, "高德API请求过于频繁")
                elif error_code == "1005":
                    return self._error_response(403, "高德API服务已被禁用")
                elif error_code == "1006":
                    return self._error_response(429, "高德API日配额已用尽")
                elif error_code == "1007":
                    return self._error_response(429, "高德API分钟配额已用尽")
                else:
                    return self._error_response(500, f"高德天气API错误: {error_info}")
            
            # 解析高德天气响应数据
            data = self._parse_amap_response(result, target_date, original_date)
            return {
                "code": 200,
                "msg": "success",
                "data": data
            }
            
        except requests.exceptions.Timeout:
            return self._error_response(504, "高德天气API请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            return self._error_response(503, "无法连接到高德天气服务器，请检查网络连接")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return self._error_response(429, "高德天气API请求过于频繁，请稍后重试")
            elif e.response.status_code == 403:
                return self._error_response(403, "高德天气API权限不足，请检查API密钥")
            else:
                return self._error_response(e.response.status_code, f"高德天气API HTTP错误: {str(e)}")
        except WeatherAPIError:
            raise
        except Exception as e:
            return self._error_response(500, f"高德天气API调用失败: {str(e)}")
    
    def _parse_amap_response(self, response: Dict[str, Any], target_date: str, original_date: str) -> Optional[Dict[str, Any]]:
        """
        解析高德天气API响应数据，转换为统一格式
        
        Args:
            response: 高德天气API原始响应
            target_date: 目标日期
            original_date: 原始日期字符串
            
        Returns:
            统一格式的天气数据或None
        """
        try:
            forecasts = response.get("forecasts", [])
            
            if not forecasts:
                # 单次实时天气查询
                lives = response.get("lives", [])
                if not lives:
                    return None
                    
                live = lives[0]
                return {
                    "city": live.get("city", ""),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "date_str": "today",
                    "weather": live.get("weather", ""),
                    "weather_night": "",
                    "temperature": {
                        "max": None,
                        "min": None
                    },
                    "temperature_current": int(float(live.get("temperature", 0))),
                    "wind": {
                        "direction": live.get("winddirection", ""),
                        "speed": live.get("windpower", ""),
                        "scale": ""
                    },
                    "humidity": int(float(live.get("humidity", 0))),
                    "precipitation": 0,
                    "provider": "amap"
                }
            
            # 多天预报
            forecast = forecasts[0]
            casts = forecast.get("casts", [])
            
            # 查找目标日期的数据
            target_data = None
            target_date_short = target_date[5:]  # MM-DD格式
            
            for cast in casts:
                date_str = cast.get("date", "")[5:]  # MM-DD格式
                if date_str == target_date_short:
                    target_data = cast
                    break
            
            # 如果没找到精确日期，根据original_date取对应索引
            if target_data is None and casts:
                if original_date == "明天" and len(casts) >= 2:
                    target_data = casts[1]
                elif original_date == "后天" and len(casts) >= 3:
                    target_data = casts[2]
                else:
                    target_data = casts[0]
            
            if target_data is None:
                return None
            
            # 转换为统一格式
            return {
                "city": forecast.get("city", ""),
                "date": target_data.get("date", ""),
                "date_str": original_date,
                "weather": self._convert_amap_weather(target_data.get("dayweather", "")),
                "weather_night": self._convert_amap_weather(target_data.get("nightweather", "")),
                "temperature": {
                    "max": int(target_data.get("daytemp", 0)),
                    "min": int(target_data.get("nighttemp", 0))
                },
                "wind": {
                    "direction": target_data.get("daywind", ""),
                    "speed": target_data.get("daypower", ""),
                    "scale": ""
                },
                "humidity": int(target_data.get("dayhumidity", 0)),
                "precipitation": float(target_data.get("dayprecipitation", 0)),
                "provider": "amap"
            }
            
        except Exception as e:
            raise WeatherAPIError(500, f"解析高德天气数据失败: {str(e)}")
    
    def _convert_amap_weather(self, weather: str) -> str:
        """将高德天气API的天气描述转换为统一格式"""
        # 高德天气码到中文描述的映射
        weather_map = {
            "晴": "晴",
            "多云": "多云",
            "阴": "阴",
            "小雨": "小雨",
            "中雨": "中雨",
            "大雨": "大雨",
            "暴雨": "暴雨",
            "阵雨": "阵雨",
            "雷阵雨": "雷阵雨",
            "小雪": "小雪",
            "中雪": "中雪",
            "大雪": "大雪",
            "暴雪": "暴雪",
            "阵雪": "阵雪",
            "雾": "雾",
            "冻雨": "冻雨",
            "沙尘暴": "沙尘暴",
            "扬沙": "扬沙",
            "浮尘": "浮尘",
        }
        return weather_map.get(weather, weather)
    
    def _get_mock_data(self, city: str, target_date: str) -> Dict[str, Any]:
        """返回模拟天气数据用于测试"""
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        week_days = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        week_day = week_days[date_obj.weekday()]
        
        # 模拟一些天气数据
        mock_conditions = [
            {"weather": "晴", "weather_night": "晴", "temp_max": 28, "temp_min": 18},
            {"weather": "多云", "weather_night": "多云", "temp_max": 26, "temp_min": 17},
            {"weather": "晴转多云", "weather_night": "多云", "temp_max": 27, "temp_min": 18},
            {"weather": "阴", "weather_night": "阴", "temp_max": 24, "temp_min": 16},
            {"weather": "小雨", "weather_night": "小雨", "temp_max": 22, "temp_min": 15},
        ]
        
        # 根据日期选择一个固定的天气条件
        day_index = date_obj.day % len(mock_conditions)
        condition = mock_conditions[day_index]
        
        return {
            "code": 200,
            "msg": "success",
            "data": {
                "city": city,
                "date": target_date,
                "date_str": target_date,
                "week_day": week_day,
                "weather": condition["weather"],
                "weather_night": condition["weather_night"],
                "temperature": {
                    "max": condition["temp_max"],
                    "min": condition["temp_min"]
                },
                "temperature_current": (condition["temp_max"] + condition["temp_min"]) // 2,
                "wind": {
                    "direction": "东南风",
                    "speed": "3级",
                    "scale": "微风"
                },
                "humidity": 65,
                "precipitation": 0.0,
                "uv_index": "中等",
                "visibility": "10km",
                "pressure": "1013hPa",
                "provider": "mock"
            }
        }
    
    def _error_response(self, code: int, message: str) -> Dict[str, Any]:
        """统一错误响应格式"""
        return {
            "code": code,
            "msg": message,
            "data": None
        }
