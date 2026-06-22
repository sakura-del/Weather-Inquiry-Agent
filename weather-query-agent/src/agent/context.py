"""
消息上下文管理 - 管理对话历史和上下文参数
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Message:
    """对话消息"""
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """对话上下文管理器"""
    
    def __init__(self, max_length: int = 100):
        """
        初始化上下文管理器
        
        Args:
            max_length: 最大消息数量，超过则自动截断旧消息
        """
        self.messages: List[Message] = []
        self.max_length = max_length
        self._context_params: Dict[str, Any] = {}
    
    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.messages.append(Message(role="user", content=content))
        self._auto_truncate()
    
    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.messages.append(Message(role="assistant", content=content))
        self._auto_truncate()
    
    def _auto_truncate(self) -> None:
        """自动截断超出最大长度的消息"""
        if len(self.messages) > self.max_length:
            # 保留最新的消息
            self.messages = self.messages[-self.max_length:]
    
    def update_last_city(self, city: str) -> None:
        """更新上下文中最后一个城市参数"""
        self._context_params["last_city"] = city
    
    def get_last_city(self) -> Optional[str]:
        """获取上下文中最后一个城市参数"""
        return self._context_params.get("last_city")
    
    def get_messages(self) -> List[Message]:
        """获取所有消息"""
        return self.messages.copy()
    
    def clear(self) -> None:
        """清空上下文"""
        self.messages.clear()
        self._context_params.clear()
