#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字符串随机长度功能
验证"1,10"格式是否正确工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_random_length():
    """测试随机长度功能"""
    generator = DataGeneratorCore()
    
    print("=== 测试字符集合随机长度功能 ===")
    
    # 测试配置：字符集合 + 随机长度
    config = {
        'name': 'random_str',
        'data_type': '字符串',
        'source_type': '字符集合',
        'charset': 'a-z',
        'string_length': '3,8',  # 随机长度3-8
        'separator': '空格',
        'loop_count': 1
    }
    
    print(f"配置: {config}")
    print("\n生成10个随机长度字符串:")
    
    for i in range(10):
        result = generator._generate_from_charset(config)
        print(f"第{i+1}个: '{result}' (长度: {len(result)})")
    
    print("\n=== 测试数据范围随机长度功能 ===")
    
    # 测试配置：数据范围 + 随机长度
    config2 = {
        'name': 'random_ascii',
        'data_type': '字符串',
        'source_type': '数据范围',
        'min_value': '65',  # ASCII 'A'
        'max_value': '90',  # ASCII 'Z'
        'string_length': '2,6',  # 随机长度2-6
        'separator': '空格',
        'loop_count': 1
    }
    
    print(f"配置: {config2}")
    print("\n生成10个随机长度大写字母字符串:")
    
    for i in range(10):
        result = generator._generate_from_range(config2)
        print(f"第{i+1}个: '{result}' (长度: {len(result)})")
    
    print("\n=== 测试固定长度功能 ===")
    
    # 测试固定长度
    config3 = {
        'name': 'fixed_str',
        'data_type': '字符串',
        'source_type': '字符集合',
        'charset': '0-9',
        'string_length': '5',  # 固定长度5
        'separator': '空格',
        'loop_count': 1
    }
    
    print(f"配置: {config3}")
    print("\n生成5个固定长度字符串:")
    
    for i in range(5):
        result = generator._generate_from_charset(config3)
        print(f"第{i+1}个: '{result}' (长度: {len(result)})")
    
    print("\n=== 测试完整数据生成 ===")
    
    # 测试完整的数据生成流程
    configs = [
        {
            'name': 'n',
            'data_type': '整数',
            'source_type': '数据范围',
            'min_value': '3',
            'max_value': '6',
            'separator': '空格',
            'loop_count': 1
        },
        {
            'name': 'words',
            'data_type': '字符串',
            'source_type': '字符集合',
            'charset': 'a-z',
            'string_length': '4,10',  # 随机长度4-10
            'separator': '空格',
            'loop_count': 'n'
        }
    ]
    
    print("配置: 生成n个随机长度单词")
    test_data = generator.generate_test_data(configs, 3)
    
    for i, data in enumerate(test_data, 1):
        parts = data.strip().split()
        n = int(parts[0])
        words = parts[1:]
        print(f"第{i}组: n={n}, 单词数={len(words)}, 单词长度={[len(w) for w in words]}")
        print(f"  数据: {data.strip()}")

if __name__ == "__main__":
    test_random_length()