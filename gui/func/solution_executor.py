#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解题代码执行器
负责处理解题代码的执行、转换和结果保存
"""

import io
import sys
from typing import List
from tkinter import messagebox


class SolutionExecutor:
    """解题代码执行器类"""
    
    def __init__(self, file_manager):
        """初始化解题代码执行器
        
        Args:
            file_manager: 文件管理器实例
        """
        self.file_manager = file_manager
    
    def execute_and_save_solution(self, code: str, test_data: List[str], output_dir: str, 
                                editor_window, delete_temp_files: bool = False):
        """执行解题代码并保存结果"""
        try:
            # 处理代码：将print语句转换为return语句
            processed_code = self.process_solution_code(code)

            # 执行代码获取所有测试用例的结果
            solutions = []
            for i, data in enumerate(test_data):
                try:
                    result = self.execute_solution_code(processed_code, data)
                    solutions.append(str(result))
                except Exception as e:
                    messagebox.showerror("执行错误", f"执行第{i + 1}个测试用例时出错：{str(e)}")
                    return

            # 使用文件管理器保存带解答的文件
            save_result = self.file_manager.save_with_solutions(test_data, solutions, output_dir,
                                                                delete_temp_files=delete_temp_files)

            # 关闭编辑器窗口
            editor_window.destroy()

            # 显示成功消息
            success_msg = (f"成功生成 {len(test_data)} 组测试数据和解答！\n"
                           f"输出目录：{output_dir}\n"
                           f"文件数量：{save_result['file_count']}")

            if delete_temp_files and 'deleted_temp_files' in save_result:
                success_msg += f"\n已删除临时文件：{len(save_result['deleted_temp_files'])} 个"

            messagebox.showinfo("成功", success_msg)

        except Exception as e:
            messagebox.showerror("错误", f"处理解题代码时出错：{str(e)}")
    
    def process_solution_code(self, code: str) -> str:
        """处理解题代码，将print语句转换为return语句"""
        lines = code.split('\n')
        has_function = False
        has_main = False

        # 检测是否有函数定义和main函数
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('def ') and not stripped_line.startswith('def #'):
                has_function = True
                if 'main(' in stripped_line:
                    has_main = True

        # 如果有函数但没有main函数，抛出异常
        if has_function and not has_main:
            raise Exception("代码包含函数定义但缺少main函数入口点。请添加main()函数作为程序入口。")

        # 如果包含函数，直接返回原始代码，不做任何转换
        if has_function:
            return code

        # 对于非函数代码，进行print到return的转换
        processed_lines = []
        for line in lines:
            stripped_line = line.strip()
            # 跳过注释行
            if stripped_line.startswith('#'):
                processed_lines.append(line)
                continue

            # 查找print语句并转换为return
            if stripped_line.startswith('print(') and stripped_line.endswith(')'):
                # 提取print括号内的内容
                content = stripped_line[6:-1]  # 去掉'print('和')'
                # 保持原有的缩进
                indent = len(line) - len(line.lstrip())
                processed_lines.append(' ' * indent + f'return {content}')
            else:
                processed_lines.append(line)

        return '\n'.join(processed_lines)
    
    def execute_solution_code(self, code: str, input_data: str) -> str:
        """执行解题代码"""
        # 创建执行环境
        namespace = {'input_data': input_data}

        # 检测是否包含函数定义
        has_function = any(line.strip().startswith('def ') and not line.strip().startswith('def #')
                           for line in code.split('\n'))

        if has_function:
            # 如果包含函数，直接执行原始代码并调用main函数
            try:
                # 执行代码定义所有函数
                exec(code, namespace)

                # 调用main函数并获取返回值
                if 'main' in namespace and callable(namespace['main']):
                    result = namespace['main']()
                    return str(result) if result is not None else ""
                else:
                    raise Exception("找不到main函数")

            except Exception as e:
                # 如果执行失败，尝试捕获print输出作为备选方案
                try:
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = io.StringIO()

                    # 重新执行代码
                    exec(code, {'input_data': input_data})

                    # 如果有main函数，调用它
                    namespace_backup = {'input_data': input_data}
                    exec(code, namespace_backup)
                    if 'main' in namespace_backup and callable(namespace_backup['main']):
                        namespace_backup['main']()

                    # 恢复stdout并获取输出
                    sys.stdout = old_stdout
                    output = captured_output.getvalue().strip()
                    return output if output else str(e)
                except Exception:
                    raise e
        else:
            # 原有的简单代码执行逻辑（已经过process_solution_code处理）
            # 将代码包装成函数
            func_code = "def solve_function(input_data):\n" + '\n'.join(['    ' + line for line in code.split('\n')])

            try:
                # 执行函数定义
                exec(func_code, namespace)
                # 调用函数获取结果
                result = namespace['solve_function'](input_data)
                return str(result) if result is not None else ""
            except Exception as e:
                # 如果执行失败，尝试直接执行原始代码（不转换print）
                try:
                    # 恢复print语句的原始代码
                    original_code = self.restore_print_statements(code)
                    # 捕获print输出
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = io.StringIO()

                    # 执行原始代码
                    exec(original_code, {'input_data': input_data})

                    # 恢复stdout并获取输出
                    sys.stdout = old_stdout
                    output = captured_output.getvalue().strip()
                    return output
                except Exception:
                    raise e
    
    def restore_print_statements(self, code: str) -> str:
        """将return语句恢复为print语句"""
        lines = code.split('\n')
        restored_lines = []

        for line in lines:
            stripped_line = line.strip()
            # 查找return语句并转换回print
            if stripped_line.startswith('return '):
                # 提取return后的内容
                content = stripped_line[7:]  # 去掉'return '
                # 保持原有的缩进
                indent = len(line) - len(line.lstrip())
                restored_lines.append(' ' * indent + f'print({content})')
            else:
                restored_lines.append(line)

        return '\n'.join(restored_lines)
