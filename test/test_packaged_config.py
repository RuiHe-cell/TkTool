#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包环境下的配置功能
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config_manager import ConfigManager

def test_packaged_config_paths():
    """测试打包环境下的配置路径"""
    print("=== 测试打包环境配置路径 ===")
    
    # 模拟打包环境
    original_frozen = getattr(sys, 'frozen', False)
    original_meipass = getattr(sys, '_MEIPASS', None)
    
    try:
        # 模拟打包环境
        sys.frozen = True
        sys._MEIPASS = str(Path(__file__).parent)  # 使用当前目录作为模拟的MEIPASS
        
        print(f"模拟打包环境:")
        print(f"  sys.frozen = {sys.frozen}")
        print(f"  sys._MEIPASS = {sys._MEIPASS}")
        
        # 创建配置管理器
        config_manager = ConfigManager()
        
        print(f"\n配置路径:")
        print(f"  配置目录: {config_manager.config_dir}")
        print(f"  配置文件: {config_manager.config_file}")
        print(f"  配置目录存在: {config_manager.config_dir.exists()}")
        
        # 测试配置保存和加载
        test_config = {
            'test_count': '25',
            'no_duplicate': True,
            'delete_temp_files': False,
            'output_dir': './packaged_output'
        }
        
        print(f"\n保存测试配置: {test_config}")
        save_result = config_manager.save_config(test_config)
        print(f"保存结果: {save_result}")
        
        if save_result:
            loaded_config = config_manager.load_config()
            print(f"加载的配置: {loaded_config}")
            
            if loaded_config == test_config:
                print("\n✅ 打包环境配置测试通过！")
            else:
                print("\n❌ 打包环境配置测试失败！")
                print(f"期望: {test_config}")
                print(f"实际: {loaded_config}")
        else:
            print("\n❌ 配置保存失败！")
            
    finally:
        # 恢复原始状态
        if original_frozen:
            sys.frozen = original_frozen
        else:
            delattr(sys, 'frozen')
            
        if original_meipass:
            sys._MEIPASS = original_meipass
        elif hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')

def test_development_config_paths():
    """测试开发环境下的配置路径"""
    print("\n=== 测试开发环境配置路径 ===")
    
    # 确保在开发环境
    if hasattr(sys, 'frozen'):
        delattr(sys, 'frozen')
    if hasattr(sys, '_MEIPASS'):
        delattr(sys, '_MEIPASS')
    
    config_manager = ConfigManager()
    
    print(f"配置路径:")
    print(f"  配置目录: {config_manager.config_dir}")
    print(f"  配置文件: {config_manager.config_file}")
    print(f"  配置目录存在: {config_manager.config_dir.exists()}")
    
    # 验证路径是否正确
    expected_config_dir = Path(__file__).parent / 'config'
    if config_manager.config_dir == expected_config_dir:
        print("\n✅ 开发环境配置路径正确！")
    else:
        print("\n❌ 开发环境配置路径错误！")
        print(f"期望: {expected_config_dir}")
        print(f"实际: {config_manager.config_dir}")

if __name__ == "__main__":
    test_development_config_paths()
    test_packaged_config_paths()