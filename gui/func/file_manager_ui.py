#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理UI模块
功能：处理文件相关的UI操作，包括目录浏览和文件删除
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import datetime
import glob


class FileManagerUI:
    """文件管理UI类"""
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
    
    def browse_output_dir(self, current_dir_var):
        """浏览输出目录"""
        directory = filedialog.askdirectory(initialdir=current_dir_var.get())
        if directory:
            current_dir_var.set(directory)
            return directory
        return None
    
    def delete_zip_files(self, output_dir_var, delete_time_var):
        """删除指定时间范围内的zip文件"""
        output_dir = output_dir_var.get().strip()
        if not output_dir:
            messagebox.showwarning("警告", "请先选择输出目录")
            return

        if not os.path.exists(output_dir):
            messagebox.showerror("错误", "输出目录不存在")
            return

        # 获取时间范围
        time_range = delete_time_var.get()
        now = datetime.datetime.now()

        # 计算时间阈值
        if time_range == "一小时内":
            threshold = now - datetime.timedelta(hours=1)
        elif time_range == "一天内":
            threshold = now - datetime.timedelta(days=1)
        elif time_range == "一周内":
            threshold = now - datetime.timedelta(weeks=1)
        elif time_range == "一月内":
            threshold = now - datetime.timedelta(days=30)
        elif time_range == "一年内":
            threshold = now - datetime.timedelta(days=365)
        else:
            threshold = now - datetime.timedelta(days=1)  # 默认一天内

        try:
            # 查找zip文件
            zip_pattern = os.path.join(output_dir, "*.zip")
            zip_files = glob.glob(zip_pattern)

            # 筛选出符合时间条件的文件
            files_to_delete = []
            for zip_file in zip_files:
                # 获取文件修改时间
                file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(zip_file))

                # 如果文件在指定时间范围内，则加入删除列表
                if file_mtime >= threshold:
                    files_to_delete.append(zip_file)

            if not files_to_delete:
                messagebox.showinfo("提示", f"在{time_range}没有找到需要删除的zip文件")
                return

            # 显示确认对话框
            file_names = [os.path.basename(f) for f in files_to_delete]
            confirm_msg = f"确定要删除以下 {len(files_to_delete)} 个zip文件吗？\n\n" + "\n".join(file_names)

            if not messagebox.askyesno("确认删除", confirm_msg):
                return

            # 执行删除操作
            deleted_files = []
            failed_files = []

            for zip_file in files_to_delete:
                try:
                    os.remove(zip_file)
                    deleted_files.append(os.path.basename(zip_file))
                except OSError as e:
                    failed_files.append(f"{os.path.basename(zip_file)}: {str(e)}")

            # 显示结果
            if deleted_files:
                success_msg = f"成功删除 {len(deleted_files)} 个文件:\n" + "\n".join(deleted_files)
                if failed_files:
                    success_msg += f"\n\n删除失败 {len(failed_files)} 个文件:\n" + "\n".join(failed_files)
                messagebox.showinfo("删除完成", success_msg)
            elif failed_files:
                messagebox.showerror("删除失败", f"所有文件删除失败:\n" + "\n".join(failed_files))

        except Exception as e:
            messagebox.showerror("错误", f"删除操作失败: {str(e)}")
    
    def create_file_management_widgets(self, parent_frame, output_dir_var, delete_time_var):
        """创建文件管理相关的UI组件"""
        # 输出目录
        tk.Label(parent_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        output_dir_entry = tk.Entry(parent_frame, textvariable=output_dir_var, width=30)
        output_dir_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
    
        browse_btn = tk.Button(parent_frame, text="浏览", 
                              command=lambda: self.browse_output_dir(output_dir_var))
        browse_btn.grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        
        # 删除按钮和时间选择下拉菜单
        delete_btn = tk.Button(parent_frame, text="删除", 
                              command=lambda: self.delete_zip_files(output_dir_var, delete_time_var))
        delete_btn.grid(row=1, column=4, padx=(5, 0), pady=(5, 0))
        
        # 时间范围下拉菜单
        time_options = ["一小时内", "一天内", "一周内", "一月内", "一年内"]
        from tkinter import ttk
        time_combo = ttk.Combobox(parent_frame, textvariable=delete_time_var, values=time_options, 
                                 state="readonly", width=8)
        time_combo.grid(row=1, column=5, padx=(5, 0), pady=(5, 0))
        
        return {
            'output_dir_entry': output_dir_entry,
            'browse_btn': browse_btn,
            'delete_btn': delete_btn,
            'time_combo': time_combo
        }
