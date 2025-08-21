#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试循环功能
"""

import sys
sys.path.append('.')

from core.data_generator_core import DataGeneratorCore

def test_loop_feature():
    """测试循环功能"""
    generator = DataGeneratorCore()
    generator.set_seed(42)  # 设置固定种子以便测试
    
    # 测试配置：类似于用户的需求
    configs = [
        {
            'name': 'n',
            'data_type': '整数',
            'source_type': '选择列表',
            'separator': '换行',
            'choices': ['9'],
            'loop_count': 1
        },
        {
            'name': 'k',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '换行',
            'min_value': '10',
            'max_value': '20',
            'loop_count': 1
        },
        {
            'name': 'arr',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '空格',
            'min_value': '1',
            'max_value': '9',
            'loop_count': 9
        }
    ]
    
    # 生成测试数据
    test_data = generator.generate_test_data(configs, 3)
    
    print("循环功能测试结果：")
    print("=" * 50)
    
    for i, data in enumerate(test_data, 1):
        print(f"测试数据 {i}:")
        print(data)
        print("-" * 30)
    
    print("\n说明：")
    print("- 第一行是n=9（固定值）")
    print("- 第二行是k（10-20之间的随机数）")
    print("- 第三行是9个1-9之间的随机数（使用循环功能生成）")

if __name__ == "__main__":
    test_loop_feature()