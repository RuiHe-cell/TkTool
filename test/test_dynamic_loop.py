#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试动态循环功能
验证循环次数能否引用前面变量的值
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_dynamic_loop():
    """测试动态循环功能"""
    generator = DataGeneratorCore()
    
    # 测试配置：n=5，然后生成5个1-9之间的数字
    configs = [
        {
            "name": "n",
            "data_type": "整数",
            "source_type": "数据范围",
            "min_value": "3",
            "max_value": "7",
            "separator": "空格",
            "loop_count": 1
        },
        {
            "name": "arr",
            "data_type": "整数",
            "source_type": "数据范围",
            "min_value": "1",
            "max_value": "9",
            "separator": "空格",
            "loop_count": "n"  # 引用前面的n变量
        }
    ]
    
    print("测试动态循环功能：")
    print("配置：n为3-7之间的随机数，arr为n个1-9之间的随机数")
    print("\n生成的测试数据：")
    
    # 生成3组测试数据
    test_data = generator.generate_test_data(configs, 3)
    
    for i, data in enumerate(test_data, 1):
        parts = data.split()
        n_value = parts[0]
        arr_values = parts[1:]
        print(f"第{i}组: n={n_value}, 数组长度={len(arr_values)}, 数组={' '.join(arr_values)}")
        
        # 验证数组长度是否等于n的值
        if len(arr_values) == int(n_value):
            print(f"  ✓ 验证通过：数组长度({len(arr_values)})等于n的值({n_value})")
        else:
            print(f"  ✗ 验证失败：数组长度({len(arr_values)})不等于n的值({n_value})")
        print()

if __name__ == "__main__":
    test_dynamic_loop()