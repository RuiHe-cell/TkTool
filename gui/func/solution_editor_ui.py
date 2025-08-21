#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解题代码编辑器UI
负责处理解题代码编辑器窗口的创建和管理
"""

import tkinter as tk
from tkinter import ttk
from typing import List


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
    
    def show_solution_editor(self, test_data: List[str], output_dir: str, input_files: List[str], 
                           delete_temp_files_var):
        """显示解题代码编辑器"""
        # 准备模板代码
        template_code = '''# 解题代码模板
# 输入数据已经通过input_data变量传入
# 请根据下面的示例数据编写处理逻辑
# 最后的print语句会被转换为return语句

lines = input_data.strip().split('\\n')
# 在这里编写你的解题逻辑

# 示例：
# result = "your_answer"
# print(result)'''

        # 创建一个自定义的编辑器窗口来集成示例数据显示和代码编辑
        editor_window = tk.Toplevel(self.parent_window)
        editor_window.title("解题代码编辑器")
        editor_window.geometry("900x700")
        editor_window.transient(self.parent_window)
        editor_window.grab_set()

        # 主框架
        main_frame = ttk.Frame(editor_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 示例数据显示
        example_frame = ttk.LabelFrame(main_frame, text="示例数据（第一个测试用例）", padding="5")
        example_frame.pack(fill=tk.X, pady=(0, 10))

        example_text = tk.Text(example_frame, height=6, wrap=tk.WORD, bg="#f0f0f0")
        example_scrollbar = ttk.Scrollbar(example_frame, orient="vertical", command=example_text.yview)
        example_text.configure(yscrollcommand=example_scrollbar.set)

        example_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        example_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 显示第一个测试用例
        if test_data:
            example_text.insert(tk.END, test_data[0])
        example_text.config(state=tk.DISABLED)

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
                                                                            test_data[0] if test_data else ""))
        deepseek_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存编辑器引用，用于DeepSeek功能
        self.deepseek_ui.set_current_code_editor(code_editor)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=editor_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        # 保存编辑器引用，用于DeepSeek功能
        self.current_code_editor = code_editor
