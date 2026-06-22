import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM配置
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # 天气API配置
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_HOST: str = os.getenv("WEATHER_API_HOST", "")  # 新版和风天气专属API Host
    
    # 上下文配置
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", "10"))  # 最大对话轮数
    MAX_TOKEN_PER_REQUEST: int = int(os.getenv("MAX_TOKEN_PER_REQUEST", "4000"))
    
    # 系统配置
    SYSTEM_PROMPT: str = """你是一个天气查询助手。用户询问天气时，你需要调用get_weather工具获取天气信息。
    仅当用户提问与天气相关时才调用工具，其他问题直接回答。
    回答时使用友好自然的语言。"""

settings = Settings()
