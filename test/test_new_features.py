#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新功能：来自代码数据源和不重复数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_code_generation():
    """测试来自代码的数据生成"""
    print("=== 测试来自代码数据生成 ===")
    
    generator = DataGeneratorCore()
    
    # 测试整数代码生成
    config_int = {
        'name': 'test_int',
        'data_type': '整数',
        'source_type': '来自代码',
        'separator': '空格',
        'loop_count': 1,
        'custom_code': '''
def generate_data():
    import random
    return random.randint(100, 200)
'''
    }
    
    print("整数代码生成测试:")
    for i in range(5):
        value = generator._generate_single_value(config_int)
        print(f"  生成值 {i+1}: {value} (类型: {type(value).__name__})")
    
    # 测试字符串代码生成
    config_str = {
        'name': 'test_str',
        'data_type': '字符串',
        'source_type': '来自代码',
        'separator': '空格',
        'loop_count': 1,
        'custom_code': '''
def generate_data():
    import random
    import string
    length = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters, k=length))
'''
    }
    
    print("\n字符串代码生成测试:")
    for i in range(5):
        value = generator._generate_single_value(config_str)
        print(f"  生成值 {i+1}: {value} (长度: {len(value)})")
    
    # 测试浮点数代码生成
    config_float = {
        'name': 'test_float',
        'data_type': '浮点数',
        'source_type': '来自代码',
        'separator': '空格',
        'loop_count': 1,
        'custom_code': '''
def generate_data():
    import random
    return round(random.uniform(0.1, 99.9), 2)
'''
    }
    
    print("\n浮点数代码生成测试:")
    for i in range(5):
        value = generator._generate_single_value(config_float)
        print(f"  生成值 {i+1}: {value} (类型: {type(value).__name__})")

def test_no_duplicate():
    """测试不重复数据生成"""
    print("\n=== 测试不重复数据生成 ===")
    
    generator = DataGeneratorCore()
    
    # 测试小范围数据的不重复生成
    config = {
        'name': 'test_range',
        'data_type': '整数',
        'source_type': '数据范围',
        'separator': '空格',
        'loop_count': 1,
        'min_value': '1',
        'max_value': '5'
    }
    
    print("小范围整数不重复测试 (1-5，生成10个):")
    data = generator.generate_test_data([config], 10, no_duplicate=True)
    print(f"  生成了 {len(data)} 个数据组")
    print(f"  数据: {data}")
    print(f"  去重后数量: {len(set(data))}")
    
    # 测试选择列表的不重复生成
    config_choice = {
        'name': 'test_choice',
        'data_type': '字符串',
        'source_type': '选择列表',
        'separator': '空格',
        'loop_count': 1,
        'choices': ['apple', 'banana', 'cherry']
    }
    
    print("\n选择列表不重复测试 (3个选项，生成5个):")
    data = generator.generate_test_data([config_choice], 5, no_duplicate=True)
    print(f"  生成了 {len(data)} 个数据组")
    print(f"  数据: {data}")
    print(f"  去重后数量: {len(set(data))}")

def test_complete_workflow():
    """测试完整的工作流程"""
    print("\n=== 测试完整工作流程 ===")
    
    generator = DataGeneratorCore()
    
    # 混合配置：包含代码生成和传统生成
    configs = [
        {
            'name': 'id',
            'data_type': '整数',
            'source_type': '来自代码',
            'separator': '空格',
            'loop_count': 1,
            'custom_code': '''
def generate_data():
    import random
    return random.randint(1000, 9999)
'''
        },
        {
            'name': 'name',
            'data_type': '字符串',
            'source_type': '选择列表',
            'separator': '空格',
            'loop_count': 1,
            'choices': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        },
        {
            'name': 'score',
            'data_type': '浮点数',
            'source_type': '数据范围',
            'separator': '换行',
            'loop_count': 1,
            'min_value': '60.0',
            'max_value': '100.0'
        }
    ]
    
    print("混合配置测试 (包含代码生成):")
    data = generator.generate_test_data(configs, 3, no_duplicate=False)
    for i, group in enumerate(data, 1):
        print(f"  数据组 {i}: {repr(group)}")
    
    print("\n混合配置不重复测试:")
    data = generator.generate_test_data(configs, 5, no_duplicate=True)
    print(f"  生成了 {len(data)} 个不重复数据组")
    for i, group in enumerate(data, 1):
        print(f"  数据组 {i}: {repr(group)}")

if __name__ == "__main__":
    test_code_generation()
    test_no_duplicate()
    test_complete_workflow()
    print("\n=== 所有测试完成 ===")