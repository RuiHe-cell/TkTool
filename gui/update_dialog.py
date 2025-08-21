import tkinter as tk
from tkinter import ttk
import webbrowser
import os

class UpdateDialog:
    def __init__(self, parent, update_data, config):
        self.parent = parent
        self.update_data = update_data
        self.config = config
        self.result = None
        self.dialog = None
        
    def show(self):
        """显示更新对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("发现更新")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # 设置对话框居中
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=f"🎉 发现新版本 {self.update_data['level']}",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 更新时间
        time_label = ttk.Label(
            main_frame,
            text=f"📅 更新时间: {self.update_data.get('update_time', '未知')}",
            font=('Arial', 10)
        )
        time_label.pack(pady=(0, 15))
        
        # 更新内容标题
        content_title = ttk.Label(
            main_frame,
            text="📋 更新内容:",
            font=('Arial', 11, 'bold')
        )
        content_title.pack(anchor='w', pady=(0, 5))
        
        # 更新内容列表框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建滚动文本框显示更新内容
        text_widget = tk.Text(
            content_frame,
            height=8,
            wrap=tk.WORD,
            font=('Arial', 9),
            bg='#f8f9fa',
            relief='solid',
            borderwidth=1,
            state='disabled'
        )
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # 填充更新内容
        text_widget.config(state='normal')
        for i, content in enumerate(self.update_data.get('update_content', []), 1):
            text_widget.insert(tk.END, f"  {i}. {content}\n")
        text_widget.config(state='disabled')
        
        # 布局文本框和滚动条
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建按钮
        self.create_buttons(button_frame)
        
        # 设置对话框关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 居中显示
        self.center_dialog()
        
        # 等待对话框关闭
        self.dialog.wait_window()
        
        return self.result
    
    def create_buttons(self, parent):
        """创建按钮"""
        # 检查是否有exe下载链接
        exe_link = self.update_data.get('line', '').strip()
        
        if exe_link:  # 如果有exe链接，显示三个按钮
            # exe下载按钮
            exe_btn = ttk.Button(
                parent,
                text="📦 下载安装包",
                command=self.open_exe_link,
                style='Accent.TButton'
            )
            exe_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # GitHub按钮
            github_btn = ttk.Button(
                parent,
                text="🔗 查看GitHub",
                command=self.open_github
            )
            github_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # 关闭按钮
            close_btn = ttk.Button(
                parent,
                text="❌ 关闭",
                command=self.on_close
            )
            close_btn.pack(side=tk.RIGHT)
            
        else:  # 如果没有exe链接，显示两个按钮
            # GitHub按钮
            github_btn = ttk.Button(
                parent,
                text="🔗 查看GitHub",
                command=self.open_github,
                style='Accent.TButton'
            )
            github_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # 关闭按钮
            close_btn = ttk.Button(
                parent,
                text="❌ 关闭",
                command=self.on_close
            )
            close_btn.pack(side=tk.RIGHT)
    
    def open_exe_link(self):
        """打开exe下载链接"""
        exe_link = self.update_data.get('line', '').strip()
        if exe_link:
            try:
                webbrowser.open(exe_link)
                self.result = 'exe_download'
            except Exception as e:
                print(f"打开exe链接失败: {e}")
    
    def open_github(self):
        """打开GitHub页面"""
        try:
            webbrowser.open(self.config['github_page_url'])
            self.result = 'github_opened'
        except Exception as e:
            print(f"打开GitHub页面失败: {e}")
    
    def on_close(self):
        """关闭对话框"""
        self.result = 'closed'
        if self.dialog:
            self.dialog.destroy()
    
    def center_dialog(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        
        # 获取对话框尺寸
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # 设置位置
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


def show_update_dialog(parent, update_data, config):
    """显示更新对话框的便捷函数"""
    dialog = UpdateDialog(parent, update_data, config)
    return dialog.show()