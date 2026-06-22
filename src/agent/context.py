"""
对话上下文管理器 - 维护多轮对话历史，支持上下文参数继承
"""
from typing import List, Dict, Any, Optional
from config import settings

class Message:
    """对话消息"""
    def __init__(self, role: str, content: Optional[str] = None, **kwargs):
        self.role = role  # "user" / "assistant" / "system" / "tool"
        self.content = content
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        result["role"] = self.role
        if self.content is not None:
            result["content"] = self.content
        # 添加额外字段（如 tool_call_id, tool_calls 等）
        for key, value in self.__dict__.items():
            if key not in ("role", "content"):
                result[key] = value
        return result

class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.max_length = settings.MAX_CONTEXT_LENGTH
        self.last_city: Optional[str] = None  # 记住上次的城市参数
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append(Message("user", content))
        self._auto_truncate()
    
    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.messages.append(Message("assistant", content))
        self._auto_truncate()
    
    def add_assistant_tool_calls_message(self, tool_calls: List[Dict[str, Any]]):
        """添加带 tool_calls 的 assistant 消息（LLM 返回工具调用时）"""
        self.messages.append(Message("assistant", tool_calls=tool_calls))
        self._auto_truncate()
    
    def add_tool_message(self, content: str, tool_call_id: str = ""):
        """添加工具响应消息"""
        self.messages.append(Message("tool", content, tool_call_id=tool_call_id))
        self._auto_truncate()
    
    def add_system_message(self, content: str):
        """添加系统消息"""
        self.messages.append(Message("system", content))
    
    def get_context(self) -> List[Dict[str, str]]:
        """获取对话上下文"""
        return [msg.to_dict() for msg in self.messages]
    
    def update_last_city(self, city: str):
        """更新记住的城市参数"""
        self.last_city = city
    
    def get_last_city(self) -> Optional[str]:
        """获取记住的城市参数"""
        return self.last_city
    
    def _auto_truncate(self):
        """自动截断过长的对话历史"""
        if len(self.messages) > self.max_length:
            # 保留系统消息和最近的消息
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            self.messages = system_msgs + other_msgs[-(self.max_length - len(system_msgs)):]
    
    def clear(self):
        """清空上下文"""
        self.messages = []
        self.last_city = None
