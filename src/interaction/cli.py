"""
命令行交互界面
"""
import sys
from src.agent.core import WeatherAgent

class CLI:
    """命令行交互界面"""
    
    def __init__(self):
        self.agent = WeatherAgent()
        self.running = False
    
    def start(self):
        """启动交互"""
        self.running = True
        self._print_welcome()
        
        while self.running:
            try:
                user_input = input("\n用户: ").strip()
                if not user_input:
                    continue
                
                if user_input.lower() in ["退出", "exit", "quit", "q"]:
                    self._print_exit()
                    break
                
                response = self.agent.chat(user_input)
                print(f"\n助手: {response}")
                
            except KeyboardInterrupt:
                self._print_exit()
                break
            except Exception as e:
                print(f"\n错误: {str(e)}")
    
    def _print_welcome(self):
        """打印欢迎信息"""
        print("=" * 50)
        print("天气查询Agent (Function Calling)")
        print("=" * 50)
        print("支持城市天气查询，例如：")
        print("  - 北京天气怎么样")
        print("  - 贵阳明天天气")
        print("  - 上海后天温度")
        print("\n输入 '退出' 结束对话")
        print("=" * 50)
    
    def _print_exit(self):
        """打印退出信息"""
        print("\n感谢使用，再见！")


def run_cli():
    """运行CLI"""
    cli = CLI()
    cli.start()
