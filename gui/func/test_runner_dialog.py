#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行对话框
重构后的主控制类，只负责测试窗口的主逻辑控制
"""

from tkinter import messagebox
from .test_executor import TestExecutor
from .test_ui_manager import TestUIManager


class TestRunnerDialog:
    """测试运行对话框主控制类"""
    
    def __init__(self, parent=None):
        """
        初始化测试运行对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.example_data = None
        self.test_data_list = None  # 完整的测试数据列表
        self.current_test_index = 0  # 当前测试数据索引
        self.current_code_editor = None  # 保存当前代码编辑器引用
        
        # 初始化功能模块
        self.executor = TestExecutor()
        self.ui_manager = TestUIManager(parent)
    
    def set_example_data(self, example_data):
        """
        设置示例数据
        
        Args:
            example_data (str): 示例数据
        """
        self.example_data = example_data
    
    def set_test_data_list(self, test_data_list, current_index=0):
        """
        设置测试数据列表
        
        Args:
            test_data_list (list): 完整的测试数据列表
            current_index (int): 当前测试数据索引
        """
        self.test_data_list = test_data_list
        self.current_test_index = current_index
        # 同时设置当前的示例数据
        if test_data_list and 0 <= current_index < len(test_data_list):
            self.example_data = test_data_list[current_index]
    
    def show_input_dialog(self):
        """
        显示输入对话框
        
        Returns:
            str: 用户输入的测试数据，如果取消则返回None
        """
        dialog, input_text, result_data = self.ui_manager.create_input_dialog(self.example_data)
        
        # 等待对话框关闭
        dialog.wait_window()
        
        if result_data['cancelled']:
            return None
        
        # 如果用户手动输入了数据，清除测试数据列表（因为不再使用预设数据）
        if result_data['input'] != self.example_data:
            self.test_data_list = None
            self.current_test_index = 0
        
        return result_data['input']
    
    def show_result_dialog(self, test_input, result):
        """
        显示运行结果对话框
        
        Args:
            test_input (str): 输入的测试数据
            result (str): 运行结果
        """
        # 根据是否有测试数据列表来决定显示哪些按钮
        has_test_list = self.test_data_list is not None and len(self.test_data_list) > 1
        
        self.ui_manager.create_result_dialog(
            test_input, 
            result, 
            self._on_re_input_data,
            self._on_next_test_data if has_test_list else None
        )
    
    def _on_re_input_data(self):
        """
        重新输入数据的回调函数
        重新打开测试数据输入窗口
        """
        if self.current_code_editor:
            self.run_test(self.current_code_editor)
    
    def _on_next_test_data(self):
        """
        使用下一个测试数据的回调函数
        自动切换到下一个测试数据并运行测试
        """
        if self.current_code_editor and self.test_data_list:
            # 切换到下一个测试数据
            self.current_test_index = (self.current_test_index + 1) % len(self.test_data_list)
            self.example_data = self.test_data_list[self.current_test_index]
            
            # 直接使用下一个测试数据运行测试
            self._run_test_with_data(self.current_code_editor, self.example_data)
    
    def _run_test_with_data(self, code_editor, test_input):
        """
        使用指定的测试数据运行测试
        
        Args:
            code_editor: 代码编辑器实例
            test_input: 测试输入数据
        """
        try:
            # 获取代码
            code = code_editor.get_code()
            
            # 验证代码
            is_valid, error_msg = self.executor.validate_code(code)
            if not is_valid:
                messagebox.showwarning("代码验证失败", error_msg)
                return
            
            # 执行代码
            result = self.executor.execute_code(code, test_input)
            
            # 显示结果
            self.show_result_dialog(test_input, result)
            
        except Exception as e:
            messagebox.showerror("运行错误", f"测试运行出错：\n{str(e)}")
    
    def run_test(self, code_editor):
        """
        运行测试的主方法
        
        Args:
            code_editor: 代码编辑器实例
        """
        try:
            # 保存代码编辑器引用，用于连续测试
            self.current_code_editor = code_editor
            
            # 获取用户输入的测试数据
            test_input = self.show_input_dialog()
            
            if test_input is None:
                return
            
            # 使用获取的测试数据运行测试
            self._run_test_with_data(code_editor, test_input)
            
        except Exception as e:
            messagebox.showerror("运行错误", f"测试运行出错：\n{str(e)}")
