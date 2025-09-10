#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解题代码编辑器UI
负责处理解题代码编辑器窗口的创建和管理
"""

import tkinter as tk
from tkinter import ttk
from typing import List
from .test_runner_dialog import TestRunnerDialog


class SolutionEditorUI:
    """解题代码编辑器UI类"""
    def __init__(self, parent_window, solution_executor, deepseek_ui):
        """
        初始化解题代码编辑器UI
        
        Args:
            parent_window: 父窗口
            solution_executor: 解题代码执行器实例
            deepseek_ui: DeepSeek UI实例
        """
        self.parent_window = parent_window
        self.solution_executor = solution_executor
        self.deepseek_ui = deepseek_ui
        self.current_code_editor = None
        self.test_runner = TestRunnerDialog()
        
        # 添加测试数据管理
        self.test_data = []
        self.current_test_index = 0
        self.example_text = None
        self.next_test_btn = None
    
    def show_solution_editor(self, test_data: List[str], output_dir: str, input_files: List[str], 
                           delete_temp_files_var):
        """显示解题代码编辑器"""
        # 保存测试数据
        self.test_data = test_data
        self.current_test_index = 0
        
        # 准备模板代码
        template_code = '''# 解题代码使用说明
# 数据已经通过input_data传入，可以直接使用此变量，数据类型是字符串
# 不使用函数的情况下，print作为返回值，并截断后续的全部代码
# 使用函数的情况下，main作为唯一入口，必须有此函数且有返回值，可以添加其他辅助函数

def main():
    # 在这里继续编写你的解题逻辑
    lines = input_data.strip().split('\\n')
    # lines = input_data.strip()
    
    return None

'''

        # 创建编辑器窗口
        editor_window = tk.Toplevel(self.parent_window)
        editor_window.title("解题代码编辑器")
        editor_window.geometry("900x700")
        editor_window.transient(self.parent_window)
        editor_window.grab_set()

        # 主框架
        main_frame = ttk.Frame(editor_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 示例数据显示
        example_frame = ttk.LabelFrame(main_frame, text=self._get_example_title(), padding="5")
        example_frame.pack(fill=tk.X, pady=(0, 10))

        self.example_text = tk.Text(example_frame, height=6, wrap=tk.WORD, bg="#f0f0f0")
        example_scrollbar = ttk.Scrollbar(example_frame, orient="vertical", command=self.example_text.yview)
        self.example_text.configure(yscrollcommand=example_scrollbar.set)

        self.example_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        example_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 显示当前测试用例
        self._update_example_display()

        # 代码编辑区域框架
        code_frame = ttk.LabelFrame(main_frame, text="解题代码（请根据上面的数据编写处理逻辑）", padding="5")
        code_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 使用我们的代码编辑器组件
        from ..code_editor import CodeEditor

        # 创建代码编辑器实例（嵌入到现有窗口中）
        code_editor = CodeEditor(
            parent=code_frame,
            title="",  # 不需要标题，因为已经在LabelFrame中
            initial_code="",
            template_code=template_code,
            width=0,  # 将使用父容器的大小
            height=0
        )

        # 创建嵌入式编辑器（不是弹窗）
        code_editor.create_embedded_editor(code_frame)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 执行并保存按钮
        execute_btn = ttk.Button(button_frame, text="执行并保存结果",
                                 command=lambda: self.solution_executor.execute_and_save_solution(
                                     code_editor.get_code(), test_data, output_dir, editor_window,
                                     delete_temp_files_var.get()))
        execute_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 问问DeepSeek按钮
        deepseek_btn = ttk.Button(button_frame, text="问问DeepSeek",
                                  command=lambda: self.deepseek_ui.ask_deepseek_with_editor(code_editor,
                                                                            self._get_current_test_data()))
        deepseek_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 设置测试运行器的示例数据
        self._update_test_runner_data()
        
        # 测试运行按钮 - 使用独立的测试运行界面
        test_run_btn = ttk.Button(button_frame, text="测试运行",
                                  command=lambda: self._run_test_with_current_data(code_editor))
        test_run_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 下一个测试数据按钮
        self.next_test_btn = ttk.Button(button_frame, text=self._get_next_button_text(),
                                       command=lambda: self._switch_to_next_test_data(example_frame))
        self.next_test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存编辑器引用，用于DeepSeek功能
        self.deepseek_ui.set_current_code_editor(code_editor)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=editor_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        # 保存编辑器引用，用于DeepSeek功能
        self.current_code_editor = code_editor
        
        # 设置测试运行器的父窗口
        self.test_runner.parent = editor_window
    
    def _get_current_test_data(self):
        """获取当前测试数据"""
        if self.test_data and 0 <= self.current_test_index < len(self.test_data):
            return self.test_data[self.current_test_index]
        return ""
    
    def _get_example_title(self):
        """获取示例数据标题"""
        if not self.test_data:
            return "示例数据"
        total = len(self.test_data)
        current = self.current_test_index + 1
        return f"示例数据（第{current}个测试用例，共{total}个）"
    
    def _get_next_button_text(self):
        """获取下一个按钮的文本"""
        if not self.test_data:
            return "下一个测试数据"
        total = len(self.test_data)
        next_index = (self.current_test_index + 1) % total
        next_num = next_index + 1
        return f"下一个测试数据({next_num}/{total})"
    
    def _update_example_display(self):
        """更新示例数据显示"""
        if self.example_text:
            self.example_text.config(state=tk.NORMAL)
            self.example_text.delete(1.0, tk.END)
            current_data = self._get_current_test_data()
            if current_data:
                self.example_text.insert(tk.END, current_data)
            self.example_text.config(state=tk.DISABLED)
    
    def _update_test_runner_data(self):
        """更新测试运行器的示例数据"""
        current_data = self._get_current_test_data()
        if current_data:
            self.test_runner.set_example_data(current_data)
    
    def _switch_to_next_test_data(self, example_frame):
        """切换到下一个测试数据"""
        if not self.test_data:
            return
        
        # 循环切换到下一个测试数据
        self.current_test_index = (self.current_test_index + 1) % len(self.test_data)
        
        # 更新示例数据框架标题
        example_frame.config(text=self._get_example_title())
        
        # 更新示例数据显示
        self._update_example_display()
        
        # 更新测试运行器数据
        self._update_test_runner_data()
        
        # 更新按钮文本
        if self.next_test_btn:
            self.next_test_btn.config(text=self._get_next_button_text())
    
    def _run_test_with_current_data(self, code_editor):
        """使用当前测试数据运行测试"""
        # 设置测试运行器的测试数据列表和当前索引
        self.test_runner.set_test_data_list(self.test_data, self.current_test_index)
        # 运行测试
        self.test_runner.run_test(code_editor)
