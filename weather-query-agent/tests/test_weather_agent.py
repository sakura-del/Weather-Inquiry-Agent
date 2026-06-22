"""
天气查询Agent单元测试
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.context import ContextManager, Message
from src.agent.dispatcher import Dispatcher, ToolCall
from src.tools.schema import validate_weather_params, GET_WEATHER_SCHEMA


class TestContextManager(unittest.TestCase):
    """上下文管理器测试"""
    
    def test_add_user_message(self):
        """测试添加用户消息"""
        ctx = ContextManager()
        ctx.add_user_message("北京天气怎么样")
        self.assertEqual(len(ctx.messages), 1)
        self.assertEqual(ctx.messages[0].role, "user")
        self.assertEqual(ctx.messages[0].content, "北京天气怎么样")
    
    def test_add_assistant_message(self):
        """测试添加助手消息"""
        ctx = ContextManager()
        ctx.add_assistant_message("北京今天晴，28度")
        self.assertEqual(len(ctx.messages), 1)
        self.assertEqual(ctx.messages[0].role, "assistant")
    
    def test_context_parameter_inheritance(self):
        """测试上下文参数继承"""
        ctx = ContextManager()
        ctx.update_last_city("北京")
        self.assertEqual(ctx.get_last_city(), "北京")
    
    def test_auto_truncate(self):
        """测试自动截断"""
        ctx = ContextManager()
        ctx.max_length = 3
        for i in range(5):
            ctx.add_user_message(f"消息{i}")
        self.assertLessEqual(len(ctx.messages), 3)


class TestDispatcher(unittest.TestCase):
    """调度器测试"""
    
    def test_parse_tool_calls_openai_format(self):
        """测试解析OpenAI格式的工具调用"""
        response = {
            "tool_calls": [
                {
                    "id": "call_123",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"city": "北京", "date": "today"}'
                    }
                }
            ]
        }
        tool_calls = Dispatcher.parse_tool_calls(response)
        self.assertIsNotNone(tool_calls)
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0].name, "get_weather")
        self.assertEqual(tool_calls[0].arguments["city"], "北京")
    
    def test_parse_tool_calls_deepseek_format(self):
        """测试解析DeepSeek格式的工具调用"""
        response = {
            "function_call": {
                "name": "get_weather",
                "arguments": '{"city": "上海", "date": "明天"}'
            }
        }
        tool_calls = Dispatcher.parse_tool_calls(response)
        self.assertIsNotNone(tool_calls)
        self.assertEqual(tool_calls[0].name, "get_weather")


class TestWeatherSchema(unittest.TestCase):
    """天气Schema测试"""
    
    def test_validate_weather_params_valid(self):
        """测试有效参数"""
        valid, msg = validate_weather_params("北京", "today")
        self.assertTrue(valid)
    
    def test_validate_weather_params_empty_city(self):
        """测试空城市名"""
        valid, msg = validate_weather_params("", "today")
        self.assertFalse(valid)
        self.assertIn("城市", msg)
    
    def test_get_weather_schema_structure(self):
        """测试Schema结构"""
        self.assertEqual(GET_WEATHER_SCHEMA["name"], "get_weather")
        self.assertIn("parameters", GET_WEATHER_SCHEMA)
        self.assertIn("city", GET_WEATHER_SCHEMA["parameters"]["properties"])


if __name__ == "__main__":
    unittest.main()
