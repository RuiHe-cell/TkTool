#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件管理类
负责测试运行对话框的界面创建和管理
"""

import tkinter as tk
from tkinter import ttk, messagebox


class TestUIManager:
    """UI组件管理类，负责界面创建和管理"""
    
    def __init__(self, parent=None):
        """
        初始化UI管理器
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.input_dialog = None
        self.result_dialog = None
    
    def create_input_dialog(self, example_data=None):
        """
        创建输入对话框
        
        Args:
            example_data (str): 示例数据
            
        Returns:
            tuple: (dialog, input_text, result_data)
        """
        result_data = {'input': None, 'cancelled': True}
        
        # 创建输入对话框
        input_dialog = tk.Toplevel(self.parent)
        input_dialog.title("测试数据输入")
        input_dialog.geometry("600x400")
        input_dialog.resizable(True, True)
        
        if self.parent:
            input_dialog.transient(self.parent)
            # 居中显示
            input_dialog.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + 50,
                self.parent.winfo_rooty() + 50
            ))
        
        input_dialog.grab_set()
        
        # 创建主要UI组件
        input_text = self._create_input_ui_components(input_dialog, example_data, result_data)
        
        return input_dialog, input_text, result_data
    
    def _create_input_ui_components(self, dialog, example_data, result_data):
        """
        创建输入对话框的UI组件
        
        Args:
            dialog: 对话框窗口
            example_data (str): 示例数据
            result_data (dict): 结果数据字典
            
        Returns:
            tk.Text: 输入文本框
        """
        # 主框架
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明标签
        label = ttk.Label(main_frame, text="请输入测试数据（支持多行输入）:", font=('', 10))
        label.pack(anchor=tk.W, pady=(0, 20))
        
        # 文本输入框框架
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 文本输入框
        input_text = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 11),
            bg='white',
            relief='solid',
            borderwidth=1,
            height=15
        )
        
        # 滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=input_text.yview)
        input_text.configure(yscrollcommand=scrollbar.set)
        
        input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建按钮
        self._create_input_buttons(main_frame, dialog, input_text, example_data, result_data)
        
        # 设置焦点和快捷键
        input_text.focus_set()
        dialog.bind('<Control-Return>', lambda e: self._on_input_ok(input_text, result_data, dialog))
        dialog.bind('<Escape>', lambda e: self._on_input_cancel(result_data, dialog))
        
        return input_text
    
    def _create_input_buttons(self, parent_frame, dialog, input_text, example_data, result_data):
        """
        创建输入对话框的按钮
        
        Args:
            parent_frame: 父框架
            dialog: 对话框窗口
            input_text: 输入文本框
            example_data (str): 示例数据
            result_data (dict): 结果数据字典
        """
        # 按钮框架
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 使用示例数据按钮（只有当有示例数据时才显示）
        if example_data:
            example_btn = ttk.Button(
                button_frame, 
                text="使用示例数据并执行", 
                command=lambda: self._on_use_example(example_data, result_data, dialog),
                width=18
            )
            example_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        # 确定按钮
        ok_btn = ttk.Button(
            button_frame, 
            text="运行测试", 
            command=lambda: self._on_input_ok(input_text, result_data, dialog),
            width=12
        )
        ok_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, 
            text="取消", 
            command=lambda: self._on_input_cancel(result_data, dialog),
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT)
    
    def _on_input_ok(self, input_text, result_data, dialog):
        """处理确定按钮点击"""
        result_data['input'] = input_text.get("1.0", tk.END).strip()
        result_data['cancelled'] = False
        dialog.destroy()
    
    def _on_input_cancel(self, result_data, dialog):
        """处理取消按钮点击"""
        result_data['cancelled'] = True
        dialog.destroy()
    
    def _on_use_example(self, example_data, result_data, dialog):
        """处理使用示例数据按钮点击"""
        if example_data:
            result_data['input'] = example_data
            result_data['cancelled'] = False
            dialog.destroy()
        else:
            messagebox.showwarning("警告", "没有可用的示例数据！")
    
    def create_result_dialog(self, test_input, result, on_re_input_callback=None, on_next_test_callback=None):
        """
        创建结果显示对话框
        
        Args:
            test_input (str): 输入的测试数据
            result (str): 运行结果
            on_re_input_callback (callable): 重新输入的回调函数
            on_next_test_callback (callable): 使用下一个测试数据的回调函数
        """
        # 创建结果显示对话框
        result_dialog = tk.Toplevel(self.parent)
        result_dialog.title("测试运行结果")
        result_dialog.geometry("700x500")
        result_dialog.resizable(True, True)
        
        if self.parent:
            result_dialog.transient(self.parent)
            # 居中显示
            result_dialog.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + 30,
                self.parent.winfo_rooty() + 30
            ))
        
        # 创建结果显示UI组件
        self._create_result_ui_components(result_dialog, test_input, result, on_re_input_callback, on_next_test_callback)
        
        return result_dialog
    
    def _create_result_ui_components(self, dialog, test_input, result, on_re_input_callback=None, on_next_test_callback=None):
        """
        创建结果对话框的UI组件
        
        Args:
            dialog: 对话框窗口
            test_input (str): 输入数据
            result (str): 运行结果
            on_re_input_callback (callable): 重新输入的回调函数
            on_next_test_callback (callable): 使用下一个测试数据的回调函数
        """
        # 结果显示框架
        result_frame = ttk.Frame(dialog, padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入数据显示
        self._create_input_display(result_frame, test_input)
        
        # 运行结果显示
        self._create_result_display(result_frame, result)
        
        # 按钮
        self._create_result_buttons(result_frame, dialog, result, on_re_input_callback, on_next_test_callback)
    
    def _create_input_display(self, parent_frame, test_input):
        """创建输入数据显示区域"""
        input_label = ttk.Label(parent_frame, text="输入数据:", font=('', 10, 'bold'))
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        input_frame = ttk.Frame(parent_frame)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_display = tk.Text(
            input_frame, 
            height=6, 
            wrap=tk.WORD, 
            bg="#f8f9fa", 
            font=('Consolas', 10),
            relief='solid',
            borderwidth=1,
            state=tk.NORMAL,
        )
        
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=input_display.yview)
        input_display.configure(yscrollcommand=input_scrollbar.set)
        
        input_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        input_display.insert(tk.END, test_input)
        input_display.config(state=tk.DISABLED)
    
    def _create_result_display(self, parent_frame, result):
        """创建结果显示区域"""
        result_label = ttk.Label(parent_frame, text="运行结果:", font=('', 10, 'bold'))
        result_label.pack(anchor=tk.W, pady=(0, 5))
        
        result_text_frame = ttk.Frame(parent_frame)
        result_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        result_display = tk.Text(
            result_text_frame, 
            height=10,
            wrap=tk.WORD, 
            bg="#f0f8ff", 
            font=('Consolas', 10),
            relief='solid',
            borderwidth=1,
            state=tk.NORMAL
        )
        
        result_scrollbar = ttk.Scrollbar(result_text_frame, orient="vertical", command=result_display.yview)
        result_display.configure(yscrollcommand=result_scrollbar.set)
        
        result_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        result_display.insert(tk.END, str(result))
        result_display.config(state=tk.DISABLED)
    
    def _create_result_buttons(self, parent_frame, dialog, result, on_re_input_callback=None, on_next_test_callback=None):
        """创建结果对话框的按钮"""
        # 按钮框架
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill=tk.X)
        
        # 关闭按钮
        close_btn = ttk.Button(
            button_frame, 
            text="关闭", 
            command=dialog.destroy,
            width=12
        )
        close_btn.pack(side=tk.RIGHT)
        
        # 使用下一个测试数据按钮（只有当有测试数据列表时才显示）
        if on_next_test_callback:
            def on_next_test():
                dialog.destroy()  # 先关闭当前结果窗口
                on_next_test_callback()  # 然后调用回调函数
            
            next_test_btn = ttk.Button(
                button_frame, 
                text="使用下一个测试数据", 
                command=on_next_test,
                width=18
            )
            next_test_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        # 重新输入按钮
        if on_re_input_callback:
            def on_re_input():
                dialog.destroy()  # 先关闭当前结果窗口
                on_re_input_callback()  # 然后调用回调函数
            
            re_input_btn = ttk.Button(
                button_frame, 
                text="重新输入", 
                command=on_re_input,
                width=12
            )
            re_input_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        # 复制结果按钮
        def copy_result():
            dialog.clipboard_clear()
            dialog.clipboard_append(str(result))
            messagebox.showinfo("提示", "结果已复制到剪贴板")
        
        copy_btn = ttk.Button(
            button_frame, 
            text="复制结果", 
            command=copy_result,
            width=12
        )
        copy_btn.pack(side=tk.RIGHT, padx=(0, 8))
        
        # 绑定快捷键
        dialog.bind('<Escape>', lambda e: dialog.destroy())