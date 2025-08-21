#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API密钥存储原理演示和清理工具

本脚本用于演示和解释API密钥管理器的存储机制，
以及如何避免多次更新exe文件导致的密钥积累问题。
"""

import keyring
from deepseek_api.api_key_manager import ApiKeyManager


def demonstrate_storage_principle():
    """演示密钥存储原理"""
    print("=== API密钥存储原理演示 ===")
    print()

    print("1. 存储机制说明:")
    print(f"   - 服务名称: {ApiKeyManager.SERVICE_NAME}")
    print(f"   - 用户名称: {ApiKeyManager.USERNAME}")
    print("   - 存储位置: Windows凭据管理器 (WinVault)")
    print("   - 存储方式: 系统级加密存储")
    print()

    print("2. 密钥唯一性原理:")
    print("   - 每个应用使用固定的服务名称和用户名组合")
    print("   - 相同组合的密钥会被覆盖，而不是累积")
    print("   - 即使多次更新exe文件，密钥存储位置保持不变")
    print()

    # 检查当前是否有保存的密钥
    current_key = ApiKeyManager.get_api_key()
    if current_key:
        print(f"3. 当前状态: 已保存密钥 (长度: {len(current_key)} 字符)")
        print(f"   密钥前缀: {current_key[:10]}...")
    else:
        print("3. 当前状态: 未保存密钥")
    print()


def list_all_tktool_keys():
    """列出所有TKTool相关的密钥"""
    print("=== 检查TKTool相关密钥 ===")
    print()

    try:
        # 尝试获取当前密钥
        api_key = keyring.get_password(ApiKeyManager.SERVICE_NAME, ApiKeyManager.USERNAME)
        if api_key:
            print(f"找到密钥: {ApiKeyManager.SERVICE_NAME}/{ApiKeyManager.USERNAME}")
            print(f"密钥长度: {len(api_key)} 字符")
            print(f"密钥前缀: {api_key[:10]}...")
        else:
            print("未找到保存的密钥")
    except Exception as e:
        print(f"检查密钥时出错: {e}")
    print()


def clean_api_keys():
    """清理API密钥"""
    print("=== 密钥清理工具 ===")
    print()

    # 检查是否有密钥需要清理
    if not ApiKeyManager.has_api_key():
        print("没有找到需要清理的密钥")
        return

    print("发现已保存的API密钥")
    choice = input("是否要删除保存的密钥? (y/N): ").strip().lower()

    if choice in ['y', 'yes', '是']:
        if ApiKeyManager.delete_api_key():
            print("✓ 密钥已成功删除")
        else:
            print("✗ 删除密钥失败")
    else:
        print("取消删除操作")
    print()


def explain_no_accumulation():
    """解释为什么不会出现密钥积累问题"""
    print("=== 为什么不会出现密钥积累问题 ===")
    print()

    print("原理解释:")
    print("1. 固定标识符:")
    print("   - 应用使用固定的服务名称 'TKTool_DeepSeek'")
    print("   - 使用固定的用户名 'deepseek_api_key'")
    print("   - 这个组合在系统中是唯一的")
    print()

    print("2. 覆盖机制:")
    print("   - 每次保存密钥时，会覆盖之前的密钥")
    print("   - 不会创建新的存储条目")
    print("   - 系统中始终只有一个密钥条目")
    print()

    print("3. 版本无关性:")
    print("   - exe文件版本不影响密钥存储位置")
    print("   - 新版本会读取旧版本保存的密钥")
    print("   - 不需要重新输入密钥")
    print()

    print("4. 系统集成:")
    print("   - 使用Windows凭据管理器")
    print("   - 与系统安全机制集成")
    print("   - 用户级别隔离")
    print()


def test_key_overwrite():
    """测试密钥覆盖机制"""
    print("=== 密钥覆盖机制测试 ===")
    print()

    # 保存第一个测试密钥
    test_key1 = "test_key_1_" + "x" * 20
    print(f"保存测试密钥1: {test_key1[:15]}...")
    ApiKeyManager.save_api_key(test_key1)

    # 验证保存
    saved_key = ApiKeyManager.get_api_key()
    print(f"读取到的密钥: {saved_key[:15]}...")
    print(f"密钥匹配: {'✓' if saved_key == test_key1 else '✗'}")
    print()

    # 保存第二个测试密钥（覆盖第一个）
    test_key2 = "test_key_2_" + "y" * 20
    print(f"保存测试密钥2: {test_key2[:15]}...")
    ApiKeyManager.save_api_key(test_key2)

    # 验证覆盖
    saved_key = ApiKeyManager.get_api_key()
    print(f"读取到的密钥: {saved_key[:15]}...")
    print(f"密钥匹配: {'✓' if saved_key == test_key2 else '✗'}")
    print(f"覆盖成功: {'✓' if saved_key != test_key1 else '✗'}")
    print()

    # 清理测试密钥
    print("清理测试密钥...")
    ApiKeyManager.delete_api_key()
    print("测试完成")
    print()


def main():
    """主函数"""
    print("TKTool API密钥存储原理演示和管理工具")
    print("=" * 50)
    print()

    while True:
        print("请选择操作:")
        print("1. 查看存储原理说明")
        print("2. 检查当前密钥状态")
        print("3. 测试密钥覆盖机制")
        print("4. 清理保存的密钥")
        print("5. 查看完整原理解释")
        print("0. 退出")
        print()

        choice = input("请输入选择 (0-5): ").strip()
        print()

        if choice == '1':
            demonstrate_storage_principle()
        elif choice == '2':
            list_all_tktool_keys()
        elif choice == '3':
            test_key_overwrite()
        elif choice == '4':
            clean_api_keys()
        elif choice == '5':
            explain_no_accumulation()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")
            print()

        input("按回车键继续...")
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    # APIKey sk-5e4557a678e840ffbad12183dd98731f
    main()
