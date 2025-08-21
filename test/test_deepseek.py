#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek功能
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_api.deepseek_client import DeepSeekClient
from deepseek_api.prompt_template import generate_coding_prompt


def test_deepseek_client():
    """测试DeepSeek客户端基本功能"""
    print("=== 测试DeepSeek客户端 ===")

    # 测试网络连接
    client = DeepSeekClient("test_key")
    network_ok = client.check_network()
    print(f"网络连接: {'正常' if network_ok else '失败'}")

    # 测试提示词生成
    problem = "给定两个整数，计算它们的和"
    test_data = "3 5"
    prompt = generate_coding_prompt(problem, test_data)
    print(f"\n生成的提示词长度: {len(prompt)} 字符")
    print(f"提示词预览: {prompt[:200]}...")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_deepseek_client()
