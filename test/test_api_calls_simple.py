#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API调用测试 - 不使用GUI
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_api.deepseek_client import DeepSeekClient
from deepseek_api.prompt_template import generate_coding_prompt
from deepseek_api.api_key_manager import ApiKeyManager

def test_direct_api_call():
    """直接测试API调用"""
    print("=== 直接API调用测试 ===")
    
    # 获取API密钥
    api_key = ApiKeyManager.get_api_key()
    if not api_key:
        print("未找到保存的API密钥")
        return
    
    print(f"使用API密钥: {api_key[:10]}...")
    
    # 创建客户端
    client = DeepSeekClient(api_key)
    
    # 生成提示
    prompt = generate_coding_prompt("计算两个数的和", "5 3")
    
    messages = [
        {"role": "system", "content": "你是一个专业的Python编程助手。"},
        {"role": "user", "content": prompt}
    ]
    
    print("\n开始调用API...")
    
    try:
        # 调用API
        response_chunks = []
        for chunk in client.chat_completion_stream(messages):
            if chunk:
                response_chunks.append(chunk)
        
        full_response = ''.join(response_chunks)
        print(f"\nAPI调用完成，收到响应长度: {len(full_response)} 字符")
        print(f"响应内容预览: {full_response[:100]}...")
        
    except Exception as e:
        print(f"API调用出错: {e}")

def main():
    """主函数"""
    print("DeepSeek API单次调用测试")
    print("=" * 30)
    print()
    
    print("此测试将直接调用DeepSeek API一次")
    print("请观察调试输出，确认只有一次API调用")
    print()
    
    test_direct_api_call()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()