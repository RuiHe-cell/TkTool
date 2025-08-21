#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调试输出 - 验证API调用次数
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_api.deepseek_dialog import DeepSeekDialog
from deepseek_api.api_key_manager import ApiKeyManager
import tkinter as tk

def test_single_api_call():
    """测试单次API调用"""
    print("=== 测试单次API调用 ===")
    print()
    
    # 检查是否有保存的API密钥
    api_key = ApiKeyManager.get_api_key()
    if not api_key:
        print("未找到保存的API密钥，请先在主程序中设置API密钥")
        return
    
    print(f"使用API密钥: {api_key[:10]}...")
    
    # 创建根窗口（隐藏）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        print("\n开始创建DeepSeekDialog...")
        
        # 创建DeepSeek对话
        dialog = DeepSeekDialog(
            parent=root,
            api_key=api_key,
            problem_description="计算两个数的和",
            test_data="5 3"
        )
        
        print("DeepSeekDialog创建完成")
        print("\n调用start_generation()...")
        
        # 开始生成（这会触发API调用）
        dialog.start_generation()
        
        print("\n请观察上面的调试输出，确认API调用次数")
        print("如果看到重复的调试信息，说明API被调用了多次")
        
        # 等待用户关闭对话框
        root.mainloop()
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        root.destroy()

def main():
    """主函数"""
    print("DeepSeek API调用次数测试")
    print("=" * 40)
    print()
    
    print("说明:")
    print("- 此测试将创建一个DeepSeek对话并调用API")
    print("- 请观察控制台输出的调试信息")
    print("- 正常情况下，每个调试信息应该只出现一次")
    print("- 如果出现重复，说明API被调用了多次")
    print()
    
    input("按回车键开始测试...")
    
    test_single_api_call()
    
    print("\n测试完成！")
    print("请检查上面的调试输出，确认API调用情况。")

if __name__ == "__main__":
    main()