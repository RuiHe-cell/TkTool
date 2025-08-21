#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新对话框功能
"""

import sys
import os
import tkinter as tk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.update_dialog import show_update_dialog

def test_update_dialog_with_exe():
    """测试带exe链接的更新对话框"""
    print("测试带exe链接的更新对话框...")
    
    # 模拟更新数据（包含exe链接）
    update_data = {
        "level": "1.2.0",
        "update_time": "2025-01-20",
        "update_content": [
            "新增功能：三按钮更新对话框",
            "新增功能：支持exe安装包下载",
            "新增功能：优化用户界面体验",
            "修复bug：解决对话框显示问题",
            "优化：提升程序启动速度"
        ],
        "line": "https://github.com/RuiHe-cell/TkTool/releases/download/v1.2.0/TkTool-v1.2.0.exe"
    }
    
    # 模拟配置
    config = {
        "github_page_url": "https://github.com/RuiHe-cell/TkTool"
    }
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    result = show_update_dialog(root, update_data, config)
    print(f"用户操作结果: {result}")
    
    root.destroy()

def test_update_dialog_without_exe():
    """测试不带exe链接的更新对话框"""
    print("测试不带exe链接的更新对话框...")
    
    # 模拟更新数据（不包含exe链接）
    update_data = {
        "level": "1.1.5",
        "update_time": "2025-01-19",
        "update_content": [
            "修复bug：解决界面显示问题",
            "优化：提升程序性能",
            "新增功能：支持更多数据格式"
        ],
        "line": ""  # 空的exe链接
    }
    
    # 模拟配置
    config = {
        "github_page_url": "https://github.com/RuiHe-cell/TkTool"
    }
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    result = show_update_dialog(root, update_data, config)
    print(f"用户操作结果: {result}")
    
    root.destroy()

def main():
    """主函数"""
    print("=== TkTool 更新对话框测试 ===")
    print("请选择测试类型:")
    print("1. 测试带exe链接的对话框（三个按钮）")
    print("2. 测试不带exe链接的对话框（两个按钮）")
    print("3. 测试两种情况")
    
    try:
        choice = input("请输入选择 (1/2/3): ").strip()
        
        if choice == '1':
            test_update_dialog_with_exe()
        elif choice == '2':
            test_update_dialog_without_exe()
        elif choice == '3':
            print("\n--- 测试1: 带exe链接 ---")
            test_update_dialog_with_exe()
            print("\n--- 测试2: 不带exe链接 ---")
            test_update_dialog_without_exe()
        else:
            print("无效选择，默认测试两种情况")
            print("\n--- 测试1: 带exe链接 ---")
            test_update_dialog_with_exe()
            print("\n--- 测试2: 不带exe链接 ---")
            test_update_dialog_without_exe()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()