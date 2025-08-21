#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量行组件
功能：单个变量的配置界面
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional


class VariableRow:
    """变量行类"""
    
    def __init__(self, parent, index: int, remove_callback: Callable[[int], None]):
        self.parent = parent
        self.index = index
        self.remove_callback = remove_callback
        
        # 变量配置
        self.var_name = tk.StringVar(value=f"var{index + 1}")
        self.data_type = tk.StringVar(value="整数")
        self.source_type = tk.StringVar(value="数据范围")
        self.separator = tk.StringVar(value="换行")
        self.loop_count = tk.StringVar(value="1")  # 循环次数
        
        # 数据源配置
        self.range_min = tk.StringVar(value="1")
        self.range_max = tk.StringVar(value="100")
        self.choice_list = tk.StringVar(value="")
        self.char_set = tk.StringVar(value="a-z")
        self.string_length = tk.StringVar(value="10")
        self.custom_code = tk.StringVar(value="")  # 自定义代码
        
        # 界面组件
        self.frame = None
        self.source_config_frame = None
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.frame = ttk.Frame(self.parent, relief="ridge", padding="5")
        self.frame.grid(row=self.index, column=0, sticky=(tk.W, tk.E), pady=2)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(3, weight=1)
        self.frame.columnconfigure(5, weight=1)
        
        # 变量名
        ttk.Label(self.frame, text="变量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        var_name_entry = ttk.Entry(self.frame, textvariable=self.var_name, width=10)
        var_name_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 数据类型
        ttk.Label(self.frame, text="类型:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        data_type_combo = ttk.Combobox(self.frame, textvariable=self.data_type, 
                                     values=["整数", "浮点数", "字符串", "字符"], 
                                     state="readonly", width=8)
        data_type_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        data_type_combo.bind('<<ComboboxSelected>>', self.on_data_type_changed)
        
        # 来源类型
        ttk.Label(self.frame, text="来自:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        source_type_combo = ttk.Combobox(self.frame, textvariable=self.source_type,
                                       values=["数据范围", "选择列表", "字符集合", "来自代码"],
                                       state="readonly", width=10)
        source_type_combo.grid(row=0, column=5, sticky=tk.W, padx=(0, 10))
        source_type_combo.bind('<<ComboboxSelected>>', self.on_source_type_changed)
        
        # 循环次数
        ttk.Label(self.frame, text="循环:").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        loop_entry = ttk.Entry(self.frame, textvariable=self.loop_count, width=6)
        loop_entry.grid(row=0, column=7, sticky=tk.W, padx=(0, 10))
        
        # 为循环次数输入框添加提示
        def show_loop_tooltip(event):
            tooltip_text = "输入数字或变量名\n例如: 1, 5, n"
            # 这里可以添加更详细的提示逻辑
        
        loop_entry.bind("<Enter>", show_loop_tooltip)
        
        # 分隔符
        ttk.Label(self.frame, text="分隔符:").grid(row=0, column=8, sticky=tk.W, padx=(0, 5))
        separator_combo = ttk.Combobox(self.frame, textvariable=self.separator,
                                     values=["换行", "空格", "制表符", "逗号", "分号"],
                                     state="readonly", width=8)
        separator_combo.grid(row=0, column=9, sticky=tk.W, padx=(0, 10))
        
        # 删除按钮
        remove_btn = ttk.Button(self.frame, text="×", width=3, 
                              command=lambda: self.remove_callback(self.index))
        remove_btn.grid(row=0, column=10, padx=(10, 0))
        
        # 数据源配置区域
        self.create_source_config_area()
    
    def create_source_config_area(self):
        """创建数据源配置区域"""
        if self.source_config_frame:
            self.source_config_frame.destroy()
        
        self.source_config_frame = ttk.Frame(self.frame)
        self.source_config_frame.grid(row=1, column=0, columnspan=11, sticky=(tk.W, tk.E), pady=(5, 0))
        self.source_config_frame.columnconfigure(1, weight=1)
        
        source_type = self.source_type.get()
        
        if source_type == "数据范围":
            self.create_range_config()
        elif source_type == "选择列表":
            self.create_choice_config()
        elif source_type == "字符集合":
            self.create_charset_config()
        elif source_type == "来自代码":
            self.create_code_config()
    
    def create_range_config(self):
        """创建数据范围配置"""
        ttk.Label(self.source_config_frame, text="范围:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        min_entry = ttk.Entry(self.source_config_frame, textvariable=self.range_min, width=10)
        min_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(self.source_config_frame, text="到").grid(row=0, column=2, padx=5)
        
        max_entry = ttk.Entry(self.source_config_frame, textvariable=self.range_max, width=10)
        max_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # 如果是字符串类型，添加长度配置
        if self.data_type.get() == "字符串":
            ttk.Label(self.source_config_frame, text="长度:").grid(row=0, column=4, sticky=tk.W, padx=(20, 5))
            length_entry = ttk.Entry(self.source_config_frame, textvariable=self.string_length, width=8)
            length_entry.grid(row=0, column=5, sticky=tk.W)
            
            # 添加长度格式说明
            length_example = "长度格式: 10 (固定) 或 1,10 (随机1-10)"
            ttk.Label(self.source_config_frame, text=length_example, foreground="blue").grid(row=1, column=4, columnspan=2, sticky=tk.W, pady=(2, 0))
    
    def create_choice_config(self):
        """创建选择列表配置"""
        ttk.Label(self.source_config_frame, text="选项 (用逗号分隔):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        choice_entry = ttk.Entry(self.source_config_frame, textvariable=self.choice_list, width=50)
        choice_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 示例标签
        example_text = "例如: apple,banana,orange 或 1,2,3,4,5"
        ttk.Label(self.source_config_frame, text=example_text, foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
    
    def create_charset_config(self):
        """创建字符集合配置"""
        ttk.Label(self.source_config_frame, text="字符集:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        charset_entry = ttk.Entry(self.source_config_frame, textvariable=self.char_set, width=30)
        charset_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 如果是字符串类型，添加长度配置
        if self.data_type.get() == "字符串":
            ttk.Label(self.source_config_frame, text="长度:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
            length_entry = ttk.Entry(self.source_config_frame, textvariable=self.string_length, width=8)
            length_entry.grid(row=0, column=3, sticky=tk.W)
        
        # 示例标签
        example_text = "例如: a-z (小写字母), A-Z (大写字母), 0-9 (数字), abc123 (指定字符)"
        ttk.Label(self.source_config_frame, text=example_text, foreground="gray").grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # 如果是字符串类型，添加长度格式说明
        if self.data_type.get() == "字符串":
            length_example = "长度格式: 10 (固定长度) 或 1,10 (随机长度1-10)"
            ttk.Label(self.source_config_frame, text=length_example, foreground="blue").grid(row=2, column=1, columnspan=3, sticky=tk.W, pady=(2, 0))
    
    def create_code_config(self):
        """创建代码配置"""
        ttk.Label(self.source_config_frame, text="代码:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # 代码预览框（只读，显示代码摘要）
        self.code_preview = tk.Text(self.source_config_frame, height=2, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.code_preview.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 编辑代码按钮
        edit_code_btn = ttk.Button(self.source_config_frame, text="编辑代码", command=self.open_code_editor)
        edit_code_btn.grid(row=0, column=2, padx=(5, 0))
        
        # 更新代码预览
        self.update_code_preview()
        
        # 示例标签
        example_text = "编写函数生成数据，函数必须返回生成的数据值"
        ttk.Label(self.source_config_frame, text=example_text, foreground="gray").grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(2, 0))
    
    def update_code_preview(self):
        """更新代码预览"""
        code = self.custom_code.get().strip()
        self.code_preview.config(state=tk.NORMAL)
        self.code_preview.delete(1.0, tk.END)
        
        if code:
            # 显示代码的前两行作为预览
            lines = code.split('\n')
            preview_lines = lines[:2]
            preview_text = '\n'.join(preview_lines)
            if len(lines) > 2:
                preview_text += '\n...'
            self.code_preview.insert(1.0, preview_text)
        else:
            # 显示模板代码的前两行作为预览
            template_preview = "def generate_data():\n    # 在这里编写生成数据的代码\n..."
            self.code_preview.insert(1.0, template_preview)
        
        # 设置正常的文本颜色
        self.code_preview.config(foreground="black")
        self.code_preview.config(state=tk.DISABLED)
    
    def open_code_editor(self):
        """打开代码编辑器窗口"""
        from .code_editor import show_code_editor
        
        # 定义模板代码
        template_code = """def generate_data():
    # 在这里编写生成数据的代码
    # 函数必须返回生成的数据值
    # 例如：
    # import random
    # return random.randint(1, 100)
    
    return None"""
        
        # 显示代码编辑器
        result_code = show_code_editor(
            parent=self.parent.winfo_toplevel(),
            title=f"代码编辑器 - {self.var_name.get()}",
            initial_code=self.custom_code.get(),
            template_code=template_code,
            width=700,
            height=600
        )
        
        # 保存结果
        self.custom_code.set(result_code)
        self.update_code_preview()
        
        # 示例标签
        example_text = "编写函数生成数据，函数必须返回生成的数据值"
        ttk.Label(self.source_config_frame, text=example_text, foreground="gray").grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(2, 0))
    
    def on_data_type_changed(self, event=None):
        """数据类型改变时的回调"""
        data_type = self.data_type.get()
        
        # 根据数据类型调整可用的来源类型
        if data_type in ["整数", "浮点数"]:
            # 数值类型支持数据范围、选择列表和来自代码
            source_values = ["数据范围", "选择列表", "来自代码"]
        elif data_type == "字符":
            # 字符类型支持选择列表、字符集合和来自代码
            source_values = ["选择列表", "字符集合", "来自代码"]
        else:  # 字符串
            # 字符串类型支持所有来源类型
            source_values = ["数据范围", "选择列表", "字符集合", "来自代码"]
        
        # 更新来源类型下拉框
        source_combo = None
        for child in self.frame.winfo_children():
            if isinstance(child, ttk.Combobox) and child['textvariable'] == str(self.source_type):
                source_combo = child
                break
        
        if source_combo:
            current_value = self.source_type.get()
            source_combo['values'] = source_values
            
            # 如果当前值不在新的选项中，设置为第一个选项
            if current_value not in source_values:
                self.source_type.set(source_values[0])
        
        # 重新创建数据源配置区域
        self.create_source_config_area()
    
    def on_source_type_changed(self, event=None):
        """来源类型改变时的回调"""
        self.create_source_config_area()
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """获取变量配置"""
        var_name = self.var_name.get().strip()
        if not var_name:
            return None
        
        config = {
            'name': var_name,
            'data_type': self.data_type.get(),
            'source_type': self.source_type.get(),
            'separator': self.separator.get(),
            'loop_count': self.loop_count.get().strip() if self.loop_count.get().strip() else 1
        }
        
        # 根据来源类型添加相应配置
        source_type = self.source_type.get()
        
        if source_type == "数据范围":
            try:
                config['min_value'] = self.range_min.get().strip()
                config['max_value'] = self.range_max.get().strip()
                if self.data_type.get() == "字符串":
                    config['string_length'] = self.string_length.get().strip()
            except ValueError:
                return None
                
        elif source_type == "选择列表":
            choices = self.choice_list.get().strip()
            if not choices:
                return None
            config['choices'] = [choice.strip() for choice in choices.split(',') if choice.strip()]
            
        elif source_type == "字符集合":
            charset = self.char_set.get().strip()
            if not charset:
                return None
            config['charset'] = charset
            if self.data_type.get() == "字符串":
                config['string_length'] = self.string_length.get().strip()
                
        elif source_type == "来自代码":
            code = self.custom_code.get().strip()
            if not code:
                return None
            config['custom_code'] = code
        
        return config
    
    def update_index(self, new_index: int):
        """更新行索引"""
        self.index = new_index
        if self.frame:
            self.frame.grid(row=new_index, column=0, sticky=(tk.W, tk.E), pady=2)
    
    def apply_config(self, config: Dict[str, Any]):
        """应用配置到变量行
        
        Args:
            config: 变量配置字典
        """
        # 设置基本配置
        if 'name' in config:
            self.var_name.set(config['name'])
        if 'data_type' in config:
            self.data_type.set(config['data_type'])
        if 'source_type' in config:
            self.source_type.set(config['source_type'])
        if 'separator' in config:
            self.separator.set(config['separator'])
        if 'loop_count' in config:
            self.loop_count.set(str(config['loop_count']))
        
        # 设置数据源配置
        source_type = config.get('source_type', '')
        
        if source_type == '数据范围':
            if 'min_value' in config:
                self.range_min.set(config['min_value'])
            if 'max_value' in config:
                self.range_max.set(config['max_value'])
            if 'string_length' in config:
                self.string_length.set(str(config['string_length']))
                
        elif source_type == '选择列表':
            if 'choices' in config:
                choices_str = ','.join(map(str, config['choices']))
                self.choice_list.set(choices_str)
                
        elif source_type == '字符集合':
            if 'charset' in config:
                self.char_set.set(config['charset'])
            if 'string_length' in config:
                self.string_length.set(str(config['string_length']))
                
        elif source_type == '来自代码':
            if 'custom_code' in config:
                self.custom_code.set(config['custom_code'])
        
        # 重新创建数据源配置区域以反映更改
        self.create_source_config_area()
    
    def destroy(self):
        """销毁组件"""
        if self.frame:
            self.frame.destroy()