#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码编辑器组件
功能：提供带有基本编辑功能和语法高亮的代码编辑窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from .SyntaxHighlighter import SyntaxHighlighter
from .auto_completion import AutoCompletion
import re

# 添加DeepSeek相关导入
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from deepseek_api.deepseek_dialog import DeepSeekDialog, ApiKeyDialog
from deepseek_api.api_key_manager import ApiKeyManager
from deepseek_api.prompt_template import generate_test_data_prompt

from .func.deBug import debug
from .func.deepseek_ui import DeepSeekUI
from .func.editor_event_handler import EditorEventHandler


class CodeEditor:
    """代码编辑器类"""

    def __init__(self, parent, title: str = "代码编辑器",
                 initial_code: str = "",
                 template_code: str = "",
                 on_save: Optional[Callable[[str], None]] = None,
                 width: int = 700, height: int = 600,
                 language: str = "python"):
        """
        初始化代码编辑器

        Args:
            parent: 父窗口
            title: 编辑器窗口标题
            initial_code: 初始代码内容
            template_code: 模板代码（当initial_code为空时使用）
            on_save: 保存回调函数
            width: 窗口宽度
            height: 窗口高度
            language: 编程语言类型
        """
        self.parent = parent
        self.title = title
        self.initial_code = initial_code
        self.template_code = template_code
        self.on_save = on_save
        self.width = width
        self.height = height
        self.language = language

        self.deepseek_ui = DeepSeekUI(parent)
        
        # 初始化自动补全实例（稍后在create_text_area中设置）
        self.auto_completion = None
        self.saved_code = self.initial_code  # 初始化保存代码，默认为初始代码

        self.event_handler = None

    def show(self) -> str:
        """显示编辑器窗口并返回编辑后的代码"""
        self.create_editor_window()
        self.parent.wait_window(self.editor_window)
        return self.saved_code

    def create_editor_window(self):
        """创建编辑器窗口"""
        self.editor_window = tk.Toplevel(self.parent)
        self.editor_window.title(self.title)
        self.editor_window.geometry(f"{self.width}x{self.height}")
        self.editor_window.transient(self.parent.winfo_toplevel())
        self.editor_window.grab_set()

        # 创建主框架
        main_frame = ttk.Frame(self.editor_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建文本编辑区域
        self.create_text_area(main_frame)

        # 创建按钮区域
        self.create_button_area(main_frame)

        # 初始化代码内容
        self.initialize_code_content()

        # 设置焦点到文本框
        self.code_text.focus_set()

    def create_embedded_editor(self, parent):
        """创建嵌入式编辑器（不是弹窗模式）"""
        # 创建文本编辑区域
        self.create_text_area(parent)

        # 绑定事件
        self.bind_editor_events()

        # 初始化语法高亮器
        if not self.highlighter:
            self.highlighter = SyntaxHighlighter(self.code_text, self.language)

        # 初始化代码内容
        self.initialize_code_content()

        # 设置焦点到文本框
        self.code_text.focus_set()

    def create_text_area(self, parent):
        """创建文本编辑区域"""
        debug("开始创建文本编辑区域", level=2)
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
    
        # 代码文本框
        self.code_text = tk.Text(text_frame,
                                 wrap=tk.NONE,
                                 font=("Consolas", 11),
                                 insertwidth=2,
                                 selectbackground="#316AC5",
                                 selectforeground="white",
                                 bg="#FFFFFF",
                                 fg="#000000",
                                 insertbackground="#000000",
                                 undo=True,  # 启用撤销功能
                                 maxundo=50)  # 设置最大撤销次数
        debug("文本框创建完成", level=2)
        # 修正：使用 self.code_text 而不是 self.text_area
        self.event_handler = EditorEventHandler(self.code_text)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.code_text.xview)
        self.code_text.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # 创建语法高亮器
        try:
            self.highlighter = SyntaxHighlighter(self.code_text, self.language)
            debug(f"语法高亮器创建成功，语言: {self.language}", level=2)
        except Exception as e:
            debug(f"语法高亮器创建失败: {e}", level=1)
            self.highlighter = None
        
        # 初始化自动补全功能
        try:
            self.auto_completion = AutoCompletion(self.code_text)
            debug("自动补全功能初始化成功", level=2)
            # 关键：让事件处理器能检测到自动补全状态
            self.code_text.autocomplete = self.auto_completion
        except Exception as e:
            debug(f"自动补全功能初始化失败: {e}", level=1)
            self.auto_completion = None

        # 绑定编辑功能事件
        self.bind_editor_events()
        debug("[DEBUG] 文本编辑区域创建完成", level=2)

    def bind_editor_events(self):
        debug("开始绑定编辑器事件", level=2)
    
        # Tab键处理
        self.code_text.bind("<Tab>", self.event_handler.handle_tab)
        debug("Tab键事件绑定完成", level=2)
    
        # Enter键处理  
        self.code_text.bind("<Return>", self.event_handler.handle_return)
        debug("Enter键事件绑定完成", level=2)
    
        # Ctrl+/ 注释切换
        self.code_text.bind("<Control-slash>", self.event_handler.toggle_comment)
    
        # Shift+Tab 减少缩进
        self.code_text.bind("<Shift-Tab>", self.event_handler.handle_shift_tab)
    
        # 退格键智能处理
        self.code_text.bind("<BackSpace>", self.event_handler.handle_backspace)
        
        # 添加符号配对功能的事件绑定
        if self.auto_completion:
            # 符号输入处理（括号、引号等自动配对）
            self.code_text.bind('<KeyPress>', self.auto_completion.handle_symbol_input)
            # 退格键在符号配对中的特殊处理
            self.code_text.bind('<BackSpace>', lambda e: self.auto_completion.handle_backspace_in_pair(e) or self.event_handler.handle_backspace(e))
    
        # 撤销和重做
        self.code_text.bind("<Control-z>", self.event_handler.handle_undo)
        self.code_text.bind("<Control-y>", self.event_handler.handle_redo)
    
        # Home和End键智能处理
        self.code_text.bind("<Home>", self.event_handler.handle_home)
        self.code_text.bind("<End>", self.event_handler.handle_end)
    
        # 保持原有的其他事件绑定
        self.code_text.bind("<Control-s>", lambda e: self.save_code())
        self.code_text.bind("<<Modified>>", self.on_text_change)
        self.code_text.bind("<Button-3>", self.on_paste)
        self.code_text.bind("<MouseWheel>", self.on_scroll)
        self.code_text.bind("<KeyRelease>", self.on_key_release)
    
        debug("所有编辑器事件绑定完成", level=2)

    def on_text_change(self, event=None):
        """文本内容变化时的处理（优化版本）"""
        debug(f"文本变化事件触发，event: {event}", level=2)
        # 触发语法高亮
        if hasattr(self, 'highlighter') and self.highlighter:
            try:
                self.highlighter.highlight_visible_area()
                debug("语法高亮更新成功", level=2)
            except Exception as e:
                debug(f"语法高亮更新失败: {e}", level=1)
        else:
            debug("语法高亮器不存在或为None", level=0)

    def on_paste(self, event=None):
        """处理粘贴事件（优化版本）"""
        if self.highlighter:
            # 粘贴后延迟触发防抖高亮
            self.code_text.after(100, self.highlighter.highlight_syntax_debounced)
        return None

    def on_scroll(self, event=None):
        """滚动时触发可见区域高亮"""
        if self.highlighter:
            # 延迟触发以避免滚动时频繁更新
            self.code_text.after(200, self.highlighter.highlight_visible_area)

    def on_key_release(self, event):
        """按键释放事件处理"""
        debug(f"按键释放事件: {event.keysym}, char: '{event.char}'", level=2)
        
        # 如果自动补全窗口开启，某些按键应该被补全窗口处理
        if self.auto_completion and self.auto_completion.completion_window:
            debug("自动补全窗口已开启，处理导航", level=2)
            if event.keysym in ['Up', 'Down']:
                # 上下键导航补全列表
                self.auto_completion.handle_completion_navigation(event)
                return "break"
            elif event.keysym in ['Return', 'Tab']:
                # 回车或Tab接受补全
                self.auto_completion.accept_completion()
                return "break"
            elif event.keysym == 'Escape':
                # Escape隐藏补全窗口
                self.auto_completion.hide_completion()
                return "break"
            elif event.keysym in ['Left', 'Right']:
                # 左右键隐藏补全窗口
                self.auto_completion.hide_completion()

        # 处理自动补全触发
        if event.char and event.char.isprintable():
            debug(f"可打印字符输入: '{event.char}'，触发自动补全", level=2)
            # 先处理文本变化，再显示补全
            self.on_text_change(event)
            if self.auto_completion:
                try:
                    self.auto_completion.show_completion()
                    debug("自动补全显示成功", level=2)
                except Exception as e:
                    debug(f"自动补全显示失败: {e}", level=1)
            else:
                debug("自动补全实例为None", level=0)
            return

        # 对于其他按键，处理文本变化
        self.on_text_change(event)

    def create_button_area(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存 (Ctrl+S)", command=self.save_code)
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel_edit)
        cancel_btn.pack(side=tk.RIGHT)

        # 问问AI按钮
        ai_btn = ttk.Button(button_frame, text="问问AI", command=self.ask_ai_for_test_data)
        ai_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 重置按钮
        reset_btn = ttk.Button(button_frame, text="重置模板", command=self.reset_template)
        reset_btn.pack(side=tk.LEFT)

    def initialize_code_content(self):
        """初始化代码内容"""
        if self.initial_code.strip():
            # 如果有初始代码，使用初始代码
            self.code_text.insert(1.0, self.initial_code)
        elif self.template_code.strip():
            # 如果没有初始代码但有模板，使用模板
            self.code_text.insert(1.0, self.template_code)

        # 执行语法高亮
        if self.highlighter:
            self.highlighter.highlight_syntax()

        # 设置文本颜色
        self.code_text.config(foreground="black")

    def reset_template(self):
        """重置为模板代码"""
        if self.template_code.strip():
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, self.template_code)
            # 触发语法高亮
            self.on_text_change()

    def save_code(self):
        """保存代码并关闭编辑器"""
        if self.code_text:
            self.saved_code = self.code_text.get(1.0, tk.END + "-1c")

            # 如果有保存回调函数，调用它
            if self.on_save:
                self.on_save(self.saved_code)

            # 关闭编辑器窗口
            if self.editor_window:
                self.editor_window.destroy()

    def cancel_edit(self):
        """取消编辑并关闭编辑器"""
        self.saved_code = self.initial_code

        if self.editor_window:
            self.editor_window.destroy()

    def get_code(self) -> str:
        """获取当前代码内容"""
        if self.code_text:
            return self.code_text.get(1.0, tk.END + "-1c")
        return self.saved_code

    def set_code(self, code: str):
        """设置代码内容"""
        if self.code_text:
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, code)
            # 触发语法高亮
            self.on_text_change()

    def ask_ai_for_test_data(self):
        """调用AI生成测试数据"""
        try:
            # 获取API密钥
            api_key = self.deepseek_ui.get_deepseek_api_key()
            if not api_key:
                return

            # 获取题目描述
            problem_description = self.deepseek_ui.get_problem_description()
            if not problem_description:
                return

            # 使用测试数据生成提示词模板
            from deepseek_api.prompt_template import generate_test_data_prompt
            prompt = generate_test_data_prompt(problem_description)

            # 创建DeepSeek对话框
            from deepseek_api.deepseek_dialog import DeepSeekDialog
            dialog = DeepSeekDialog(self.editor_window or self.parent, api_key, prompt, "")
            dialog.start_generation()  # 启动代码生成

        except Exception as e:
            messagebox.showerror("错误", f"调用DeepSeek时出错：{str(e)}")

    def get_deepseek_api_key(self) -> str:
        """获取DeepSeek API密钥"""
        # 使用API密钥管理器
        api_key = ApiKeyManager.get_api_key()
        if api_key:
            return api_key

        # 如果没有保存的密钥，弹出输入对话框
        dialog = ApiKeyDialog(self.editor_window or self.parent)
        api_key = dialog.show()

        return api_key

    def get_problem_description(self) -> str:
        """获取题目描述"""
        # 创建题目描述输入对话框
        dialog = tk.Toplevel(self.editor_window or self.parent)
        dialog.title("输入题目描述")
        dialog.geometry("600x400")
        dialog.transient(self.editor_window or self.parent)
        dialog.grab_set()

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 说明标签
        info_label = ttk.Label(main_frame, text="请输入题目描述，AI将根据此描述生成测试数据：")
        info_label.pack(pady=(0, 10))

        # 文本输入框 - 限制高度
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10), height=12)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.focus_set()

        # 按钮框架 - 确保固定在底部
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        result = {"description": ""}

        def on_confirm():
            result["description"] = text_widget.get(1.0, tk.END).strip()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # 确认和取消按钮
        ttk.Button(button_frame, text="确认", command=on_confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

        # 等待对话框关闭
        dialog.wait_window()

        return result["description"]


# 便捷函数
def show_code_editor(parent, title: str = "代码编辑器",
                     initial_code: str = "",
                     template_code: str = "",
                     width: int = 700, height: int = 600) -> str:
    """显示代码编辑器的便捷函数

    Args:
        parent: 父窗口
        title: 编辑器标题
        initial_code: 初始代码
        template_code: 模板代码
        width: 窗口宽度
        height: 窗口高度

    Returns:
        编辑后的代码
    """
    editor = CodeEditor(parent, title, initial_code, template_code, width=width, height=height)
    return editor.show()
