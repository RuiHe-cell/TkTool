import tkinter as tk
from .deBug import debug


class EditorEventHandler:
    """编辑器事件处理器类"""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def handle_tab(self, event):
        """处理Tab键事件"""
        debug("Tab键事件触发", level=2)
        try:
            if hasattr(self.text_widget,
                       'autocomplete') and self.text_widget.autocomplete and self.text_widget.autocomplete.completion_window:
                debug("补全窗口打开，接受补全", level=2)
                self.text_widget.autocomplete.accept_completion()
                return "break"

            debug("开始处理Tab缩进", level=2)

            # 获取当前选择
            try:
                sel_start = self.text_widget.index(tk.SEL_FIRST)
                sel_end = self.text_widget.index(tk.SEL_LAST)
                # 有选择文本，缩进选择的行
                self.indent_selection()
            except tk.TclError:
                # 没有选择文本，插入Tab
                cursor_pos = self.text_widget.index(tk.INSERT)
                self.text_widget.insert(cursor_pos, "    ")

            return "break"
        except Exception as e:
            debug(f"Tab处理错误: {e}", level=0)
            return "break"

    def indent_selection(self):
        """缩进选中的文本"""
        try:
            sel_start = self.text_widget.index(tk.SEL_FIRST)
            sel_end = self.text_widget.index(tk.SEL_LAST)

            start_line = int(sel_start.split('.')[0])
            end_line = int(sel_end.split('.')[0])

            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                self.text_widget.insert(line_start, "    ")

        except tk.TclError:
            pass

    def handle_return(self, event):
        """处理回车键事件"""
        debug("回车键事件触发", level=2)
        try:
            if hasattr(self.text_widget,
                       'autocomplete') and self.text_widget.autocomplete and self.text_widget.autocomplete.completion_window:
                debug("补全窗口打开，接受补全并阻止默认回车", level=2)
                self.text_widget.autocomplete.accept_completion()
                return "break"

            debug("开始处理自动缩进", level=2)

            # 获取当前行
            cursor_pos = self.text_widget.index(tk.INSERT)
            line_num = int(cursor_pos.split('.')[0])
            current_line = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")

            # 计算当前行的缩进
            indent = ""
            for char in current_line:
                if char in [' ', '\t']:
                    indent += char
                else:
                    break

            # 如果当前行以冒号结尾，增加一级缩进
            if current_line.rstrip().endswith(':'):
                indent += "    "

            # 插入换行和缩进
            self.text_widget.insert(cursor_pos, "\n" + indent)

            return "break"
        except Exception as e:
            debug(f"回车处理错误: {e}", level=1)
            return "break"

    def toggle_comment(self, event):
        """切换注释"""
        try:
            # 获取选中的文本范围
            try:
                sel_start = self.text_widget.index(tk.SEL_FIRST)
                sel_end = self.text_widget.index(tk.SEL_LAST)
                start_line = int(sel_start.split('.')[0])
                end_line = int(sel_end.split('.')[0])
            except tk.TclError:
                # 没有选中文本，处理当前行
                cursor_pos = self.text_widget.index(tk.INSERT)
                start_line = end_line = int(cursor_pos.split('.')[0])

            # 检查是否所有行都已注释
            all_commented = True
            for line_num in range(start_line, end_line + 1):
                line_content = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")
                stripped = line_content.lstrip()
                if stripped and not stripped.startswith('#'):
                    all_commented = False
                    break

            # 切换注释
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                line_content = self.text_widget.get(line_start, line_end)

                if all_commented:
                    # 取消注释
                    if line_content.lstrip().startswith('#'):
                        # 找到#的位置
                        hash_pos = line_content.find('#')
                        # 删除#和可能的空格
                        new_content = line_content[:hash_pos] + line_content[hash_pos + 1:].lstrip(' ', 1)
                        self.text_widget.delete(line_start, line_end)
                        self.text_widget.insert(line_start, new_content)
                else:
                    # 添加注释
                    if line_content.strip():  # 只对非空行添加注释
                        # 找到第一个非空字符的位置
                        first_char_pos = len(line_content) - len(line_content.lstrip())
                        comment_pos = f"{line_num}.{first_char_pos}"
                        self.text_widget.insert(comment_pos, "# ")

            return "break"
        except Exception as e:
            debug(f"注释切换错误: {e}", level=1)
            return "break"

    def handle_shift_tab(self, event):
        """处理Shift+Tab键事件（减少缩进）"""
        try:
            # 获取选中的文本范围
            try:
                sel_start = self.text_widget.index(tk.SEL_FIRST)
                sel_end = self.text_widget.index(tk.SEL_LAST)
                start_line = int(sel_start.split('.')[0])
                end_line = int(sel_end.split('.')[0])
            except tk.TclError:
                # 没有选中文本，处理当前行
                cursor_pos = self.text_widget.index(tk.INSERT)
                start_line = end_line = int(cursor_pos.split('.')[0])

            # 对每一行减少缩进
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                line_content = self.text_widget.get(line_start, f"{line_num}.end")

                # 移除行首的4个空格或1个tab
                if line_content.startswith("    "):
                    self.text_widget.delete(line_start, f"{line_num}.4")
                elif line_content.startswith("\t"):
                    self.text_widget.delete(line_start, f"{line_num}.1")

            return "break"
        except Exception as e:
            debug(f"Shift+Tab处理错误: {e}", level=1)
            return "break"

    def handle_backspace(self, event):
        """处理退格键事件"""
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line, col = map(int, cursor_pos.split('.'))

            # 如果光标在行首，正常处理
            if col == 0:
                return None

            # 获取当前行内容
            line_content = self.text_widget.get(f"{line}.0", cursor_pos)

            # 如果光标前面都是空格，且是4的倍数，删除4个空格
            if line_content and all(c == ' ' for c in line_content) and len(line_content) % 4 == 0:
                # 删除4个空格
                delete_start = f"{line}.{col - 4}"
                self.text_widget.delete(delete_start, cursor_pos)
                return "break"

            return None
        except Exception as e:
            debug(f"退格键处理错误: {e}", level=1)
            return None

    def handle_auto_complete(self, event):
        """处理自动补全（括号、引号等）"""
        char = event.char
        cursor_pos = self.text_widget.index(tk.INSERT)

        # 自动补全配对字符
        pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }

        if char in pairs:
            # 插入配对字符
            self.text_widget.insert(cursor_pos, pairs[char])
            # 将光标移回到配对字符之间
            self.text_widget.mark_set(tk.INSERT, cursor_pos)
            return "break"

        return None

    def handle_undo(self, event):
        """处理撤销操作"""
        try:
            self.text_widget.edit_undo()
            return "break"
        except tk.TclError:
            return "break"

    def handle_redo(self, event):
        """处理重做操作"""
        try:
            self.text_widget.edit_redo()
            return "break"
        except tk.TclError:
            return "break"

    def handle_home(self, event):
        """处理Home键事件 - 智能跳转到行首非空字符"""
        debug("Home键事件触发", level=2)
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line_num = int(cursor_pos.split('.')[0])

            # 获取当前行内容
            current_line = self.text_widget.get(f"{line_num}.0", f"{line_num}.end")

            # 找到第一个非空字符的位置
            first_non_space = 0
            for i, char in enumerate(current_line):
                if char not in [' ', '\t']:
                    first_non_space = i
                    break
            else:
                # 如果整行都是空格，跳转到行首
                first_non_space = 0

            # 获取当前光标的列位置
            current_col = int(cursor_pos.split('.')[1])

            # 如果光标已经在第一个非空字符位置，或者在非空字符之前，则跳转到行首
            if current_col <= first_non_space:
                new_pos = f"{line_num}.0"
            else:
                # 否则跳转到第一个非空字符
                new_pos = f"{line_num}.{first_non_space}"

            self.text_widget.mark_set(tk.INSERT, new_pos)
            return "break"

        except Exception as e:
            debug(f"Home键处理错误: {e}", level=1)
            return "break"

    def handle_end(self, event):
        """处理End键事件 - 跳转到行尾"""
        debug("End键事件触发", level=2)
        try:
            cursor_pos = self.text_widget.index(tk.INSERT)
            line_num = int(cursor_pos.split('.')[0])

            # 跳转到行尾
            new_pos = f"{line_num}.end"
            self.text_widget.mark_set(tk.INSERT, new_pos)
            return "break"

        except Exception as e:
            debug(f"End键处理错误: {e}", level=1)
            return "break"
