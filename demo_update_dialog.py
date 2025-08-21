#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示更新对话框功能
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.update_dialog import UpdateDialog

def demo_with_exe_link():
    """演示带exe链接的更新对话框"""
    print("演示：带exe链接的更新对话框（三个按钮）")
    
    # 模拟更新数据（包含exe链接）
    update_data = {
        "level": "1.2.0",
        "update_time": "2025-01-20",
        "update_content": [
            "新增功能：三按钮更新对话框",
            "新增功能：支持exe安装包下载",
            "新增功能：优化用户界面体验",
            "修复bug：解决对话框显示问题",
            "优化：提升程序启动速度",
            "新增功能：支持自定义主题",
            "修复bug：解决内存泄漏问题"
        ],
        "line": "https://github.com/RuiHe-cell/TkTool/releases/download/v1.2.0/TkTool-v1.2.0.exe"
    }
    
    # 模拟配置
    config = {
        "github_page_url": "https://github.com/RuiHe-cell/TkTool"
    }
    
    root = tk.Tk()
    root.title("TkTool 更新对话框演示")
    root.geometry("300x200")
    
    # 创建演示按钮
    demo_frame = tk.Frame(root, padx=20, pady=20)
    demo_frame.pack(fill=tk.BOTH, expand=True)
    
    title_label = tk.Label(
        demo_frame, 
        text="TkTool 更新对话框演示",
        font=('Arial', 14, 'bold')
    )
    title_label.pack(pady=(0, 20))
    
    def show_with_exe():
        dialog = UpdateDialog(root, update_data, config)
        result = dialog.show()
        messagebox.showinfo("结果", f"用户操作: {result}")
    
    def show_without_exe():
        update_data_no_exe = update_data.copy()
        update_data_no_exe["line"] = ""  # 清空exe链接
        update_data_no_exe["level"] = "1.1.5"
        dialog = UpdateDialog(root, update_data_no_exe, config)
        result = dialog.show()
        messagebox.showinfo("结果", f"用户操作: {result}")
    
    btn1 = tk.Button(
        demo_frame,
        text="📦 演示三按钮对话框\n（有exe链接）",
        command=show_with_exe,
        height=2,
        font=('Arial', 10)
    )
    btn1.pack(fill=tk.X, pady=(0, 10))
    
    btn2 = tk.Button(
        demo_frame,
        text="🔗 演示两按钮对话框\n（无exe链接）",
        command=show_without_exe,
        height=2,
        font=('Arial', 10)
    )
    btn2.pack(fill=tk.X, pady=(0, 10))
    
    info_label = tk.Label(
        demo_frame,
        text="点击按钮查看不同的更新对话框",
        font=('Arial', 9),
        fg='gray'
    )
    info_label.pack(pady=(10, 0))
    
    root.mainloop()

def main():
    """主函数"""
    print("=== TkTool 更新对话框演示程序 ===")
    print("启动演示界面...")
    
    try:
        demo_with_exe_link()
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()