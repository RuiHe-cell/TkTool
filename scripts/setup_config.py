#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置设置脚本 - 帮助用户配置GitHub仓库信息

使用方法:
1. 交互式配置: python setup_config.py
2. 命令行配置: python setup_config.py --username your-username --repo your-repo
"""

import os
import json
import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import webbrowser

class ConfigSetup:
    def __init__(self):
        self.update_config_file = "config/update_config.json"
        self.git_config_file = "config/git_config.json"
        
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    def save_config(self, config_file, config_data):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def update_github_config(self, username, repo_name):
        """更新GitHub配置"""
        # 更新update_config.json
        update_config = self.load_config(self.update_config_file)
        update_config.update({
            "github_raw_url": f"https://raw.githubusercontent.com/{username}/{repo_name}/main/INFO/update.json",
            "github_page_url": f"https://github.com/{username}/{repo_name}/blob/main/INFO/update.json#L9-L9",
            "check_on_startup": True,
            "timeout": 10,
            "auto_update_local": True,
            "show_update_dialog": True,
            "update_check_interval": 3600
        })
        
        # 更新git_config.json
        git_config = self.load_config(self.git_config_file)
        git_config.update({
            "remote_name": "origin",
            "branch_name": "main",
            "auto_add_all": False,
            "files_to_track": [
                "INFO/update.json",
                "README.md",
                "config/"
            ],
            "commit_template": "更新版本信息 - {timestamp}",
            "github_username": username,
            "github_repo": repo_name,
            "github_token": git_config.get("github_token", "")
        })
        
        # 保存配置
        success1 = self.save_config(self.update_config_file, update_config)
        success2 = self.save_config(self.git_config_file, git_config)
        
        return success1 and success2
    
    def interactive_setup(self):
        """交互式配置界面"""
        root = tk.Tk()
        root.title("GitHub仓库配置")
        root.geometry("600x500")
        root.resizable(False, False)
        
        # 居中显示
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (500 // 2)
        root.geometry(f"600x500+{x}+{y}")
        
        # 加载当前配置
        git_config = self.load_config(self.git_config_file)
        
        # 创建界面
        tk.Label(root, text="GitHub仓库配置", font=('Arial', 18, 'bold')).pack(pady=20)
        
        # 说明文本
        info_text = (
            "请配置您的GitHub仓库信息以启用自动更新功能。\n"
            "如果您还没有GitHub仓库，请先创建一个。"
        )
        tk.Label(root, text=info_text, font=('Arial', 10), wraplength=550, justify='left').pack(pady=10)
        
        # 配置框架
        config_frame = tk.Frame(root)
        config_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        # GitHub用户名
        tk.Label(config_frame, text="GitHub用户名:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        username_var = tk.StringVar(value=git_config.get('github_username', ''))
        username_entry = tk.Entry(config_frame, textvariable=username_var, font=('Arial', 11))
        username_entry.pack(fill='x', pady=(0, 15))
        
        # 仓库名称
        tk.Label(config_frame, text="仓库名称:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        repo_var = tk.StringVar(value=git_config.get('github_repo', ''))
        repo_entry = tk.Entry(config_frame, textvariable=repo_var, font=('Arial', 11))
        repo_entry.pack(fill='x', pady=(0, 15))
        
        # GitHub Token (可选)
        tk.Label(config_frame, text="GitHub Token (可选，用于私有仓库):", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        token_var = tk.StringVar(value=git_config.get('github_token', ''))
        token_entry = tk.Entry(config_frame, textvariable=token_var, font=('Arial', 11), show='*')
        token_entry.pack(fill='x', pady=(0, 10))
        
        # 帮助链接
        help_frame = tk.Frame(config_frame)
        help_frame.pack(fill='x', pady=10)
        
        def open_github():
            webbrowser.open("https://github.com/new")
        
        def open_token_help():
            webbrowser.open("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token")
        
        tk.Button(help_frame, text="创建GitHub仓库", command=open_github, 
                 bg='#24292e', fg='white', font=('Arial', 10)).pack(side='left', padx=(0, 10))
        tk.Button(help_frame, text="获取GitHub Token", command=open_token_help, 
                 bg='#0366d6', fg='white', font=('Arial', 10)).pack(side='left')
        
        # 预览配置
        preview_frame = tk.LabelFrame(config_frame, text="配置预览", font=('Arial', 11, 'bold'))
        preview_frame.pack(fill='x', pady=15)
        
        preview_text = tk.Text(preview_frame, height=6, font=('Consolas', 9), bg='#f6f8fa')
        preview_text.pack(fill='x', padx=10, pady=10)
        
        def update_preview():
            username = username_var.get().strip()
            repo = repo_var.get().strip()
            
            if username and repo:
                preview_content = f"""更新检查URL: https://raw.githubusercontent.com/{username}/{repo}/main/INFO/update.json
更新页面URL: https://github.com/{username}/{repo}/blob/main/INFO/update.json#L9-L9
远程仓库URL: https://github.com/{username}/{repo}.git

配置完成后，程序将能够:
✓ 自动检查更新
✓ 自动上传版本信息
✓ 显示更新对话框"""
            else:
                preview_content = "请填写GitHub用户名和仓库名称以查看配置预览"
            
            preview_text.delete('1.0', 'end')
            preview_text.insert('1.0', preview_content)
        
        # 绑定更新事件
        username_var.trace('w', lambda *args: update_preview())
        repo_var.trace('w', lambda *args: update_preview())
        
        # 初始更新预览
        update_preview()
        
        # 按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        def save_config():
            username = username_var.get().strip()
            repo = repo_var.get().strip()
            token = token_var.get().strip()
            
            if not username or not repo:
                messagebox.showerror("错误", "请填写GitHub用户名和仓库名称")
                return
            
            # 更新配置
            success = self.update_github_config(username, repo)
            
            if success:
                # 如果有token，单独保存
                if token:
                    git_config = self.load_config(self.git_config_file)
                    git_config['github_token'] = token
                    self.save_config(self.git_config_file, git_config)
                
                messagebox.showinfo(
                    "配置成功", 
                    f"GitHub仓库配置已保存！\n\n"
                    f"用户名: {username}\n"
                    f"仓库: {repo}\n\n"
                    f"现在您可以使用自动更新功能了。"
                )
                root.destroy()
            else:
                messagebox.showerror("错误", "保存配置失败，请检查文件权限")
        
        def test_config():
            username = username_var.get().strip()
            repo = repo_var.get().strip()
            
            if not username or not repo:
                messagebox.showerror("错误", "请填写GitHub用户名和仓库名称")
                return
            
            # 测试URL是否可访问
            import requests
            test_url = f"https://api.github.com/repos/{username}/{repo}"
            
            try:
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    repo_info = response.json()
                    messagebox.showinfo(
                        "测试成功", 
                        f"仓库连接成功！\n\n"
                        f"仓库名: {repo_info['full_name']}\n"
                        f"描述: {repo_info.get('description', '无')}\n"
                        f"创建时间: {repo_info['created_at'][:10]}"
                    )
                elif response.status_code == 404:
                    messagebox.showerror("测试失败", "仓库不存在或无法访问")
                else:
                    messagebox.showerror("测试失败", f"HTTP错误: {response.status_code}")
            except Exception as e:
                messagebox.showerror("测试失败", f"网络错误: {str(e)}")
        
        tk.Button(button_frame, text="测试连接", command=test_config, 
                 bg='#ffc107', fg='black', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="保存配置", command=save_config, 
                 bg='#28a745', fg='white', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        tk.Button(button_frame, text="取消", command=root.destroy, 
                 bg='#dc3545', fg='white', font=('Arial', 11), padx=20).pack(side='left', padx=5)
        
        root.mainloop()
    
    def command_line_setup(self, username, repo, token=None):
        """命令行配置"""
        success = self.update_github_config(username, repo)
        
        if success:
            if token:
                git_config = self.load_config(self.git_config_file)
                git_config['github_token'] = token
                self.save_config(self.git_config_file, git_config)
            
            print(f"✅ GitHub仓库配置已保存: {username}/{repo}")
            return True
        else:
            print("❌ 配置保存失败")
            return False

def main():
    parser = argparse.ArgumentParser(description='GitHub仓库配置脚本')
    parser.add_argument('--username', '-u', help='GitHub用户名')
    parser.add_argument('--repo', '-r', help='仓库名称')
    parser.add_argument('--token', '-t', help='GitHub Token (可选)')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    
    args = parser.parse_args()
    
    setup = ConfigSetup()
    
    if args.interactive or (not args.username and not args.repo):
        setup.interactive_setup()
    else:
        if not args.username or not args.repo:
            print("错误: 请提供用户名和仓库名称")
            parser.print_help()
            return
        
        setup.command_line_setup(args.username, args.repo, args.token)

if __name__ == "__main__":
    main()