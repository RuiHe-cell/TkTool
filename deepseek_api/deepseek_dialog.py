#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 对话窗口
功能：显示DeepSeek返回的代码，支持流式显示和复制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from .deepseek_client import DeepSeekClient
from .prompt_template import generate_coding_prompt
from .api_key_manager import ApiKeyManager
from .code_extractor import clean_and_extract_code


class DeepSeekDialog:
    """DeepSeek对话窗口"""

    def __init__(self, parent, api_key: str, problem_description: str, test_data: str):
        self.parent = parent
        self.api_key = api_key
        self.problem_description = problem_description
        self.test_data = test_data
        self.client = DeepSeekClient(api_key)
        self.generated_code = ""

        self.create_dialog()

    def create_dialog(self):
        """创建对话窗口"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("问问DeepSeek")
        self.dialog.geometry("900x750")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 设置最小窗口大小，确保按钮始终可见
        self.dialog.minsize(800, 650)

        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="正在连接DeepSeek...")
        self.status_label.pack(pady=(0, 10))

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # 创建主要内容区域的PanedWindow来分割两个文本框
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 原始返回结果区域（上半部分）
        raw_frame = ttk.LabelFrame(paned_window, text="DeepSeek原始返回结果（可编辑）", padding="5")
        paned_window.add(raw_frame, weight=1)

        # 创建原始结果文本框和滚动条
        raw_text_frame = ttk.Frame(raw_frame)
        raw_text_frame.pack(fill=tk.BOTH, expand=True)

        self.raw_text = tk.Text(raw_text_frame, wrap=tk.NONE, font=('Consolas', 10),
                                state=tk.DISABLED, bg="#f8f8f8", height=15)

        raw_v_scrollbar = ttk.Scrollbar(raw_text_frame, orient="vertical", command=self.raw_text.yview)
        raw_h_scrollbar = ttk.Scrollbar(raw_text_frame, orient="horizontal", command=self.raw_text.xview)

        self.raw_text.configure(yscrollcommand=raw_v_scrollbar.set, xscrollcommand=raw_h_scrollbar.set)

        self.raw_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        raw_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        raw_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        raw_text_frame.grid_rowconfigure(0, weight=1)
        raw_text_frame.grid_columnconfigure(0, weight=1)

        # 精炼代码区域（下半部分）
        refined_frame = ttk.LabelFrame(paned_window, text="精炼后的代码（只读）", padding="5")
        paned_window.add(refined_frame, weight=1)

        # 创建精炼代码文本框和滚动条
        refined_text_frame = ttk.Frame(refined_frame)
        refined_text_frame.pack(fill=tk.BOTH, expand=True)

        self.refined_text = tk.Text(refined_text_frame, wrap=tk.NONE, font=('Consolas', 10),
                                    state=tk.DISABLED, bg="#f0f8ff", height=15)

        refined_v_scrollbar = ttk.Scrollbar(refined_text_frame, orient="vertical", command=self.refined_text.yview)
        refined_h_scrollbar = ttk.Scrollbar(refined_text_frame, orient="horizontal", command=self.refined_text.xview)

        self.refined_text.configure(yscrollcommand=refined_v_scrollbar.set, xscrollcommand=refined_h_scrollbar.set)

        self.refined_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        refined_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        refined_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        refined_text_frame.grid_rowconfigure(0, weight=1)
        refined_text_frame.grid_columnconfigure(0, weight=1)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 复制精炼代码按钮
        self.copy_btn = ttk.Button(button_frame, text="复制精炼代码",
                                   command=self.copy_refined_code, state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 手动提取按钮
        self.extract_btn = ttk.Button(button_frame, text="手动提取代码",
                                      command=self.manual_extract_code, state=tk.DISABLED)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 重新生成按钮
        self.regenerate_btn = ttk.Button(button_frame, text="重新生成",
                                         command=self.regenerate_code, state=tk.DISABLED)
        self.regenerate_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 关闭按钮
        close_btn = ttk.Button(button_frame, text="关闭", command=self.dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

        # 注意：不在这里自动开始生成代码，由外部调用start_generation()

    def start_generation(self):
        """开始生成代码"""
        print("[DEBUG] start_generation() 被调用")

        # 检查网络连接
        if not self.client.check_network():
            self.status_label.config(text="网络连接失败，请检查网络设置")
            self.progress.stop()
            return

        # 验证API密钥
        self.status_label.config(text="验证API密钥...")
        if not self.client.validate_api_key():
            self.status_label.config(text="API密钥无效，请检查设置")
            self.progress.stop()
            return

        self.progress.start()
        self.status_label.config(text="DeepSeek正在思考中...")

        # 在新线程中生成代码
        thread = threading.Thread(target=self.generate_code_thread)
        thread.daemon = True
        thread.start()
        print("[DEBUG] 代码生成线程已启动")

    def generate_code_thread(self):
        """在后台线程中生成代码"""
        print("[DEBUG] generate_code_thread() 开始执行")
        try:
            prompt = generate_coding_prompt(self.problem_description, self.test_data)
            messages = [
                {"role": "system",
                 "content": "你是一个专业的编程助手，专门帮助用户解决编程问题。请只返回可执行的Python代码，不要包含任何解释。"},
                {"role": "user", "content": prompt}
            ]

            print("[DEBUG] 准备调用DeepSeek API")
            self.generated_code = ""
            chunk_count = 0

            for chunk in self.client.chat_completion_stream(messages):
                if chunk:
                    chunk_count += 1
                    self.generated_code += chunk
                    # 在主线程中更新UI
                    self.dialog.after(0, self.update_code_display, chunk)

            print(f"[DEBUG] API调用完成，共收到 {chunk_count} 个数据块")
            print(f"[DEBUG] 生成的代码长度: {len(self.generated_code)} 字符")

            # 生成完成
            self.dialog.after(0, self.generation_complete)

        except Exception as e:
            print(f"[DEBUG] 代码生成出错: {str(e)}")
            self.dialog.after(0, self.generation_error, str(e))

    def update_code_display(self, chunk: str):
        """更新原始代码显示"""
        self.raw_text.config(state=tk.NORMAL)
        self.raw_text.insert(tk.END, chunk)
        self.raw_text.see(tk.END)
        self.raw_text.config(state=tk.DISABLED)

    def generation_complete(self):
        """生成完成"""
        self.progress.stop()

        # 启用原始文本框的编辑功能
        self.raw_text.config(state=tk.NORMAL)

        # 自动提取和清理代码到精炼文本框
        if self.generated_code:
            self.extract_and_display_refined_code()

        self.status_label.config(text="代码生成完成")
        self.copy_btn.config(state=tk.NORMAL)
        self.extract_btn.config(state=tk.NORMAL)
        self.regenerate_btn.config(state=tk.NORMAL)

    def generation_error(self, error_msg: str):
        """生成错误"""
        self.progress.stop()
        self.status_label.config(text=f"生成失败: {error_msg}")
        self.regenerate_btn.config(state=tk.NORMAL)

    def extract_and_display_refined_code(self):
        """提取并显示精炼代码"""
        # 获取当前原始文本框的内容
        raw_content = self.raw_text.get(1.0, tk.END).strip()

        # 提取和清理代码
        refined_code = clean_and_extract_code(raw_content)

        # 更新精炼代码文本框
        self.refined_text.config(state=tk.NORMAL)
        self.refined_text.delete(1.0, tk.END)
        self.refined_text.insert(1.0, refined_code)
        self.refined_text.config(state=tk.DISABLED)

    def copy_refined_code(self):
        """复制精炼代码到剪贴板"""
        refined_content = self.refined_text.get(1.0, tk.END).strip()
        if refined_content:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(refined_content)
            messagebox.showinfo("提示", "精炼代码已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的精炼代码")

    def manual_extract_code(self):
        """手动提取代码"""
        self.extract_and_display_refined_code()
        messagebox.showinfo("提示", "代码提取完成")

    def regenerate_code(self):
        """重新生成代码"""
        # 清空两个文本框
        self.raw_text.config(state=tk.NORMAL)
        self.raw_text.delete(1.0, tk.END)
        self.raw_text.config(state=tk.DISABLED)

        self.refined_text.config(state=tk.NORMAL)
        self.refined_text.delete(1.0, tk.END)
        self.refined_text.config(state=tk.DISABLED)

        # 禁用按钮
        self.copy_btn.config(state=tk.DISABLED)
        self.extract_btn.config(state=tk.DISABLED)
        self.regenerate_btn.config(state=tk.DISABLED)

        # 重新开始生成
        self.start_generation()


class ApiKeyDialog:
    """API密钥输入对话框"""

    def __init__(self, parent):
        self.parent = parent
        self.api_key = None
        self.dialog = None

    def show(self):
        """显示API密钥输入对话框"""
        # 先尝试从keyring获取已保存的密钥
        saved_key = ApiKeyManager.get_api_key()
        if saved_key:
            return saved_key

        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("输入DeepSeek API密钥")
        self.dialog.geometry("450x340")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))

        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # 说明文本
        info_label = ttk.Label(
            main_frame,
            text="请输入您的DeepSeek API密钥：\n\n您可以在 https://platform.deepseek.com 获取API密钥\n密钥将使用系统密钥环安全存储",
            justify='center'
        )
        info_label.pack(pady=(0, 20))

        # API密钥输入框
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill='x', pady=(0, 20))

        ttk.Label(key_frame, text="API密钥:").pack(anchor='w')
        self.key_entry = ttk.Entry(key_frame, show="*", width=50)
        self.key_entry.pack(fill='x', pady=(5, 0))

        # 显示/隐藏密钥按钮
        self.show_key_var = tk.BooleanVar()
        show_key_cb = ttk.Checkbutton(
            key_frame,
            text="显示密钥",
            variable=self.show_key_var,
            command=self.toggle_key_visibility
        )
        show_key_cb.pack(anchor='w', pady=(5, 0))

        # 保存密钥选项
        self.save_key_var = tk.BooleanVar(value=True)
        save_key_cb = ttk.Checkbutton(
            key_frame,
            text="保存密钥到系统密钥环",
            variable=self.save_key_var
        )
        save_key_cb.pack(anchor='w', pady=(5, 0))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        # 确定按钮
        ok_button = ttk.Button(
            button_frame,
            text="确定",
            command=self.on_ok
        )
        ok_button.pack(side='right', padx=(5, 0))

        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.on_cancel
        )
        cancel_button.pack(side='right')

        # 绑定回车键
        self.key_entry.bind('<Return>', lambda e: self.on_ok())
        self.key_entry.focus()

        # 等待对话框关闭
        self.dialog.wait_window()
        return self.api_key

    def toggle_key_visibility(self):
        """切换密钥显示/隐藏"""
        if self.show_key_var.get():
            self.key_entry.config(show="")
        else:
            self.key_entry.config(show="*")

    def on_ok(self):
        """确定按钮点击事件"""
        api_key = self.key_entry.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return

        # 简单验证API密钥格式
        if not api_key.startswith('sk-'):
            result = messagebox.askyesno(
                "警告",
                "API密钥格式可能不正确（通常以'sk-'开头）\n是否继续？"
            )
            if not result:
                return

        # 保存密钥到keyring（如果用户选择）
        if self.save_key_var.get():
            if ApiKeyManager.save_api_key(api_key):
                messagebox.showinfo("成功", "API密钥已安全保存到系统密钥环")
            else:
                messagebox.showwarning("警告", "保存API密钥失败，但仍可使用当前会话")

        self.api_key = api_key
        self.dialog.destroy()

    def on_cancel(self):
        """取消按钮点击事件"""
        self.api_key = None
        self.dialog.destroy()
