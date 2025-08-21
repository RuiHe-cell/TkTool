#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动测试更新对话框功能
"""

import sys
import os
import tkinter as tk
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.update_dialog import show_update_dialog

def test_update_dialog_with_exe():
    """测试带exe链接的更新对话框"""
    print("正在显示带exe链接的更新对话框（三个按钮）...")
    
    # 模拟更新数据（包含exe链接）
    update_data = {
        "level": "1.2.0",
        "update_time": "2025-01-20",
        "update_content": [
            "新增功能：三按钮更新对话框",
            "新增功能：支持exe安装包下载",
            "新增功能：优化用户界面体验",
            "修复bug：解决对话框显示问题",
            "优化：提升程序启动速度",
            "新增功能：支持自定义主题",
            "修复bug：解决内存泄漏问题"
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
    return result

def test_update_dialog_without_exe():
    """测试不带exe链接的更新对话框"""
    print("正在显示不带exe链接的更新对话框（两个按钮）...")
    
    # 模拟更新数据（不包含exe链接）
    update_data = {
        "level": "1.1.5",
        "update_time": "2025-01-19",
        "update_content": [
            "修复bug：解决界面显示问题",
            "优化：提升程序性能",
            "新增功能：支持更多数据格式",
            "修复bug：解决配置文件读取问题",
            "优化：改进错误处理机制"
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
    return result

def main():
    """主函数"""
    print("=== TkTool 更新对话框自动测试 ===")
    print("即将自动展示两种更新对话框...\n")
    
    try:
        # 测试1: 带exe链接的对话框
        print("--- 测试1: 带exe链接的对话框 ---")
        print("此对话框包含三个按钮：📦 下载安装包、🔗 查看GitHub、❌ 关闭")
        result1 = test_update_dialog_with_exe()
        
        print(f"\n测试1完成，结果: {result1}")
        print("等待3秒后进行下一个测试...\n")
        time.sleep(3)
        
        # 测试2: 不带exe链接的对话框
        print("--- 测试2: 不带exe链接的对话框 ---")
        print("此对话框包含两个按钮：🔗 查看GitHub、❌ 关闭")
        result2 = test_update_dialog_without_exe()
        
        print(f"\n测试2完成，结果: {result2}")
        print("\n=== 所有测试完成 ===")
        print("\n功能说明:")
        print("1. 当update.json中的line字段有值时，显示三个按钮")
        print("2. 当update.json中的line字段为空时，只显示两个按钮")
        print("3. 📦 下载安装包按钮：打开line字段中的exe下载链接")
        print("4. 🔗 查看GitHub按钮：打开GitHub仓库页面")
        print("5. ❌ 关闭按钮：关闭对话框")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()