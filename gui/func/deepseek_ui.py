#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek UI模块
功能：处理DeepSeek相关的UI操作，包括API调用、问题描述输入等
"""

import tkinter as tk
from tkinter import ttk, messagebox
from deepseek_api.deepseek_dialog import DeepSeekDialog, ApiKeyDialog
from deepseek_api.api_key_manager import ApiKeyManager
from .deBug import debug


class DeepSeekUI:
    """DeepSeek UI类"""
    
    def __init__(self, parent_window):
        """
        初始化DeepSeek UI
        
        Args:
            parent_window: 父窗口
        """
        self.parent_window = parent_window
        self.current_code_editor = None
    
    def set_current_code_editor(self, code_editor):
        """设置当前代码编辑器引用"""
        self.current_code_editor = code_editor
    
    def ask_deepseek_with_editor(self, code_editor, example_data: str):
        """使用代码编辑器的DeepSeek功能"""
        try:
            current_code = code_editor.get_code()

            # 获取API密钥
            api_key = self.get_deepseek_api_key()
            if not api_key:
                return

            # 获取问题描述
            problem_description = self.get_problem_description()
            if not problem_description:
                return

            # 创建DeepSeek对话框 - 传递正确的4个参数
            dialog = DeepSeekDialog(self.parent_window, api_key, problem_description, example_data)
            dialog.start_generation()  # 启动代码生成

            # 注意：DeepSeekDialog 不返回结果，它是一个独立的对话窗口

        except ImportError as e:
            messagebox.showerror("导入错误",
                                 f"DeepSeek功能不可用，缺少模块：{str(e)}\n\n请检查以下模块是否已安装：\n- deepseek_dialog\n- 相关依赖库")
        except ModuleNotFoundError as e:
            messagebox.showerror("模块未找到",
                                 f"找不到模块：{str(e)}\n\n请确保以下文件存在：\n- gui/deepseek_dialog.py\n- deepseek_api/deepseek_dialog.py")
        except Exception as e:
            messagebox.showerror("错误", f"调用DeepSeek时出错：{str(e)}")
    
    def ask_deepseek(self, code_text, test_data: str):
        """调用DeepSeek生成代码"""
        debug("ask_deepseek() 被调用")
        try:
            # 获取API密钥
            api_key = self.get_deepseek_api_key()
            if not api_key:
                debug(" 未获取到API密钥，退出")
                return

            # 获取题目描述
            problem_description = self.get_problem_description()
            if not problem_description:
                debug(" 未获取到题目描述，退出")
                return

            debug(" 创建DeepSeekDialog实例")
            # 创建DeepSeek对话窗口
            dialog = DeepSeekDialog(
                parent=self.parent_window,
                api_key=api_key,
                problem_description=problem_description,
                test_data=test_data
            )
            debug(" 调用dialog.start_generation()")
            dialog.start_generation()

        except Exception as e:
            debug(f" ask_deepseek出错: {str(e)}")
            messagebox.showerror("错误", f"调用DeepSeek时出错：{str(e)}")
    
    def get_deepseek_api_key(self) -> str:
        """获取DeepSeek API密钥"""
        # 使用新的API密钥管理器
        api_key = ApiKeyManager.get_api_key()
        if api_key:
            return api_key

        # 如果没有保存的密钥，弹出输入对话框
        dialog = ApiKeyDialog(self.parent_window)
        api_key = dialog.show()

        return api_key
    
    def get_problem_description(self) -> str:
        """获取题目描述"""
        # 创建题目描述输入对话框
        dialog = tk.Toplevel(self.parent_window)
        dialog.title("输入题目描述")
        dialog.geometry("600x600")
        dialog.transient(self.parent_window)
        dialog.grab_set()

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 说明标签
        info_label = ttk.Label(main_frame, text="请输入题目描述，这将帮助DeepSeek更好地理解问题：")
        info_label.pack(pady=(0, 10))

        # 文本输入框
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 默认提示文本
        placeholder = "例如：\n给定一个整数数组和一个目标值，找出数组中两个数的和等于目标值的所有组合。\n\n输入格式：\n第一行包含数组长度n和目标值target\n第二行包含n个整数\n\n输出格式：\n输出所有满足条件的数对"
        text_widget.insert(tk.END, placeholder)
        text_widget.focus()

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        result = {'description': None}

        def ok_clicked():
            description = text_widget.get("1.0", tk.END).strip()
            if not description or description == placeholder.strip():
                messagebox.showerror("错误", "请输入题目描述")
                return
            result['description'] = description
            dialog.destroy()

        def cancel_clicked():
            result['description'] = None
            dialog.destroy()

        # 确定按钮
        ok_btn = ttk.Button(button_frame, text="确定", command=ok_clicked)
        ok_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=cancel_clicked)
        cancel_btn.pack(side=tk.RIGHT)

        # 绑定快捷键
        dialog.bind('<Control-Return>', lambda e: ok_clicked())
        dialog.bind('<Escape>', lambda e: cancel_clicked())

        # 等待对话框关闭
        dialog.wait_window()

        return result['description']
