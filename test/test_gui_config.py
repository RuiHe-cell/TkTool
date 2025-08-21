#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GUI配置加载功能
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def test_gui_config_loading():
    """测试GUI配置加载"""
    print("=== 测试GUI配置加载 ===")
    
    try:
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建主窗口实例
        app = MainWindow(root)
        
        # 检查配置是否正确加载
        print(f"测试用例数量: {app.test_count_var.get()}")
        print(f"不生成重复数据: {app.no_duplicate_var.get()}")
        print(f"删除临时文件: {app.delete_temp_files_var.get()}")
        print(f"输出目录: {app.output_dir_var.get()}")
        
        # 验证配置值
        expected_config = {
            'test_count': '15',
            'no_duplicate': True,
            'delete_temp_files': True,
            'output_dir': './custom_output'
        }
        
        actual_config = {
            'test_count': app.test_count_var.get(),
            'no_duplicate': app.no_duplicate_var.get(),
            'delete_temp_files': app.delete_temp_files_var.get(),
            'output_dir': app.output_dir_var.get()
        }
        
        if actual_config == expected_config:
            print("\n✅ 配置加载测试通过！")
            print("GUI成功加载了保存的配置")
        else:
            print("\n❌ 配置加载测试失败！")
            print(f"期望配置: {expected_config}")
            print(f"实际配置: {actual_config}")
        
        root.destroy()
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gui_config_loading()