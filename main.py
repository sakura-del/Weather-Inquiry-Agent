"""
天气查询Agent入口文件
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interaction.cli import run_cli


def main():
    """主入口"""
    print("正在初始化天气查询Agent...")
    run_cli()


if __name__ == "__main__":
    main()
