#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动补全功能模块
功能：为代码编辑器提供智能自动补全功能
"""

import tkinter as tk
import keyword
import builtins
import re

from .func import deBug


class AutoCompletion:
    """自动补全类"""
    
    def __init__(self, text_widget, language="python"):
        """
        初始化自动补全功能
        
        Args:
            text_widget: 文本控件
            language: 编程语言类型
        """
        self.text_widget = text_widget
        self.language = language
        
        # 自动补全相关属性
        self.completion_window = None
        self.completion_listbox = None
        self.completion_candidates = []
        self.completion_start_pos = None
        self.completion_prefix = ""
        
        # Python 关键字和内置函数
        self.python_keywords = keyword.kwlist
        self.python_builtins = dir(builtins)
        
        # 符号配对映射
        self.symbol_pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'",
            '`': '`'
        }
        
        # 右符号集合，用于快速查找
        self.right_symbols = set(self.symbol_pairs.values())
    
    def show_completion(self):
        """显示自动补全窗口"""
        try:
            # 获取当前光标位置
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # 获取当前行内容
            line_start = f"{line}.0"
            line_end = f"{line}.end"
            line_content = self.text_widget.get(line_start, line_end)

            # 检查是否是对象方法调用（如 a.）
            dot_pos = line_content.rfind('.', 0, col)
            if dot_pos != -1 and dot_pos < col:
                # 找到点操作符，获取对象名和方法前缀
                obj_start = dot_pos - 1
                while obj_start >= 0 and (line_content[obj_start].isalnum() or line_content[obj_start] == '_'):
                    obj_start -= 1
                obj_start += 1

                object_name = line_content[obj_start:dot_pos]
                method_prefix = line_content[dot_pos + 1:col]

                # 获取对象方法补全候选项
                candidates = self.get_object_method_candidates(object_name, method_prefix, line_content)

                if candidates:
                    # 保存补全信息
                    self.completion_prefix = method_prefix
                    self.completion_start_pos = f"{line}.{dot_pos + 1}"
                    self.completion_candidates = candidates
                    # 创建或更新补全窗口
                    self.create_completion_window(cursor_pos)
                    return
                else:
                    self.hide_completion()
                    return

            # 常规标识符补全
            # 找到当前单词的开始位置
            word_start = col
            while word_start > 0 and (line_content[word_start - 1].isalnum() or line_content[word_start - 1] == '_'):
                word_start -= 1

            # 获取当前输入的前缀
            prefix = line_content[word_start:col]

            if len(prefix) < 1:  # 至少输入1个字符才显示补全
                self.hide_completion()
                return

            # 获取补全候选项
            candidates = self.get_completion_candidates(prefix)

            if not candidates:
                self.hide_completion()
                return

            # 保存补全信息
            self.completion_prefix = prefix
            self.completion_start_pos = f"{line}.{word_start}"
            self.completion_candidates = candidates

            # 创建或更新补全窗口
            self.create_completion_window(cursor_pos)

        except Exception as e:
            deBug.info(f"补全显示错误: {e}")
            self.hide_completion()
    
    def get_object_method_candidates(self, object_name, method_prefix, full_line):
        """获取对象方法补全候选项"""
        candidates = []
        method_prefix_lower = method_prefix.lower()
    
        # 尝试分析对象类型
        object_type = self.infer_object_type(object_name, full_line)
    
        # 根据对象类型获取方法
        methods = self.get_methods_for_type(object_type)
    
        # 修复：现在 methods 是一个列表，不是字典
        for method_info in methods:
            method_name = method_info['text']
            if method_name.lower().startswith(method_prefix_lower):
                candidates.append((method_name, method_info['type'], method_info.get('auto_parentheses', False)))
    
        # 排序候选项：常用方法优先
        candidates.sort(key=lambda x: (x[1] != "method", x[0].lower()))
    
        return candidates[:15]  # 限制显示数量
    
    def infer_object_type(self, object_name, full_line):
        """推断对象类型"""
        # 获取整个文件内容进行分析
        try:
            code = self.text_widget.get(1.0, tk.END)
            lines = code.split('\n')
    
            # 首先检查是否是导入的模块
            for line in lines:
                line = line.strip()
                # 检查 import module 语句
                if line.startswith('import ') and object_name in line:
                    # 处理 "import random" 或 "import random, os" 等情况
                    import_parts = line.replace('import ', '').split(',')
                    for part in import_parts:
                        module_name = part.strip()
                        if module_name == object_name:
                            return f"module_{object_name}"
                    
                # 检查 from module import * 语句
                elif line.startswith('from ') and 'import' in line:
                    # 处理 "from random import *" 等情况
                    if f'from {object_name} import' in line:
                        return f"module_{object_name}"
                    
                # 检查 import module as alias 语句
                elif 'import' in line and ' as ' in line:
                    # 处理 "import random as rd" 等情况
                    parts = line.split(' as ')
                    if len(parts) == 2:
                        import_part = parts[0].strip()
                        alias = parts[1].strip()
                        if alias == object_name and 'import' in import_part:
                            module_name = import_part.replace('import ', '').strip()
                            return f"module_{module_name}"
    
            # 查找变量赋值语句
            for line in lines:
                line = line.strip()
                if f"{object_name} = " in line:
                    # 简单的类型推断
                    if '"' in line or "'" in line:
                        return "str"
                    elif "[" in line and "]" in line:
                        return "list"
                    elif "{" in line and "}" in line:
                        # 更精确的字典/集合判断
                        assignment_part = line.split('=', 1)[1].strip()
                        if assignment_part == "{}":
                            # 空字典
                            return "dict"
                        elif ":" in assignment_part:
                            # 包含键值对的字典
                            return "dict"
                        elif assignment_part.startswith("set("):
                            # 显式的集合构造
                            return "set"
                        else:
                            # 其他情况，可能是集合字面量 {1, 2, 3}
                            return "set"
                    elif line.endswith(".split(") or ".strip(" in line:
                        return "str"
                    elif "int(" in line:
                        return "int"
                    elif "float(" in line:
                        return "float"
                    elif "range(" in line:
                        return "range"
    
            # 如果没有找到明确的赋值，返回通用类型
            return "object"
    
        except:
            return "object"

    def get_methods_for_type(self, obj_type):
        """为指定类型获取方法建议"""
        methods = []
        
        try:
            if obj_type == 'str':
                # 创建一个字符串实例并获取其方法
                sample_obj = ""
            elif obj_type == 'list':
                sample_obj = []
            elif obj_type == 'dict':
                sample_obj = {}
            elif obj_type == 'set':
                sample_obj = set()
            elif obj_type == 'tuple':
                sample_obj = ()
            elif obj_type == 'int':
                sample_obj = 0
            elif obj_type == 'float':
                sample_obj = 0.0
            elif obj_type == 'file':
                # 对于文件对象，我们需要特殊处理
                import io
                sample_obj = io.StringIO()
            else:
                # 尝试动态导入模块
                try:
                    if '.' in obj_type:
                        module_name, class_name = obj_type.rsplit('.', 1)
                        module = __import__(module_name, fromlist=[class_name])
                        if hasattr(module, class_name):
                            sample_obj = getattr(module, class_name)
                            # 如果是类，尝试创建实例
                            if isinstance(sample_obj, type):
                                try:
                                    sample_obj = sample_obj()
                                except:
                                    # 如果无法实例化，直接使用类
                                    pass
                        else:
                            return []
                    else:
                        module = __import__(obj_type)
                        sample_obj = module
                except ImportError:
                    return []
            
            # 使用 dir() 获取所有属性和方法
            all_attrs = dir(sample_obj)
            
            for attr in all_attrs:
                # 过滤掉私有方法（以双下划线开头和结尾的）
                if attr.startswith('__') and attr.endswith('__'):
                    continue
                
                try:
                    # 检查是否是可调用的方法
                    attr_obj = getattr(sample_obj, attr)
                    if callable(attr_obj):
                        # 检查是否需要括号
                        needs_parentheses = True
                        try:
                            import inspect
                            sig = inspect.signature(attr_obj)
                            # 如果方法有必需参数（除了self），则需要括号
                            params = list(sig.parameters.values())
                            if params and params[0].name == 'self':
                                params = params[1:]  # 移除self参数
                            
                            # 如果没有必需参数，或者所有参数都有默认值
                            required_params = [p for p in params if p.default == inspect.Parameter.empty]
                            if not required_params:
                                needs_parentheses = True  # 仍然显示括号，但用户可以直接按Tab补全
                        except:
                            needs_parentheses = True
                        
                        display_text = f"{attr}()" if needs_parentheses else attr
                        methods.append({
                            'text': attr,
                            'display': display_text,
                            'type': 'method'
                        })
                    else:
                        # 属性（非方法）
                        methods.append({
                            'text': attr,
                            'display': attr,
                            'type': 'property'
                        })
                except:
                    # 如果无法获取属性，跳过
                    continue
            
            # 按名称排序，方法优先
            methods.sort(key=lambda x: (x['type'] != 'method', x['text']))
            
        except Exception as e:
            # 如果出现任何错误，返回空列表
            pass
        
        return methods
    
    def get_completion_candidates(self, prefix):
        """获取补全候选项"""
        candidates = []
        prefix_lower = prefix.lower()

        # Python 关键字
        for keyword_item in self.python_keywords:
            if keyword_item.lower().startswith(prefix_lower):
                candidates.append((keyword_item, "keyword", False))

        # Python 内置函数
        for builtin in self.python_builtins:
            if not builtin.startswith('_') and builtin.lower().startswith(prefix_lower):
                # 内置函数需要自动添加括号
                auto_parentheses = builtin in ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'max', 'min', 'sum', 'abs', 'round', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'input', 'open']
                candidates.append((builtin, "builtin", auto_parentheses))

        # 当前文件中的标识符
        file_identifiers = self.extract_identifiers_from_code()
        for identifier in file_identifiers:
            if identifier.lower().startswith(prefix_lower) and identifier != prefix:
                candidates.append((identifier, "identifier", False))

        # 去重并排序
        unique_candidates = list(set(candidates))
        unique_candidates.sort(key=lambda x: (x[1] != "keyword", x[1] != "builtin", x[0].lower()))

        return unique_candidates[:20]  # 限制显示数量
    
    def extract_identifiers_from_code(self):
        """从当前代码中提取标识符"""
        try:
            code = self.text_widget.get(1.0, tk.END)
            # 使用正则表达式提取标识符
            pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
            identifiers = re.findall(pattern, code)
            # 过滤掉关键字和内置函数
            filtered = []
            for identifier in identifiers:
                if (identifier not in self.python_keywords and
                        identifier not in self.python_builtins and
                        len(identifier) > 1):
                    filtered.append(identifier)
            return list(set(filtered))
        except:
            return []
    
    def create_completion_window(self, cursor_pos):
        """创建自动补全窗口"""
        if self.completion_window:
            self.completion_window.destroy()

        # 创建顶层窗口
        self.completion_window = tk.Toplevel(self.text_widget)
        self.completion_window.wm_overrideredirect(True)
        self.completion_window.configure(bg='white', relief='solid', bd=1)

        # 创建列表框
        self.completion_listbox = tk.Listbox(
            self.completion_window,
            height=min(10, len(self.completion_candidates)),
            font=('Consolas', 9),
            selectmode=tk.SINGLE,
            bg='white',
            fg='black',
            selectbackground='#0078d4',
            selectforeground='white',
            relief='flat',
            bd=0
        )
        self.completion_listbox.pack(fill=tk.BOTH, expand=True)

        # 填充候选项
        for candidate_info in self.completion_candidates:
            if len(candidate_info) == 3:
                candidate, candidate_type, auto_parentheses = candidate_info
            else:
                candidate, candidate_type = candidate_info
                auto_parentheses = False
            
            # 根据类型显示不同的图标或标识
            if candidate_type == "method":
                display_text = f"🔧 {candidate}"
            elif candidate_type == "attribute":
                display_text = f"📋 {candidate}"
            elif candidate_type == "builtin":
                display_text = f"⚙️ {candidate}"
            elif candidate_type == "keyword":
                display_text = f"🔑 {candidate}"
            else:
                display_text = f"📝 {candidate}"
                
            self.completion_listbox.insert(tk.END, display_text)

        # 选中第一项
        if self.completion_candidates:
            self.completion_listbox.selection_set(0)

        # 绑定补全窗口的键盘事件
        self.completion_listbox.bind('<Double-Button-1>', lambda e: self.accept_completion())
        self.completion_listbox.bind('<Return>', lambda e: self.accept_completion())
        self.completion_listbox.bind('<Tab>', lambda e: self.accept_completion())
        self.completion_listbox.bind('<Escape>', lambda e: self.hide_completion())
        self.completion_listbox.bind('<Up>', self.handle_listbox_navigation)
        self.completion_listbox.bind('<Down>', self.handle_listbox_navigation)

        # 计算窗口位置
        self.position_completion_window(cursor_pos)
    
    def handle_listbox_navigation(self, event):
        """处理补全列表框的导航"""
        current_selection = self.completion_listbox.curselection()
        if not current_selection:
            self.completion_listbox.selection_set(0)
            return "break"

        current_index = current_selection[0]

        if event.keysym == 'Down':
            new_index = min(current_index + 1, self.completion_listbox.size() - 1)
        elif event.keysym == 'Up':
            new_index = max(current_index - 1, 0)
        else:
            return

        self.completion_listbox.selection_clear(0, tk.END)
        self.completion_listbox.selection_set(new_index)
        self.completion_listbox.see(new_index)
        return "break"
    
    def position_completion_window(self, cursor_pos):
        """定位补全窗口位置"""
        try:
            # 获取光标在屏幕上的位置
            bbox = self.text_widget.bbox(cursor_pos)
            if bbox:
                x, y, width, height = bbox
                # 转换为屏幕坐标
                screen_x = self.text_widget.winfo_rootx() + x
                screen_y = self.text_widget.winfo_rooty() + y + height + 2

                # 确保窗口不会超出屏幕边界
                screen_width = self.completion_window.winfo_screenwidth()
                screen_height = self.completion_window.winfo_screenheight()

                # 更新窗口以获取实际大小
                self.completion_window.update_idletasks()
                window_width = self.completion_window.winfo_reqwidth()
                window_height = self.completion_window.winfo_reqheight()

                # 调整位置避免超出屏幕
                if screen_x + window_width > screen_width:
                    screen_x = screen_width - window_width - 10
                if screen_y + window_height > screen_height:
                    screen_y = self.text_widget.winfo_rooty() + y - window_height - 2

                self.completion_window.geometry(f"+{screen_x}+{screen_y}")
        except:
            # 如果定位失败，使用默认位置
            self.completion_window.geometry("+100+100")
    
    def accept_completion(self):
        """接受当前选中的补全项"""
        if not self.completion_listbox or not self.completion_candidates:
            return "break"
    
        current_selection = self.completion_listbox.curselection()
        if not current_selection:
            return "break"
    
        selected_index = current_selection[0]
        candidate_info = self.completion_candidates[selected_index]
    
        if len(candidate_info) == 3:
            selected_candidate, candidate_type, auto_parentheses = candidate_info
        else:
            selected_candidate, candidate_type = candidate_info
            auto_parentheses = False
    
        # 计算当前输入的结束位置
        line, col = map(int, self.completion_start_pos.split('.'))
        current_end_pos = f"{line}.{col + len(self.completion_prefix)}"
    
        # 替换文本 - 使用保存的位置而不是当前光标位置
        self.text_widget.delete(self.completion_start_pos, current_end_pos)
    
        # 定义需要自动添加空格的关键字
        keywords_need_space = {
            'import', 'from', 'return', 'yield', 'raise', 'assert', 
            'del', 'global', 'nonlocal', 'if', 'elif', 'while', 
            'for', 'try', 'except', 'finally', 'with', 'as',
            'class', 'def', 'lambda', 'and', 'or', 'not', 'in', 'is'
        }
    
        # 插入补全文本
        insert_text = selected_candidate
        
        if auto_parentheses and candidate_type in ["builtin", "method", "function"]:
            insert_text += "()"
            # 将光标放在括号之间
            self.text_widget.insert(self.completion_start_pos, insert_text)
            new_cursor_pos = f"{line}.{col + len(selected_candidate) + 1}"
            self.text_widget.mark_set(tk.INSERT, new_cursor_pos)
        elif candidate_type == "keyword" and selected_candidate in keywords_need_space:
            # 关键字后自动添加空格
            insert_text += " "
            self.text_widget.insert(self.completion_start_pos, insert_text)
            # 设置光标到空格后面
            new_cursor_pos = f"{line}.{col + len(selected_candidate) + 1}"
            self.text_widget.mark_set(tk.INSERT, new_cursor_pos)
        else:
            self.text_widget.insert(self.completion_start_pos, insert_text)
            # 设置光标到补全文本的末尾
            new_cursor_pos = f"{line}.{col + len(selected_candidate)}"
            self.text_widget.mark_set(tk.INSERT, new_cursor_pos)
    
        # 隐藏补全窗口
        self.hide_completion()
        return "break"
    
    def hide_completion(self, event=None):
        """隐藏补全窗口"""
        if self.completion_window:
            self.completion_window.destroy()
            self.completion_window = None
            self.completion_listbox = None
            self.completion_candidates = []
            self.completion_start_pos = None
            self.completion_prefix = ""
    
    def handle_completion_navigation(self, event):
        """处理补全窗口的导航键"""
        if not self.completion_listbox:
            return

        current_selection = self.completion_listbox.curselection()
        if not current_selection:
            self.completion_listbox.selection_set(0)
            return

        current_index = current_selection[0]

        if event.keysym == 'Down':
            new_index = min(current_index + 1, self.completion_listbox.size() - 1)
        elif event.keysym == 'Up':
            new_index = max(current_index - 1, 0)
        else:
            return

        self.completion_listbox.selection_clear(0, tk.END)
        self.completion_listbox.selection_set(new_index)
        self.completion_listbox.see(new_index)

    def handle_symbol_input(self, event):
        """处理符号输入的配对功能"""
        char = event.char
        
        # 处理左符号：自动插入配对的右符号
        if char in self.symbol_pairs:
            return self.insert_symbol_pair(char)
        
        # 处理右符号：智能跳过或插入
        elif char in self.right_symbols:
            return self.handle_right_symbol(char)
        
        return None
    
    def insert_symbol_pair(self, left_symbol):
        """插入符号配对"""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            right_symbol = self.symbol_pairs[left_symbol]
            
            # 获取光标右侧的字符
            try:
                next_char = self.text_widget.get(cursor_pos, f"{cursor_pos}+1c")
            except:
                next_char = ""
            
            # 特殊处理引号：如果光标在单词中间，不自动配对
            if left_symbol in ['"', "'", '`']:
                # 获取光标左侧的字符
                try:
                    prev_char = self.text_widget.get(f"{cursor_pos}-1c", cursor_pos)
                except:
                    prev_char = ""
                
                # 如果左侧是字母数字或下划线，且右侧也是，则不自动配对
                if (prev_char.isalnum() or prev_char == '_') and (next_char.isalnum() or next_char == '_'):
                    return None
            
            # 插入左符号
            self.text_widget.insert(cursor_pos, left_symbol)
            
            # 如果右侧不是相同的右符号，则插入右符号
            if next_char != right_symbol:
                new_cursor_pos = self.text_widget.index(tk.INSERT)
                self.text_widget.insert(new_cursor_pos, right_symbol)
                # 将光标移动到两个符号之间
                self.text_widget.mark_set(tk.INSERT, new_cursor_pos)
            
            return "break"
            
        except Exception as e:
            deBug.info(f"符号配对插入错误: {e}")
            return None
    
    def handle_right_symbol(self, right_symbol):
        """处理右符号输入"""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            
            # 获取光标右侧的字符
            try:
                next_char = self.text_widget.get(cursor_pos, f"{cursor_pos}+1c")
            except:
                next_char = ""
            
            # 如果右侧就是要输入的右符号，则跳过（移动光标）
            if next_char == right_symbol:
                new_pos = f"{cursor_pos}+1c"
                self.text_widget.mark_set(tk.INSERT, new_pos)
                return "break"
            
            # 否则正常插入
            return None
            
        except Exception as e:
            deBug.info(f"右符号处理错误: {e}")
            return None
    
    def is_inside_string(self, pos):
        """检查位置是否在字符串内部"""
        try:
            # 获取当前行内容
            line_num = int(pos.split('.')[0])
            col_num = int(pos.split('.')[1])
            line_start = f"{line_num}.0"
            line_content = self.text_widget.get(line_start, f"{line_num}.end")
            
            # 简单的字符串检测：计算引号数量
            single_quotes = 0
            double_quotes = 0
            
            for i, char in enumerate(line_content[:col_num]):
                if char == "'" and (i == 0 or line_content[i-1] != '\\'):
                    single_quotes += 1
                elif char == '"' and (i == 0 or line_content[i-1] != '\\'):
                    double_quotes += 1
            
            # 如果引号数量为奇数，说明在字符串内部
            return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)
            
        except:
            return False
    
    def handle_backspace_in_pair(self, event):
        """处理在符号配对中的退格键"""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            
            # 获取光标左侧和右侧的字符
            try:
                left_char = self.text_widget.get(f"{cursor_pos}-1c", cursor_pos)
                right_char = self.text_widget.get(cursor_pos, f"{cursor_pos}+1c")
            except:
                return None
            
            # 检查是否是配对的符号
            if left_char in self.symbol_pairs and self.symbol_pairs[left_char] == right_char:
                # 删除左符号
                self.text_widget.delete(f"{cursor_pos}-1c", cursor_pos)
                # 删除右符号
                new_cursor_pos = self.text_widget.index(tk.INSERT)
                self.text_widget.delete(new_cursor_pos, f"{new_cursor_pos}+1c")
                return "break"
            
            return None
            
        except Exception as e:
            print(f"退格处理错误: {e}")
            return None
