#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
功能：提供数据生成器的图形化界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from typing import List, Dict, Any
import threading
import datetime
import glob

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gui.variable_row import VariableRow
from core.data_generator_core import DataGeneratorCore
from core.file_manager_core import FileManagerCore
from core.config_manager import ConfigManager
from templates.template_manager import TemplateManager
from deepseek_api.deepseek_dialog import DeepSeekDialog, ApiKeyDialog
from deepseek_api.api_key_manager import ApiKeyManager

# 各个功能组件相关
from .func.deBug import debug
from gui.func.file_manager_ui import FileManagerUI
from .func.solution_executor import SolutionExecutor
from gui.func.template_manager_ui import TemplateManagerUI
from gui.func.deepseek_ui import DeepSeekUI
from gui.func.solution_editor_ui import SolutionEditorUI


class MainWindow:
    """主窗口类"""

    def __init__(self, root):
        self.root = root
        self.variable_rows = []

        # 初始化核心组件
        self.data_generator = DataGeneratorCore()
        self.file_manager = FileManagerCore()
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()

        # 初始化功能组件
        self.file_manager_ui = FileManagerUI(self.root)  # 文件管理组件
        self.solution_executor = SolutionExecutor(self.file_manager)  # 解决方案执行组件
        self.template_manager_ui = TemplateManagerUI(
            self.root, 
            self.template_manager, 
            self.variable_rows, 
            None,  # scrollable_frame 将在 create_widgets 后设置
            self.get_variable_configs
        )  # 模板管理组件
        self.deepseek_ui = DeepSeekUI(self.root)  # DeepSeek功能组件
        self.solution_editor_ui = SolutionEditorUI(self.root, self.solution_executor, self.deepseek_ui)  # 解决方案编辑组件

        # 加载用户配置
        self.user_config = self.config_manager.load_config()

        self.setup_window()
        self.create_widgets()
        self.add_initial_variable_row()

        # 应用保存的配置
        self.apply_saved_config()

    def setup_window(self):
        """设置窗口属性"""
        self.root.title("数据生成器 v2.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="数据生成器配置", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        # 变量配置区域（可滚动）
        self.create_variable_area(main_frame)

        # 控制按钮区域
        self.create_control_area(main_frame)

        # 生成配置区域
        self.create_generation_area(main_frame)

        # 设置模板管理UI的scrollable_frame引用
        self.template_manager_ui.scrollable_frame = self.scrollable_frame
        self.template_manager_ui.set_remove_variable_row_callback(self.remove_variable_row)

    def create_variable_area(self, parent):
        """创建变量配置区域"""
        # 变量配置框架
        var_frame = ttk.LabelFrame(parent, text="变量配置", padding="5")
        var_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        var_frame.columnconfigure(0, weight=1)
        var_frame.rowconfigure(0, weight=1)

        # 创建滚动区域
        canvas = tk.Canvas(var_frame, height=300)
        scrollbar = ttk.Scrollbar(var_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        self.scrollable_frame.columnconfigure(0, weight=1)

    def create_control_area(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 添加变量按钮
        add_btn = ttk.Button(control_frame, text="+ 添加变量", command=self.add_variable_row)
        add_btn.grid(row=0, column=0, padx=(0, 10))

        # 清空所有变量按钮
        clear_btn = ttk.Button(control_frame, text="清空所有", command=self.clear_all_variables)
        clear_btn.grid(row=0, column=1, padx=(0, 10))

        # 预设模板按钮
        template_btn = ttk.Button(control_frame, text="加载模板", command=self.load_template)
        template_btn.grid(row=0, column=2)

    def create_generation_area(self, parent):
        """创建生成配置区域"""
        gen_frame = ttk.LabelFrame(parent, text="生成配置", padding="5")
        gen_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
        # 测试用例数量
        ttk.Label(gen_frame, text="测试用例数量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.test_count_var = tk.StringVar()
        test_count_entry = ttk.Entry(gen_frame, textvariable=self.test_count_var, width=10)
        test_count_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
    
        # 不生成重复数据选项
        self.no_duplicate_var = tk.BooleanVar()
        no_duplicate_cb = ttk.Checkbutton(gen_frame, text="不生成重复数据", variable=self.no_duplicate_var)
        no_duplicate_cb.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
    
        # 删除临时文件选项
        self.delete_temp_files_var = tk.BooleanVar()
        delete_temp_cb = ttk.Checkbutton(gen_frame, text="生成zip后删除临时文件", variable=self.delete_temp_files_var)
        delete_temp_cb.grid(row=0, column=3, sticky=tk.W)
    
        # 输出目录
        ttk.Label(gen_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.output_dir_var = tk.StringVar()
        output_dir_entry = ttk.Entry(gen_frame, textvariable=self.output_dir_var, width=30)
        output_dir_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
    
        browse_btn = ttk.Button(gen_frame, text="浏览", 
                               command=lambda: self.file_manager_ui.browse_output_dir(self.output_dir_var))
        browse_btn.grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        
        # 删除按钮和时间选择下拉菜单
        delete_btn = ttk.Button(gen_frame, text="删除", 
                               command=lambda: self.file_manager_ui.delete_zip_files(self.output_dir_var, self.delete_time_var))
        delete_btn.grid(row=1, column=4, padx=(5, 0), pady=(5, 0))
        
        # 时间范围下拉菜单
        self.delete_time_var = tk.StringVar(value="一天内")
        time_options = ["一小时内", "一天内", "一周内", "一月内", "一年内"]
        time_combo = ttk.Combobox(gen_frame, textvariable=self.delete_time_var, values=time_options, 
                                 state="readonly", width=8)
        time_combo.grid(row=1, column=5, padx=(5, 0), pady=(5, 0))

        # 生成按钮
        generate_frame = ttk.Frame(parent)
        generate_frame.grid(row=4, column=0, pady=10)

        generate_btn = ttk.Button(generate_frame, text="生成测试数据", command=self.generate_data,
                                  style='Accent.TButton')
        generate_btn.grid(row=0, column=0, padx=(0, 10))

        preview_btn = ttk.Button(generate_frame, text="预览数据", command=self.preview_data)
        preview_btn.grid(row=0, column=1)

    def add_initial_variable_row(self):
        """添加初始变量行"""
        self.add_variable_row()

    def add_variable_row(self):
        """添加变量行"""
        row_index = len(self.variable_rows)
        var_row = VariableRow(self.scrollable_frame, row_index, self.remove_variable_row)
        var_row.create_widgets()
        self.variable_rows.append(var_row)

        # 更新滚动区域
        self.scrollable_frame.update_idletasks()

    def remove_variable_row(self, row_index):
        """移除变量行"""
        if len(self.variable_rows) <= 1:
            messagebox.showwarning("警告", "至少需要保留一个变量！")
            return

        # 移除指定行
        if 0 <= row_index < len(self.variable_rows):
            self.variable_rows[row_index].destroy()
            self.variable_rows.pop(row_index)

            # 重新排列剩余行的索引
            for i, row in enumerate(self.variable_rows):
                row.update_index(i)

    def clear_all_variables(self):
        """清空所有变量"""
        if messagebox.askyesno("确认", "确定要清空所有变量配置吗？"):
            for row in self.variable_rows:
                row.destroy()
            self.variable_rows.clear()
            self.add_initial_variable_row()

    def load_template(self):
        """加载预设模板"""
        self.template_manager_ui.load_template()

    def get_variable_configs(self) -> List[Dict[str, Any]]:
        """获取所有变量配置"""
        configs = []
        for row in self.variable_rows:
            config = row.get_config()
            if config:
                configs.append(config)
        return configs

    def preview_data(self):
        """预览数据"""
        try:
            configs = self.get_variable_configs()
            if not configs:
                messagebox.showwarning("警告", "请至少配置一个变量！")
                return

            # 获取不重复数据选项
            no_duplicate = self.no_duplicate_var.get()

            # 生成预览数据（只生成3组）
            preview_data = self.data_generator.generate_preview_data(configs, 3, no_duplicate)

            # 显示预览窗口
            self.show_preview_window(preview_data)

        except Exception as e:
            messagebox.showerror("错误", f"预览数据时出错：{str(e)}")

    def generate_data(self):
        """生成测试数据"""
        try:
            # 获取配置
            configs = self.get_variable_configs()
            if not configs:
                messagebox.showwarning("警告", "请至少配置一个变量！")
                return

            test_count = int(self.test_count_var.get())
            if test_count <= 0:
                messagebox.showwarning("警告", "测试用例数量必须大于0！")
                return

            output_dir = self.output_dir_var.get()
            if not output_dir:
                messagebox.showwarning("警告", "请选择输出目录！")
                return

            # 获取不重复数据选项
            no_duplicate = self.no_duplicate_var.get()

            # 获取删除临时文件选项
            delete_temp_files = self.delete_temp_files_var.get()

            # 生成数据
            generated_data = self.data_generator.generate_test_data(configs, test_count, no_duplicate)

            # 保存文件
            save_result = self.file_manager.save_test_files(generated_data, output_dir,
                                                                delete_temp_files=delete_temp_files)

            # 询问是否生成处理结果
            if messagebox.askyesno("生成处理结果", "数据生成完成！是否生成处理结果(.out文件)？"):
                # 修复：使用正确的变量名
                input_files = save_result.get('created_files', [])
                self.solution_editor_ui.show_solution_editor(generated_data, output_dir, input_files, self.delete_temp_files_var)
            else:
                success_msg = f"成功生成 {test_count} 组测试数据！\n输出目录：{output_dir}"
                if delete_temp_files and 'deleted_temp_files' in save_result:
                    success_msg += f"\n已删除临时文件：{len(save_result['deleted_temp_files'])} 个"
                messagebox.showinfo("成功", success_msg)

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"生成数据时出错：{str(e)}")

    def show_preview_window(self, preview_data):
        """显示预览窗口"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("数据预览")
        preview_window.geometry("600x400")

        # 创建文本框显示预览数据
        text_frame = ttk.Frame(preview_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 插入预览数据
        for i, data in enumerate(preview_data, 1):
            text_widget.insert(tk.END, f"=== 测试用例 {i} ===\n")
            text_widget.insert(tk.END, data + "\n\n")

        text_widget.config(state=tk.DISABLED)

        # 关闭按钮
        close_btn = ttk.Button(preview_window, text="关闭", command=preview_window.destroy)
        close_btn.pack(pady=10)

    def apply_saved_config(self):
        """应用保存的配置"""
        try:
            # 应用测试用例数量
            self.test_count_var.set(self.user_config.get('test_count', '10'))

            # 应用不重复数据选项
            self.no_duplicate_var.set(self.user_config.get('no_duplicate', False))

            # 应用删除临时文件选项
            self.delete_temp_files_var.set(self.user_config.get('delete_temp_files', False))

            # 应用输出目录
            self.output_dir_var.set(self.user_config.get('output_dir', './test_data'))

        except Exception as e:
            debug(f"应用配置时出错: {e}")

    def save_current_config(self):
        """保存当前配置"""
        try:
            current_config = {
                'test_count': self.test_count_var.get(),
                'no_duplicate': self.no_duplicate_var.get(),
                'delete_temp_files': self.delete_temp_files_var.get(),
                'output_dir': self.output_dir_var.get()
            }

            self.config_manager.save_config(current_config)

        except Exception as e:
            debug(f"保存配置时出错: {e}")

    def on_closing(self):
        """窗口关闭时的处理"""
        # 保存当前配置
        self.save_current_config()
        # 关闭窗口
        self.root.destroy()
