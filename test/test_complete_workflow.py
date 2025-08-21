#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的解题工作流程
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from core.file_manager_core import FileManagerCore
import tkinter as tk

def test_complete_workflow():
    """测试完整的解题工作流程"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"测试目录: {temp_dir}")
    
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        app = MainWindow(root)
        
        # 模拟测试数据
        test_data = [
            "3 5\n1 2 3",
            "4 7\n2 3 4 5",
            "2 10\n1 9"
        ]
        
        # 解题代码
        solution_code = '''
# 和为k问题解题代码
lines = input_data.strip().split('\\n')
n, k = map(int, lines[0].split())
sequence = list(map(int, lines[1].split()))

# 使用哈希表查找两个数的和为k
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
        
        print("\n=== 测试解题代码处理 ===")
        processed_code = app.process_solution_code(solution_code)
        print("代码处理成功")
        
        print("\n=== 测试代码执行 ===")
        solutions = []
        for i, data in enumerate(test_data):
            result = app.execute_solution_code(processed_code, data)
            solutions.append(result)
            print(f"测试用例 {i+1}: {data.replace(chr(10), ' | ')} -> {result}")
        
        print("\n=== 测试文件保存 ===")
        file_manager = FileManagerCore()
        save_result = file_manager.save_with_solutions(test_data, solutions, temp_dir)
        
        print(f"保存结果: {save_result}")
        print(f"创建的文件数量: {save_result['file_count']}")
        
        # 验证文件内容
        print("\n=== 验证文件内容 ===")
        for i in range(len(test_data)):
            in_file = os.path.join(temp_dir, f"test{i+1:02d}.in")
            out_file = os.path.join(temp_dir, f"test{i+1:02d}.out")
            
            if os.path.exists(in_file) and os.path.exists(out_file):
                with open(in_file, 'r', encoding='utf-8') as f:
                    in_content = f.read().strip()
                with open(out_file, 'r', encoding='utf-8') as f:
                    out_content = f.read().strip()
                
                print(f"test{i+1:02d}.in: {in_content.replace(chr(10), ' | ')}")
                print(f"test{i+1:02d}.out: {out_content}")
                print()
        
        print("测试完成！")
        root.destroy()
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"已清理临时目录: {temp_dir}")

if __name__ == "__main__":
    test_complete_workflow()