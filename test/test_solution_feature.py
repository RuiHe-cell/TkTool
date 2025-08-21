#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试解题功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
import tkinter as tk

def test_solution_processing():
    """测试解题代码处理功能"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    app = MainWindow(root)
    
    # 测试代码处理
    test_code = '''
# 测试代码
lines = input_data.strip().split('\\n')
n, k = map(int, lines[0].split())
sequence = list(map(int, lines[1].split()))

# 查找两个数的和为k
seen = set()
for num in sequence:
    complement = k - num
    if complement in seen:
        print("yes")
        break
    seen.add(num)
else:
    print("no")
'''
    
    processed_code = app.process_solution_code(test_code)
    print("原始代码:")
    print(test_code)
    print("\n处理后的代码:")
    print(processed_code)
    
    # 测试代码执行
    test_input = "3 5\n1 2 3"
    try:
        result = app.execute_solution_code(processed_code, test_input)
        print(f"\n执行结果: {result}")
    except Exception as e:
        print(f"\n执行出错: {e}")
    
    root.destroy()

if __name__ == "__main__":
    test_solution_processing()