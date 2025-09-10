#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试执行器核心类
负责代码执行逻辑，与UI界面分离
"""

import io
import sys


class TestExecutor:
    """测试执行器核心类，负责代码执行逻辑"""
    
    def __init__(self):
        """初始化测试执行器"""
        pass
    
    def execute_code(self, code, test_input):
        """
        执行代码并返回结果
        
        Args:
            code (str): 要执行的代码
            test_input (str): 测试输入数据
            
        Returns:
            str: 执行结果
        """
        try:
            # 准备执行环境
            exec_globals = {'input_data': test_input}
            exec_locals = {}
            
            # 重定向stdout来捕获print输出
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            result = None
            
            try:
                # 执行代码
                exec(code, exec_globals, exec_locals)
                
                # 获取print输出
                print_output = captured_output.getvalue().strip()
                
                # 检查是否有main函数并获取其返回值
                if 'def main(' in code:
                    result = self._execute_main_function(exec_locals, print_output)
                else:
                    # 没有main函数，使用print输出或其他结果
                    result = self._get_execution_result(exec_locals, print_output)
                        
            finally:
                sys.stdout = old_stdout
            
            return result
            
        except Exception as e:
            return f"代码执行出错：\n{str(e)}"
    
    def _execute_main_function(self, exec_locals, print_output):
        """
        执行main函数并获取结果
        
        Args:
            exec_locals (dict): 执行环境的局部变量
            print_output (str): print输出内容
            
        Returns:
            str: 执行结果
        """
        if 'main' in exec_locals and callable(exec_locals['main']):
            try:
                main_result = exec_locals['main']()
                if main_result is not None:
                    return str(main_result)
                elif print_output:
                    return print_output
                else:
                    return "main函数执行完成，无返回值"
            except Exception as main_e:
                return f"main函数执行错误: {str(main_e)}"
        else:
            return "未找到main函数或main函数不可调用"
    
    def _get_execution_result(self, exec_locals, print_output):
        """
        获取代码执行结果（非main函数情况）
        
        Args:
            exec_locals (dict): 执行环境的局部变量
            print_output (str): print输出内容
            
        Returns:
            str: 执行结果
        """
        if print_output:
            return print_output
        else:
            # 尝试获取最后的表达式结果或变量
            possible_results = []
            for var_name, var_value in exec_locals.items():
                if not var_name.startswith('__') and not callable(var_value):
                    possible_results.append(f"{var_name}: {var_value}")
            
            if possible_results:
                return "\n".join(possible_results)
            else:
                return "代码执行完成，无输出结果"
    
    def validate_code(self, code):
        """
        验证代码是否有效
        
        Args:
            code (str): 要验证的代码
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not code.strip():
            return False, "代码不能为空"
        
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        except Exception as e:
            return False, f"代码验证失败: {str(e)}"