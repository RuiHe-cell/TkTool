#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试取值范围支持变量引用功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_variable_range():
    """测试取值范围支持变量引用"""
    print("=== 测试取值范围支持变量引用 ===")
    
    generator = DataGeneratorCore()
    
    # 测试配置：生成 L R，确保 R > L
    configs = [
        {
            'name': 'L',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '空格',
            'loop_count': '1',
            'min_value': '1',
            'max_value': '10'
        },
        {
            'name': 'R',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '换行',
            'loop_count': '1',
            'min_value': 'L',  # 使用变量L作为最小值
            'max_value': '20'  # 固定最大值
        }
    ]
    
    print("\n配置说明：")
    print("- L: 整数范围 1-10")
    print("- R: 整数范围 L-20 (使用变量L作为最小值)")
    print("- 预期结果：R >= L")
    
    print("\n生成的测试数据：")
    for i in range(10):
        result = generator.generate_test_data(configs, 1)[0]
        parts = result.split()
        if len(parts) >= 2:
            L_val = int(parts[0])
            R_val = int(parts[1])
            status = "✓" if R_val >= L_val else "✗"
            print(f"{i+1:2d}. L={L_val:2d}, R={R_val:2d} {status}")
        else:
            print(f"{i+1:2d}. 解析失败: {result}")

def test_complex_variable_range():
    """测试复杂的变量引用场景"""
    print("\n=== 测试复杂变量引用场景 ===")
    
    generator = DataGeneratorCore()
    
    # 测试配置：A B C，其中 B 的范围是 A 到 A+5，C 的范围是 B 到 B+3
    configs = [
        {
            'name': 'A',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '空格',
            'loop_count': '1',
            'min_value': '5',
            'max_value': '15'
        },
        {
            'name': 'B',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '空格',
            'loop_count': '1',
            'min_value': 'A',  # 使用变量A
            'max_value': '25'  # A的最大值是15，所以B最大可能是25
        },
        {
            'name': 'C',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '换行',
            'loop_count': '1',
            'min_value': 'B',  # 使用变量B
            'max_value': '30'  # B的最大值是25，所以C最大可能是30
        }
    ]
    
    print("\n配置说明：")
    print("- A: 整数范围 5-15")
    print("- B: 整数范围 A-25 (使用变量A作为最小值)")
    print("- C: 整数范围 B-30 (使用变量B作为最小值)")
    print("- 预期结果：A <= B <= C")
    
    print("\n生成的测试数据：")
    for i in range(8):
        result = generator.generate_test_data(configs, 1)[0]
        parts = result.split()
        if len(parts) >= 3:
            A_val = int(parts[0])
            B_val = int(parts[1])
            C_val = int(parts[2])
            status1 = "✓" if A_val <= B_val else "✗"
            status2 = "✓" if B_val <= C_val else "✗"
            status_all = "✓" if A_val <= B_val <= C_val else "✗"
            print(f"{i+1}. A={A_val:2d}, B={B_val:2d}, C={C_val:2d} | A<=B:{status1} B<=C:{status2} 总体:{status_all}")
        else:
            print(f"{i+1}. 解析失败: {result}")

def test_loop_with_variable_range():
    """测试循环次数和变量范围的组合"""
    print("\n=== 测试循环次数和变量范围的组合 ===")
    
    generator = DataGeneratorCore()
    
    # 测试配置：N 表示数量，然后生成 N 个在 1 到 N*2 范围内的数
    configs = [
        {
            'name': 'N',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '换行',
            'loop_count': '1',
            'min_value': '3',
            'max_value': '5'
        },
        {
            'name': 'nums',
            'data_type': '整数',
            'source_type': '数据范围',
            'separator': '空格',
            'loop_count': 'N',  # 使用变量N作为循环次数
            'min_value': '1',
            'max_value': '10'  # 简化范围，不使用N*2以避免复杂计算
        }
    ]
    
    print("\n配置说明：")
    print("- N: 整数范围 3-5")
    print("- nums: 生成N个整数，每个在1-10范围内")
    print("- 预期结果：第一行是N，第二行有N个数字")
    
    print("\n生成的测试数据：")
    for i in range(5):
        result = generator.generate_test_data(configs, 1)[0]
        lines = result.strip().split('\n')
        if len(lines) >= 2:
            N_val = int(lines[0])
            nums = lines[1].split()
            actual_count = len(nums)
            status = "✓" if actual_count == N_val else "✗"
            print(f"{i+1}. N={N_val}, 实际生成{actual_count}个数 {status}")
            print(f"   数字: {' '.join(nums)}")
        else:
            print(f"{i+1}. 解析失败: {result}")

if __name__ == "__main__":
    test_variable_range()
    test_complex_variable_range()
    test_loop_with_variable_range()
    print("\n=== 测试完成 ===")