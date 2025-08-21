#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据生成器 - 主界面
功能：提供图形化界面，简化测试数据生成操作
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import threading

# 添加父目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from core.update_checker import UpdateChecker


def main():
    """主函数"""
    try:
        print("启动数据生成器...")

        # 启动更新检查（在后台线程中）
        try:
            update_checker = UpdateChecker()

            # 延迟2秒后检查更新，避免影响程序启动速度
            def delayed_update_check():
                import time
                time.sleep(2)
                update_checker.start_update_check()

            update_thread = threading.Thread(target=delayed_update_check, daemon=True)
            update_thread.start()
            print("更新检查已启动")
        except Exception as e:
            print(f"启动更新检查失败: {e}")

        root = tk.Tk()
        app = MainWindow(root)

        # 在主窗口中添加更新检查菜单项
        try:
            if hasattr(app, 'menubar'):
                # 创建帮助菜单
                help_menu = tk.Menu(app.menubar, tearoff=0)
                help_menu.add_command(label="检查更新", command=lambda: update_checker.manual_check_update())
                help_menu.add_separator()
                help_menu.add_command(label="版本更新工具", command=open_version_updater)
                help_menu.add_command(label="配置GitHub", command=open_config_setup)
                app.menubar.add_cascade(label="帮助", menu=help_menu)
        except Exception as e:
            print(f"添加更新菜单失败: {e}")

        print("界面初始化完成")
        root.mainloop()
        print("程序正常退出")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()


def open_version_updater():
    """打开版本更新工具"""
    try:
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "update_version.py")
        subprocess.Popen([sys.executable, script_path, "--interactive"])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开版本更新工具: {e}")


def open_config_setup():
    """打开配置设置"""
    try:
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "setup_config.py")
        subprocess.Popen([sys.executable, script_path, "--interactive"])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开配置设置: {e}")


if __name__ == "__main__":
    main()
