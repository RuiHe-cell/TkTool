#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分隔符功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_separator_functionality():
    """测试分隔符功能"""
    generator = DataGeneratorCore()
    
    print("=== 测试分隔符功能 ===")
    
    # 测试1: 单个变量，换行分隔符，循环3次
    print("\n测试1: 单个变量n，换行分隔符，循环3次")
    configs = [
        {
            'name': 'n',
            'data_type': '整数',
            'source_type': '数据范围',
            'min_value': 1,
            'max_value': 3,
            'loop_count': '3',
            'separator': '换行'
        }
    ]
    
    result = generator.generate_test_data(configs, 1)
    print("生成结果:")
    print(repr(result[0]))  # 使用repr显示转义字符
    print("实际显示:")
    print(result[0])
    
    # 测试2: 两个变量，都使用换行分隔符
    print("\n测试2: 两个变量，都使用换行分隔符")
    configs = [
        {
            'name': 'n',
            'data_type': '整数',
            'source_type': '数据范围',
            'min_value': 1,
            'max_value': 5,
            'loop_count': '1',
            'separator': '换行'
        },
        {
            'name': 'arr',
            'data_type': '整数',
            'source_type': '数据范围',
            'min_value': 1,
            'max_value': 10,
            'loop_count': 'n',
            'separator': '空格'
        }
    ]
    
    result = generator.generate_test_data(configs, 1)
    print("生成结果:")
    print(repr(result[0]))
    print("实际显示:")
    print(result[0])
    
    # 测试3: 模拟用户需求 - 生成如下格式的数据:
    # 3
    # 1
    # 2
    # 3
    print("\n测试3: 模拟用户需求格式")
    configs = [
        {
            'name': 'n',
            'data_type': '整数',
            'source_type': '选择列表',
            'choices': [3],
            'loop_count': '1',
            'separator': '换行'
        },
        {
            'name': 'numbers',
            'data_type': '整数',
            'source_type': '数据范围',
            'min_value': 1,
            'max_value': 3,
            'loop_count': 'n',
            'separator': '换行'
        }
    ]
    
    result = generator.generate_test_data(configs, 1)
    print("生成结果:")
    print(repr(result[0]))
    print("实际显示:")
    print(result[0])
    
    # 测试4: 不同分隔符组合
    print("\n测试4: 不同分隔符组合")
    configs = [
        {
            'name': 'a',
            'data_type': '整数',
            'source_type': '选择列表',
            'choices': [1, 2, 3],
            'loop_count': '3',
            'separator': '逗号'
        },
        {
            'name': 'b',
            'data_type': '字符串',
            'source_type': '选择列表',
            'choices': ['x', 'y', 'z'],
            'loop_count': '2',
            'separator': '制表符'
        }
    ]
    
    result = generator.generate_test_data(configs, 1)
    print("生成结果:")
    print(repr(result[0]))
    print("实际显示:")
    print(result[0])

if __name__ == "__main__":
    test_separator_functionality()