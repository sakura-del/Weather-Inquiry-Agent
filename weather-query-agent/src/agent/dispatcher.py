"""
Function Calling调度器 - 解析LLM工具调用指令，调用对应工具函数
"""
from typing import Dict, Any, Optional, Callable, List, Union
from src.tools.schema import GET_WEATHER_SCHEMA
from src.services.weather_api import WeatherAPIAdapter


class ToolCall:
    """工具调用指令"""
    
    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.name = name
        self.arguments = arguments
    
    def __repr__(self) -> str:
        return f"ToolCall(name='{self.name}', arguments={self.arguments})"


class Dispatcher:
    """Function Calling调度器"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            "get_weather": self._call_get_weather
        }
        self.weather_api = WeatherAPIAdapter()
    
    def dispatch(self, tool_call: ToolCall) -> Dict[str, Any]:
        """
        分发工具调用
        
        Args:
            tool_call: 工具调用指令
            
        Returns:
            工具执行结果
        """
        tool_name = tool_call.name
        if tool_name not in self.tools:
            return self._error_response(f"未知工具: {tool_name}")
        
        return self.tools[tool_name](tool_call.arguments)
    
    def _call_get_weather(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用天气查询工具"""
        city = arguments.get("city", "")
        date = arguments.get("date", "today")
        
        # 参数校验
        if not city:
            return self._error_response("城市参数不能为空")
        
        # 调用API
        try:
            return self.weather_api.get_weather(city, date)
        except Exception as e:
            return self._error_response(f"天气查询失败: {str(e)}")
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """统一错误响应"""
        return {
            "code": 500,
            "msg": message,
            "data": None
        }
    
    @staticmethod
    def parse_tool_calls(llm_response: Union[Dict[str, Any], str]) -> Optional[List[ToolCall]]:
        """
        解析LLM返回的工具调用指令
        
        支持多种LLM返回格式:
        - OpenAI格式: tool_calls field with {name, arguments}
        - DeepSeek格式: function_call field with {name, arguments}
        - Anthropic格式: tool_use field with {name, input}
        - 通用的function call格式
        
        Args:
            llm_response: LLM返回的响应
            
        Returns:
            工具调用指令列表，如果没有工具调用则返回None
        """
        if llm_response is None:
            return None
        
        # 如果是字符串，尝试解析为JSON
        if isinstance(llm_response, str):
            try:
                import json
                llm_response = json.loads(llm_response)
            except json.JSONDecodeError:
                return None
        
        if not isinstance(llm_response, dict):
            return None
        
        tool_calls: List[ToolCall] = []
        
        # 格式1: OpenAI标准格式 - tool_calls
        # "tool_calls": [{"id": "call_xxx", "type": "function", "function": {"name": "get_weather", "arguments": "{...}"}}]
        if "tool_calls" in llm_response:
            for tc in llm_response["tool_calls"]:
                if not isinstance(tc, dict):
                    continue
                
                # 处理 function 嵌套格式
                func_data = tc.get("function", tc)
                name = func_data.get("name", "")
                arguments = func_data.get("arguments", "{}")
                
                # arguments可能是字符串或字典
                if isinstance(arguments, str):
                    try:
                        import json
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {"_raw": arguments}
                
                if name:
                    tool_calls.append(ToolCall(name=name, arguments=arguments))
            
            if tool_calls:
                return tool_calls
        
        # 格式2: DeepSeek格式 - function_call
        # "function_call": {"name": "get_weather", "arguments": "{...}"}
        if "function_call" in llm_response:
            fc = llm_response["function_call"]
            if isinstance(fc, dict):
                name = fc.get("name", "")
                arguments = fc.get("arguments", "{}")
                
                if isinstance(arguments, str):
                    try:
                        import json
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {"_raw": arguments}
                
                if name:
                    tool_calls.append(ToolCall(name=name, arguments=arguments))
            
            if tool_calls:
                return tool_calls
        
        # 格式3: Anthropic格式 - tool_use
        # "tool_use": {"name": "get_weather", "input": {...}}
        if "tool_use" in llm_response:
            tu = llm_response["tool_use"]
            if isinstance(tu, dict):
                name = tu.get("name", "")
                arguments = tu.get("input", {})
                
                if not isinstance(arguments, dict):
                    arguments = {"_raw": arguments}
                
                if name:
                    tool_calls.append(ToolCall(name=name, arguments=arguments))
            
            if tool_calls:
                return tool_calls
        
        # 格式4: 通用的函数调用格式 - function_call 或 function_call
        # 支持混合形式: function_call 可能是一个列表
        if "function_call" in llm_response:
            fc = llm_response["function_call"]
            if isinstance(fc, list):
                for item in fc:
                    if isinstance(item, dict):
                        name = item.get("name", "")
                        arguments = item.get("arguments", {})
                        if isinstance(arguments, str):
                            try:
                                import json
                                arguments = json.loads(arguments)
                            except json.JSONDecodeError:
                                arguments = {"_raw": arguments}
                        if name:
                            tool_calls.append(ToolCall(name=name, arguments=arguments))
        
        # 格式5: 国产模型通用格式 - tools字段直接包含
        # "tools": [{"function": {"name": "get_weather", "parameters": {...}}}]
        if "tools" in llm_response and isinstance(llm_response["tools"], list):
            for tool in llm_response["tools"]:
                if isinstance(tool, dict) and "function" in tool:
                    func = tool["function"]
                    name = func.get("name", "")
                    if name and name not in [tc.name for tc in tool_calls]:
                        # 从llm_response中查找对应的tool_call
                        pass
        
        return tool_calls if tool_calls else None
