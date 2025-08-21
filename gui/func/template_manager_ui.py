#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理UI模块
功能：处理模板相关的UI操作，包括模板选择、保存和应用
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any


class TemplateManagerUI:
    """模板管理UI类"""
    
    def __init__(self, parent_window, template_manager, variable_rows, scrollable_frame, get_variable_configs_callback):
        """
        初始化模板管理UI
        
        Args:
            parent_window: 父窗口
            template_manager: 模板管理器实例
            variable_rows: 变量行列表的引用
            scrollable_frame: 可滚动框架的引用
            get_variable_configs_callback: 获取变量配置的回调函数
        """
        self.parent_window = parent_window
        self.template_manager = template_manager
        self.variable_rows = variable_rows
        self.scrollable_frame = scrollable_frame
        self.get_variable_configs = get_variable_configs_callback
    
    def load_template(self):
        """加载预设模板"""
        self.show_template_dialog()
    
    def show_template_dialog(self):
        """显示模板选择对话框"""
        template_window = tk.Toplevel(self.parent_window)
        template_window.title("选择模板")
        template_window.geometry("500x520")
        template_window.transient(self.parent_window)
        template_window.grab_set()

        # 主框架
        main_frame = ttk.Frame(template_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 模板列表
        ttk.Label(main_frame, text="可用模板:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # 创建列表框和滚动条
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        template_listbox = tk.Listbox(list_frame, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=template_listbox.yview)
        template_listbox.configure(yscrollcommand=scrollbar.set)

        template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载模板
        all_templates = self.template_manager.get_all_templates()
        template_data = []

        # 添加默认模板
        for template in all_templates['default']:
            display_name = f"[默认] {template['name']}"
            template_listbox.insert(tk.END, display_name)
            template_data.append(('default', template))

        # 添加用户模板
        for template in all_templates['user']:
            display_name = f"[用户] {template['name']}"
            template_listbox.insert(tk.END, display_name)
            template_data.append(('user', template))

        # 描述区域
        desc_frame = ttk.LabelFrame(main_frame, text="模板描述", padding="5")
        desc_frame.pack(fill=tk.X, pady=(0, 10))

        desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        desc_text.pack(fill=tk.X)

        def on_template_select(event):
            """模板选择事件"""
            selection = template_listbox.curselection()
            if selection:
                index = selection[0]
                template_type, template = template_data[index]

                desc_text.config(state=tk.NORMAL)
                desc_text.delete(1.0, tk.END)

                description = template.get('description', '无描述')
                variables_info = f"变量数量: {len(template.get('variables', []))}\n"

                desc_text.insert(tk.END, f"{description}\n\n{variables_info}")

                # 显示变量信息
                for i, var in enumerate(template.get('variables', []), 1):
                    var_info = f"{i}. {var.get('name', '')} ({var.get('data_type', '')})\n"
                    desc_text.insert(tk.END, var_info)

                desc_text.config(state=tk.DISABLED)

        template_listbox.bind('<<ListboxSelect>>', on_template_select)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def apply_template():
            """应用模板"""
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请选择一个模板！")
                return

            index = selection[0]
            template_type, template = template_data[index]

            # 清空现有变量
            for row in self.variable_rows:
                row.destroy()
            self.variable_rows.clear()

            # 应用模板变量
            for var_config in template.get('variables', []):
                self.add_variable_row_with_config(var_config)

            template_window.destroy()
            messagebox.showinfo("成功", f"已应用模板: {template['name']}")

        def save_current_as_template():
            """将当前配置保存为模板"""
            self.show_save_template_dialog(template_window)

        ttk.Button(button_frame, text="应用模板", command=apply_template).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="保存当前配置为模板", command=save_current_as_template).pack(side=tk.LEFT,
                                                                                                   padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=template_window.destroy).pack(side=tk.RIGHT)
    
    def add_variable_row_with_config(self, config: Dict[str, Any]):
        """添加带配置的变量行"""
        from gui.variable_row import VariableRow
        
        row_index = len(self.variable_rows)
        var_row = VariableRow(self.scrollable_frame, row_index, self._remove_variable_row_callback)
        var_row.create_widgets()

        # 应用配置
        var_row.apply_config(config)

        self.variable_rows.append(var_row)

        # 更新滚动区域
        self.scrollable_frame.update_idletasks()
    
    def _remove_variable_row_callback(self, row_index):
        """移除变量行的回调函数（需要主窗口提供）"""
        # 这个方法需要在主窗口中设置具体的实现
        pass
    
    def set_remove_variable_row_callback(self, callback):
        """设置移除变量行的回调函数"""
        self._remove_variable_row_callback = callback
    
    def show_save_template_dialog(self, parent_window=None):
        """显示保存模板对话框"""
        save_window = tk.Toplevel(parent_window or self.parent_window)
        save_window.title("保存模板")
        save_window.geometry("400x300")
        save_window.transient(parent_window or self.parent_window)
        save_window.grab_set()

        # 主框架
        main_frame = ttk.Frame(save_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 模板名称
        ttk.Label(main_frame, text="模板名称:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        name_entry.focus()

        # 模板描述
        ttk.Label(main_frame, text="模板描述:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        desc_text = tk.Text(main_frame, height=8, width=40, wrap=tk.WORD)
        desc_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        def save_template():
            """保存模板"""
            template_name = name_var.get().strip()
            if not template_name:
                messagebox.showwarning("警告", "请输入模板名称！")
                return

            description = desc_text.get(1.0, tk.END).strip()

            # 获取当前变量配置
            configs = self.get_variable_configs()
            if not configs:
                messagebox.showwarning("警告", "当前没有变量配置可保存！")
                return

            # 保存模板
            if self.template_manager.save_user_template(template_name, configs, description):
                messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功！")
                save_window.destroy()
            else:
                messagebox.showerror("错误", "保存模板失败！")

        ttk.Button(button_frame, text="保存", command=save_template).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=save_window.destroy).pack(side=tk.RIGHT)
