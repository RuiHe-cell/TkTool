#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本更新脚本 - 简化版本更新和自动上传流程

使用方法:
1. 直接运行: python update_version.py
2. 指定版本: python update_version.py --version 1.0.1
3. 指定更新内容: python update_version.py --content "修复bug" "新增功能"
"""

import os
import json
import sys
import argparse
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# 添加scripts目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_upload import GitAutoUploader

class VersionUpdater:
    def __init__(self, update_file="INFO/update.json"):
        self.update_file = update_file
        self.uploader = GitAutoUploader()
        
    def load_current_version(self):
        """加载当前版本信息"""
        try:
            if os.path.exists(self.update_file):
                with open(self.update_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "level": "1.0.0",
                    "update_time": datetime.now().strftime("%Y-%m-%d"),
                    "update_content": [],
                    "line": ""
                }
        except Exception as e:
            print(f"加载版本信息失败: {e}")
            return None
    
    def increment_version(self, current_version, increment_type="patch"):
        """自动递增版本号"""
        try:
            parts = list(map(int, current_version.split('.')))
            
            if increment_type == "major":
                parts[0] += 1
                parts[1] = 0
                parts[2] = 0
            elif increment_type == "minor":
                parts[1] += 1
                parts[2] = 0
            else:  # patch
                parts[2] += 1
            
            return '.'.join(map(str, parts))
        except:
            return current_version
    
    def update_version_info(self, new_version=None, update_content=None, increment_type="patch"):
        """更新版本信息"""
        current_data = self.load_current_version()
        if current_data is None:
            return False, "无法加载当前版本信息"
        
        # 确定新版本号
        if new_version is None:
            new_version = self.increment_version(current_data['level'], increment_type)
        
        # 更新数据
        current_data['level'] = new_version
        current_data['update_time'] = datetime.now().strftime("%Y-%m-%d")
        
        if update_content:
            if isinstance(update_content, str):
                update_content = [update_content]
            current_data['update_content'] = update_content
        
        # 保存文件
        try:
            os.makedirs(os.path.dirname(self.update_file), exist_ok=True)
            with open(self.update_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=4, ensure_ascii=False)
            
            return True, f"版本已更新到 {new_version}"
        except Exception as e:
            return False, f"保存版本信息失败: {e}"
    
    def interactive_update(self):
        """交互式版本更新"""
        root = tk.Tk()
        root.title("版本更新")
        root.geometry("500x400")
        root.resizable(False, False)
        
        # 居中显示
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (500 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"500x400+{x}+{y}")
        
        # 加载当前版本
        current_data = self.load_current_version()
        if current_data is None:
            messagebox.showerror("错误", "无法加载当前版本信息")
            root.destroy()
            return
        
        # 创建界面
        tk.Label(root, text="版本更新工具", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # 当前版本信息
        info_frame = tk.Frame(root)
        info_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(info_frame, text=f"当前版本: {current_data['level']}", font=('Arial', 12)).pack(anchor='w')
        tk.Label(info_frame, text=f"更新时间: {current_data['update_time']}", font=('Arial', 12)).pack(anchor='w')
        
        # 新版本输入
        version_frame = tk.Frame(root)
        version_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(version_frame, text="新版本号:", font=('Arial', 12)).pack(anchor='w')
        version_var = tk.StringVar(value=self.increment_version(current_data['level']))
        version_entry = tk.Entry(version_frame, textvariable=version_var, font=('Arial', 11))
        version_entry.pack(fill='x', pady=5)
        
        # 更新内容输入
        content_frame = tk.Frame(root)
        content_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(content_frame, text="更新内容 (每行一项):", font=('Arial', 12)).pack(anchor='w')
        content_text = tk.Text(content_frame, height=8, font=('Arial', 10))
        content_text.pack(fill='both', expand=True, pady=5)
        
        # 预填充当前更新内容
        if current_data.get('update_content'):
            content_text.insert('1.0', '\n'.join(current_data['update_content']))
        
        # 按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        def update_and_upload():
            new_version = version_var.get().strip()
            content_lines = [line.strip() for line in content_text.get('1.0', 'end').strip().split('\n') if line.strip()]
            
            if not new_version:
                messagebox.showerror("错误", "请输入版本号")
                return
            
            # 更新版本信息
            success, message = self.update_version_info(new_version, content_lines)
            if not success:
                messagebox.showerror("错误", message)
                return
            
            # 自动上传
            commit_message = f"更新版本到 {new_version}"
            results = self.uploader.auto_upload(
                files=[self.update_file],
                commit_message=commit_message,
                show_gui=False
            )
            
            # 显示结果
            all_success = all(result[1] for result in results)
            if all_success:
                messagebox.showinfo("成功", f"版本已更新到 {new_version} 并成功上传到GitHub！")
                root.destroy()
            else:
                error_msg = "\n".join([f"{step}: {detail}" for step, success, detail in results if not success])
                messagebox.showerror("上传失败", f"版本更新成功，但上传失败：\n{error_msg}")
        
        def update_only():
            new_version = version_var.get().strip()
            content_lines = [line.strip() for line in content_text.get('1.0', 'end').strip().split('\n') if line.strip()]
            
            if not new_version:
                messagebox.showerror("错误", "请输入版本号")
                return
            
            success, message = self.update_version_info(new_version, content_lines)
            if success:
                messagebox.showinfo("成功", message)
                root.destroy()
            else:
                messagebox.showerror("错误", message)
        
        tk.Button(button_frame, text="更新并上传", command=update_and_upload, 
                 bg='#4CAF50', fg='white', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="仅更新", command=update_only, 
                 bg='#2196F3', fg='white', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="取消", command=root.destroy, 
                 bg='#f44336', fg='white', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        
        root.mainloop()
    
    def quick_update(self, increment_type="patch", upload=True):
        """快速更新（自动递增版本号）"""
        current_data = self.load_current_version()
        if current_data is None:
            print("无法加载当前版本信息")
            return False
        
        new_version = self.increment_version(current_data['level'], increment_type)
        success, message = self.update_version_info(new_version)
        
        print(message)
        
        if success and upload:
            print("正在上传到GitHub...")
            results = self.uploader.auto_upload(
                files=[self.update_file],
                commit_message=f"快速更新版本到 {new_version}",
                show_gui=False
            )
            
            all_success = all(result[1] for result in results)
            if all_success:
                print("✅ 版本更新并上传成功！")
            else:
                print("❌ 上传失败，请检查网络连接和Git配置")
                for step, success, detail in results:
                    if not success:
                        print(f"  {step}: {detail}")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='版本更新脚本')
    parser.add_argument('--version', '-v', help='新版本号')
    parser.add_argument('--content', '-c', nargs='+', help='更新内容')
    parser.add_argument('--type', '-t', choices=['major', 'minor', 'patch'], 
                       default='patch', help='版本递增类型')
    parser.add_argument('--no-upload', action='store_true', help='不自动上传')
    parser.add_argument('--quick', '-q', action='store_true', help='快速更新（自动递增）')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    updater = VersionUpdater()
    
    if args.interactive:
        updater.interactive_update()
    elif args.quick:
        updater.quick_update(args.type, not args.no_upload)
    else:
        success, message = updater.update_version_info(
            new_version=args.version,
            update_content=args.content,
            increment_type=args.type
        )
        
        print(message)
        
        if success and not args.no_upload:
            print("正在上传到GitHub...")
            results = updater.uploader.auto_upload(
                files=[updater.update_file],
                commit_message=f"更新版本信息",
                show_gui=False
            )
            
            all_success = all(result[1] for result in results)
            if all_success:
                print("✅ 上传成功！")
            else:
                print("❌ 上传失败")

if __name__ == "__main__":
    main()