#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试"数组长度+数组元素"模板的动态循环功能
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_generator_core import DataGeneratorCore

def test_template_dynamic_loop():
    """测试模板中的动态循环功能"""
    # 读取模板配置
    with open('templates/default_templates.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    templates = data['templates']
    
    # 找到"数组长度+数组元素"模板
    array_template = None
    for template in templates:
        if template['name'] == '数组长度+数组元素':
            array_template = template
            break
    
    if not array_template:
        print("未找到'数组长度+数组元素'模板")
        return
    
    print("模板配置:")
    for i, var in enumerate(array_template['variables']):
        print(f"变量{i+1}: {var['name']}, 循环次数: {var.get('loop_count', 1)}")
    
    # 使用模板配置生成数据
    generator = DataGeneratorCore()
    configs = array_template['variables']
    
    print("\n生成的测试数据:")
    test_data = generator.generate_test_data(configs, 3)
    
    for i, data in enumerate(test_data, 1):
        parts = data.split()
        if len(parts) >= 2:
            n_value = parts[0]
            arr_values = parts[1:]
            print(f"第{i}组: n={n_value}, 数组长度={len(arr_values)}, 数组={' '.join(arr_values)}")
            
            # 验证数组长度是否等于n的值
            if len(arr_values) == int(n_value):
                print(f"  ✓ 验证通过：数组长度({len(arr_values)})等于n的值({n_value})")
            else:
                print(f"  ✗ 验证失败：数组长度({len(arr_values)})不等于n的值({n_value})")
        else:
            print(f"第{i}组: {data} (格式异常)")
        print()

if __name__ == "__main__":
    test_template_dynamic_loop()