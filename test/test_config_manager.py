#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置管理功能
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config_manager import ConfigManager

def test_config_manager():
    """测试配置管理器功能"""
    print("=== 测试配置管理器 ===")
    
    # 创建临时目录作为配置目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时配置目录: {temp_dir}")
    
    try:
        # 创建配置管理器实例
        config_manager = ConfigManager()
        # 临时修改配置目录用于测试
        from pathlib import Path
        config_manager.config_dir = Path(temp_dir)
        config_manager.config_file = Path(temp_dir) / 'user_preferences.json'
        
        print("\n1. 测试默认配置加载")
        default_config = config_manager.load_config()
        print(f"默认配置: {default_config}")
        
        print("\n2. 测试配置保存")
        test_config = {
            'test_count': '20',
            'no_duplicate': True,
            'delete_temp_files': True,
            'output_dir': './my_test_data'
        }
        
        save_result = config_manager.save_config(test_config)
        print(f"保存结果: {save_result}")
        
        print("\n3. 测试配置加载")
        loaded_config = config_manager.load_config()
        print(f"加载的配置: {loaded_config}")
        
        print("\n4. 测试单个配置值操作")
        config_manager.set_config_value('test_count', '50')
        test_count = config_manager.get_config_value('test_count')
        print(f"设置后的test_count: {test_count}")
        
        print("\n5. 测试重置为默认配置")
        config_manager.reset_to_default()
        reset_config = config_manager.load_config()
        print(f"重置后的配置: {reset_config}")
        
        print("\n6. 测试配置文件路径")
        config_path = config_manager.get_config_file_path()
        print(f"配置文件路径: {config_path}")
        
        print("\n配置管理器测试完成！")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"已清理临时目录: {temp_dir}")

def test_gui_integration():
    """测试GUI集成"""
    print("\n=== 测试GUI集成 ===")
    
    try:
        import tkinter as tk
        from gui.main_window import MainWindow
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建主窗口实例
        app = MainWindow(root)
        
        print("GUI集成测试成功！")
        print(f"当前配置: {app.user_config}")
        
        # 测试配置保存
        app.test_count_var.set('15')
        app.no_duplicate_var.set(True)
        app.delete_temp_files_var.set(True)
        app.output_dir_var.set('./custom_output')
        
        app.save_current_config()
        print("配置保存测试完成！")
        
        root.destroy()
        
    except Exception as e:
        print(f"GUI集成测试失败: {e}")

if __name__ == "__main__":
    test_config_manager()
    test_gui_integration()