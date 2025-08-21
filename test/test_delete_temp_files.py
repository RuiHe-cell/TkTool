#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除临时文件功能
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.file_manager_core import FileManagerCore

def test_delete_temp_files():
    """测试删除临时文件功能"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"测试目录: {temp_dir}")
    
    try:
        file_manager = FileManagerCore()
        
        # 测试数据
        test_data = [
            "5\n1 2 3 4 5",
            "3\n10 20 30",
            "4\n100 200 300 400"
        ]
        
        print("\n=== 测试1: 不删除临时文件 ===")
        result1 = file_manager.save_test_files(test_data, temp_dir, "test", True, False)
        print(f"创建的文件: {len(result1['created_files'])}")
        print(f"zip文件: {result1.get('zip_file', 'None')}")
        
        # 检查文件是否存在
        for file_path in result1['created_files']:
            exists = os.path.exists(file_path)
            print(f"文件 {os.path.basename(file_path)} 存在: {exists}")
        
        print("\n=== 测试2: 删除临时文件 ===")
        result2 = file_manager.save_test_files(test_data, temp_dir, "test2", True, True)
        print(f"创建的文件: {len(result2['created_files'])}")
        print(f"zip文件: {result2.get('zip_file', 'None')}")
        print(f"删除的临时文件: {len(result2.get('deleted_temp_files', []))}")
        
        # 检查文件是否被删除
        for file_path in result2['created_files']:
            exists = os.path.exists(file_path)
            print(f"文件 {os.path.basename(file_path)} 存在: {exists}")
        
        # 检查zip文件是否存在
        zip_exists = os.path.exists(result2['zip_file'])
        print(f"zip文件存在: {zip_exists}")
        
        print("\n=== 测试3: 带解答的文件删除 ===")
        solutions = ["15", "60", "1000"]
        result3 = file_manager.save_with_solutions(test_data, solutions, temp_dir, "test3", True)
        print(f"创建的文件: {len(result3['created_files'])}")
        print(f"删除的临时文件: {len(result3.get('deleted_temp_files', []))}")
        
        # 检查文件是否被删除
        for file_path in result3['created_files']:
            exists = os.path.exists(file_path)
            print(f"文件 {os.path.basename(file_path)} 存在: {exists}")
        
        print("\n测试完成！")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"已清理临时目录: {temp_dir}")

if __name__ == "__main__":
    test_delete_temp_files()