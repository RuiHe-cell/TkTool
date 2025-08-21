import tkinter as tk
import re
import json
import os


class SyntaxHighlighter:
    """优化的语法高亮器类"""
    
    def __init__(self, text_widget, language="python"):
        self.text_widget = text_widget
        self.language = language
        self.config = self.load_syntax_config()
        self.setup_tags()
        
        # 性能优化相关
        self.highlight_job = None  # 防抖任务ID
        self.last_content_hash = None  # 内容哈希，避免重复高亮
        self.max_highlight_lines = 1000  # 最大高亮行数
        self.debounce_delay = 300  # 防抖延迟（毫秒）
        
    def load_syntax_config(self):
        """加载语法高亮配置"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "syntax_highlight.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self):
        """获取默认语法高亮配置"""
        return {
            "python": {
                "keywords": {
                    "words": ["def", "class", "if", "else", "elif", "for", "while", "try", "except", "import", "from", "return"],
                    "color": "#0000FF",
                    "bold": True
                },
                "strings": {
                    "patterns": ["\".*?\"", "'.*?'"],
                    "color": "#008000",
                    "bold": False
                },
                "comments": {
                    "patterns": ["#.*$"],
                    "color": "#808080",
                    "bold": False,
                    "italic": True
                }
            }
        }
    
    def setup_tags(self):
        """设置文本标签样式"""
        if self.language not in self.config:
            return
            
        lang_config = self.config[self.language]
        
        for category, settings in lang_config.items():
            font_config = ["Consolas", 11]
            
            if settings.get("bold", False):
                font_config.append("bold")
            if settings.get("italic", False):
                font_config.append("italic")
                
            self.text_widget.tag_config(
                category,
                foreground=settings.get("color", "#000000"),
                font=tuple(font_config)
            )
    
    def highlight_syntax_debounced(self):
        """防抖的语法高亮"""
        # 取消之前的任务
        if self.highlight_job:
            self.text_widget.after_cancel(self.highlight_job)
        
        # 设置新的延迟任务
        self.highlight_job = self.text_widget.after(self.debounce_delay, self.highlight_syntax)
    
    def highlight_syntax(self):
        """执行语法高亮（优化版本）"""
        if self.language not in self.config:
            return
        
        try:
            content = self.text_widget.get(1.0, tk.END)
            
            # 检查内容是否变化
            content_hash = hash(content)
            if content_hash == self.last_content_hash:
                return
            self.last_content_hash = content_hash
            
            # 检查文本长度，如果太长则只高亮可见部分
            lines = content.split('\n')
            if len(lines) > self.max_highlight_lines:
                self.highlight_visible_area()
                return
            
            # 清除所有现有标签
            self.clear_highlights()
            
            # 重新设置标签
            self.setup_tags()
            
            lang_config = self.config[self.language]
            
            # 分批处理以避免UI冻结
            self.highlight_batch(lang_config, content, 0)
            
        except Exception as e:
            print(f"语法高亮错误: {e}")
    
    def highlight_visible_area(self):
        """只高亮可见区域"""
        try:
            # 获取可见区域
            first_visible = self.text_widget.index("@0,0")
            last_visible = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
            
            first_line = int(first_visible.split('.')[0])
            last_line = int(last_visible.split('.')[0])
            
            # 扩展范围以包含上下文
            start_line = max(1, first_line - 50)
            end_line = min(int(self.text_widget.index(tk.END).split('.')[0]), last_line + 50)
            
            # 获取可见区域的内容
            start_pos = f"{start_line}.0"
            end_pos = f"{end_line}.end"
            visible_content = self.text_widget.get(start_pos, end_pos)
            
            # 清除可见区域的高亮
            self.clear_highlights(start_pos, end_pos)
            
            # 高亮可见区域
            lang_config = self.config[self.language]
            self.highlight_content_range(lang_config, visible_content, start_line)
            
        except Exception as e:
            print(f"可见区域高亮错误: {e}")
    
    def highlight_batch(self, lang_config, content, category_index):
        """分批处理高亮以避免UI冻结"""
        categories = list(lang_config.keys())
        if category_index >= len(categories):
            return
        
        category = categories[category_index]
        settings = lang_config[category]
        
        # 处理当前类别
        if "words" in settings:
            for word in settings["words"]:
                self.highlight_word(word, category, content)
        
        if "patterns" in settings:
            for pattern in settings["patterns"]:
                self.highlight_pattern(pattern, category, content)
        
        # 调度下一个类别
        if category_index + 1 < len(categories):
            self.text_widget.after_idle(lambda: self.highlight_batch(lang_config, content, category_index + 1))
    
    def highlight_content_range(self, lang_config, content, start_line_num):
        """高亮指定范围的内容（修复注释优先级问题）"""
        # 首先处理注释，并记录注释的位置
        comment_ranges = []
        if "comments" in lang_config:
            settings = lang_config["comments"]
            if "patterns" in settings:
                for pattern in settings["patterns"]:
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        match_line = content[:match.start()].count('\n')
                        actual_line = start_line_num + match_line
                        start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
                        end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
                        
                        start_pos = f"{actual_line}.{start_col}"
                        end_pos = f"{actual_line}.{end_col}"
                        
                        # 记录注释范围
                        comment_ranges.append((match.start(), match.end()))
                        
                        try:
                            self.text_widget.tag_add("comments", start_pos, end_pos)
                        except tk.TclError:
                            continue
        
        # 处理其他语法元素，但跳过注释区域
        for category, settings in lang_config.items():
            if category == "comments":  # 跳过注释，已经处理过了
                continue
                
            if "words" in settings:
                for word in settings["words"]:
                    self.highlight_word_in_range_skip_comments(word, category, content, start_line_num, comment_ranges)
            
            if "patterns" in settings:
                for pattern in settings["patterns"]:
                    self.highlight_pattern_in_range_skip_comments(pattern, category, content, start_line_num, comment_ranges)
    
    def clear_highlights(self, start_pos="1.0", end_pos=None):
        """清除指定范围的高亮"""
        if end_pos is None:
            end_pos = tk.END
        
        for tag in self.text_widget.tag_names():
            if tag not in ["sel", "current"]:
                # 获取标签范围
                ranges = self.text_widget.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    tag_start = ranges[i]
                    tag_end = ranges[i + 1]
                    
                    # 检查是否在清除范围内
                    if (self.text_widget.compare(tag_start, ">=", start_pos) and 
                        self.text_widget.compare(tag_end, "<=", end_pos)):
                        self.text_widget.tag_remove(tag, tag_start, tag_end)
    
    def highlight_word(self, word, tag, content=None):
        """高亮单词（优化版本）"""
        if content is None:
            content = self.text_widget.get(1.0, tk.END)
        
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # 限制匹配数量以提高性能
        matches = list(re.finditer(pattern, content))
        if len(matches) > 500:  # 如果匹配太多，只处理前500个
            matches = matches[:500]
        
        for match in matches:
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            start_pos = f"{start_line}.{start_col}"
            end_pos = f"{end_line}.{end_col}"
            
            try:
                self.text_widget.tag_add(tag, start_pos, end_pos)
            except tk.TclError:
                continue  # 忽略无效位置
    
    def highlight_word_in_range(self, word, tag, content, start_line_num):
        """在指定范围内高亮单词"""
        pattern = r'\b' + re.escape(word) + r'\b'
        
        for match in re.finditer(pattern, content):
            match_line = content[:match.start()].count('\n')
            actual_line = start_line_num + match_line
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            start_pos = f"{actual_line}.{start_col}"
            end_pos = f"{actual_line}.{end_col}"
            
            try:
                self.text_widget.tag_add(tag, start_pos, end_pos)
            except tk.TclError:
                continue
    
    def highlight_pattern(self, pattern, tag, content=None):
        """高亮正则表达式模式（优化版本）"""
        if content is None:
            content = self.text_widget.get(1.0, tk.END)
        
        try:
            # 限制匹配数量
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if len(matches) > 200:  # 模式匹配限制更严格
                matches = matches[:200]
            
            for match in matches:
                start_line = content[:match.start()].count('\n') + 1
                start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
                end_line = content[:match.end()].count('\n') + 1
                end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                start_pos = f"{start_line}.{start_col}"
                end_pos = f"{end_line}.{end_col}"
                
                try:
                    self.text_widget.tag_add(tag, start_pos, end_pos)
                except tk.TclError:
                    continue
        except re.error:
            print(f"正则表达式错误: {pattern}")
    
    def highlight_pattern_in_range(self, pattern, tag, content, start_line_num):
        """在指定范围内高亮模式"""
        try:
            for match in re.finditer(pattern, content, re.MULTILINE):
                match_line = content[:match.start()].count('\n')
                actual_line = start_line_num + match_line
                start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
                end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                start_pos = f"{actual_line}.{start_col}"
                end_pos = f"{actual_line}.{end_col}"
                
                try:
                    self.text_widget.tag_add(tag, start_pos, end_pos)
                except tk.TclError:
                    continue
        except re.error:
            print(f"正则表达式错误: {pattern}")
    
    def is_in_comment(self, start_pos, end_pos, comment_ranges):
        """检查位置是否在注释范围内"""
        for comment_start, comment_end in comment_ranges:
            if start_pos >= comment_start and end_pos <= comment_end:
                return True
        return False
    
    def highlight_pattern_in_range_skip_comments(self, pattern, tag, content, start_line_num, comment_ranges):
        """在指定范围内高亮模式，但跳过注释区域"""
        try:
            for match in re.finditer(pattern, content, re.MULTILINE):
                # 检查是否在注释中
                if self.is_in_comment(match.start(), match.end(), comment_ranges):
                    continue
                    
                match_line = content[:match.start()].count('\n')
                actual_line = start_line_num + match_line
                start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
                end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
                
                start_pos = f"{actual_line}.{start_col}"
                end_pos = f"{actual_line}.{end_col}"
                
                try:
                    self.text_widget.tag_add(tag, start_pos, end_pos)
                except tk.TclError:
                    continue
        except re.error:
            print(f"正则表达式错误: {pattern}")
    
    def highlight_word_in_range_skip_comments(self, word, tag, content, start_line_num, comment_ranges):
        """在指定范围内高亮单词，但跳过注释区域"""
        pattern = r'\b' + re.escape(word) + r'\b'
        self.highlight_pattern_in_range_skip_comments(pattern, tag, content, start_line_num, comment_ranges)
    
    def set_performance_settings(self, max_lines=1000, debounce_delay=300):
        """设置性能参数"""
        self.max_highlight_lines = max_lines
        self.debounce_delay = debounce_delay
        