#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API密钥管理器功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_api.api_key_manager import ApiKeyManager, get_deepseek_api_key, save_deepseek_api_key, setup_api_key

def test_api_key_manager():
    """测试API密钥管理器的基本功能"""
    print("=== 测试API密钥管理器 ===")
    
    # 测试1: 检查是否有已保存的密钥
    print("\n1. 检查已保存的密钥...")
    has_key = ApiKeyManager.has_api_key()
    print(f"是否有已保存的密钥: {has_key}")
    
    if has_key:
        saved_key = ApiKeyManager.get_api_key()
        if saved_key:
            print(f"已保存的密钥: {saved_key[:10]}...{saved_key[-10:]}")
    
    # 测试2: 测试保存和获取功能
    print("\n2. 测试保存和获取功能...")
    test_key = "sk-test123456789abcdef"
    
    # 保存测试密钥
    save_result = ApiKeyManager.save_api_key(test_key)
    print(f"保存测试密钥结果: {save_result}")
    
    if save_result:
        # 获取保存的密钥
        retrieved_key = ApiKeyManager.get_api_key()
        print(f"获取的密钥: {retrieved_key}")
        print(f"密钥匹配: {retrieved_key == test_key}")
        
        # 删除测试密钥
        delete_result = ApiKeyManager.delete_api_key()
        print(f"删除测试密钥结果: {delete_result}")
    
    # 测试3: 测试便捷函数
    print("\n3. 测试便捷函数...")
    
    # 保存密钥
    save_result = save_deepseek_api_key(test_key)
    print(f"便捷函数保存结果: {save_result}")
    
    if save_result:
        # 获取密钥
        retrieved_key = get_deepseek_api_key()
        print(f"便捷函数获取结果: {retrieved_key}")
        
        # 清理
        ApiKeyManager.delete_api_key()
    
    print("\n=== 测试完成 ===")

def test_keyring_availability():
    """测试keyring库是否可用"""
    print("=== 测试keyring库可用性 ===")
    
    try:
        import keyring
        try:
            print(f"keyring版本: {keyring.__version__}")
        except AttributeError:
            print("keyring库已导入（版本信息不可用）")
        
        # 获取当前后端
        backend = keyring.get_keyring()
        print(f"当前keyring后端: {backend}")
        
        # 测试基本功能
        service = "test_service"
        username = "test_user"
        password = "test_password"
        
        # 设置密码
        keyring.set_password(service, username, password)
        print("设置测试密码: 成功")
        
        # 获取密码
        retrieved = keyring.get_password(service, username)
        print(f"获取测试密码: {retrieved}")
        print(f"密码匹配: {retrieved == password}")
        
        # 删除密码
        keyring.delete_password(service, username)
        print("删除测试密码: 成功")
        
        print("keyring库工作正常！")
        
    except ImportError:
        print("错误: keyring库未安装")
        return False
    except Exception as e:
        print(f"keyring测试失败: {e}")
        return False
    
    print("=== keyring测试完成 ===")
    return True

if __name__ == "__main__":
    print("开始测试API密钥管理功能...\n")
    
    # 首先测试keyring库
    if test_keyring_availability():
        print()
        # 然后测试API密钥管理器
        test_api_key_manager()
    else:
        print("keyring库不可用，无法继续测试")
    
    print("\n测试结束")