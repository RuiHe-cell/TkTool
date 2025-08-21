#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动上传脚本 - 自动提交和推送更新文件到GitHub

功能:
1. 自动检测文件变化
2. 提交到本地Git仓库
3. 推送到远程GitHub仓库
4. 支持自定义提交信息
5. 支持批量操作
"""

import os
import json
import subprocess
import sys
from datetime import datetime
import argparse
import tkinter as tk
from tkinter import messagebox, simpledialog

class GitAutoUploader:
    def __init__(self, repo_path=None, config_file="config/git_config.json"):
        self.repo_path = repo_path or os.getcwd()
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """加载Git配置"""
        default_config = {
            "remote_name": "origin",
            "branch_name": "main",
            "auto_add_all": False,
            "files_to_track": [
                "INFO/update.json",
                "README.md",
                "config/"
            ],
            "commit_template": "更新版本信息 - {timestamp}",
            "github_username": "",
            "github_repo": "",
            "github_token": ""
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # 创建默认配置文件
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                return default_config
        except Exception as e:
            print(f"加载Git配置失败，使用默认配置: {e}")
            return default_config
    
    def run_git_command(self, command, capture_output=True):
        """执行Git命令"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                shell=True,
                capture_output=capture_output,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                print(f"Git命令执行失败: {command}")
                print(f"错误信息: {result.stderr}")
                return False, result.stderr
            
            return True, result.stdout if capture_output else "Success"
        except Exception as e:
            print(f"执行Git命令时出错: {e}")
            return False, str(e)
    
    def check_git_status(self):
        """检查Git状态"""
        success, output = self.run_git_command("git status --porcelain")
        if success:
            return output.strip() != "", output
        return False, output
    
    def init_git_repo(self):
        """初始化Git仓库"""
        if not os.path.exists(os.path.join(self.repo_path, '.git')):
            print("初始化Git仓库...")
            success, output = self.run_git_command("git init")
            if not success:
                return False, "初始化Git仓库失败"
        
        # 检查是否有远程仓库
        success, output = self.run_git_command("git remote -v")
        if success and self.config['remote_name'] not in output:
            if self.config['github_username'] and self.config['github_repo']:
                remote_url = f"https://github.com/{self.config['github_username']}/{self.config['github_repo']}.git"
                success, output = self.run_git_command(f"git remote add {self.config['remote_name']} {remote_url}")
                if not success:
                    return False, f"添加远程仓库失败: {output}"
        
        return True, "Git仓库初始化完成"
    
    def add_files(self, files=None):
        """添加文件到暂存区"""
        if files is None:
            if self.config['auto_add_all']:
                success, output = self.run_git_command("git add .")
                return success, output
            else:
                files = self.config['files_to_track']
        
        if isinstance(files, str):
            files = [files]
        
        for file in files:
            if os.path.exists(os.path.join(self.repo_path, file)):
                success, output = self.run_git_command(f"git add {file}")
                if not success:
                    return False, f"添加文件 {file} 失败: {output}"
            else:
                print(f"警告: 文件 {file} 不存在，跳过")
        
        return True, "文件添加成功"
    
    def commit_changes(self, message=None):
        """提交更改"""
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = self.config['commit_template'].format(timestamp=timestamp)
        
        success, output = self.run_git_command(f'git commit -m "{message}"')
        return success, output
    
    def push_to_remote(self):
        """推送到远程仓库"""
        # 首先尝试推送
        success, output = self.run_git_command(
            f"git push {self.config['remote_name']} {self.config['branch_name']}"
        )
        
        if not success and "upstream" in output:
            # 如果是第一次推送，设置upstream
            success, output = self.run_git_command(
                f"git push -u {self.config['remote_name']} {self.config['branch_name']}"
            )
        
        return success, output
    
    def auto_upload(self, files=None, commit_message=None, show_gui=True):
        """自动上传流程"""
        results = []
        
        # 1. 初始化Git仓库
        success, message = self.init_git_repo()
        results.append(("初始化仓库", success, message))
        if not success:
            return results
        
        # 2. 检查是否有变化
        has_changes, status = self.check_git_status()
        if not has_changes:
            results.append(("检查状态", True, "没有需要提交的更改"))
            if show_gui:
                self.show_result_dialog(results)
            return results
        
        # 3. 添加文件
        success, message = self.add_files(files)
        results.append(("添加文件", success, message))
        if not success:
            if show_gui:
                self.show_result_dialog(results)
            return results
        
        # 4. 提交更改
        success, message = self.commit_changes(commit_message)
        results.append(("提交更改", success, message))
        if not success:
            if show_gui:
                self.show_result_dialog(results)
            return results
        
        # 5. 推送到远程
        success, message = self.push_to_remote()
        results.append(("推送远程", success, message))
        
        if show_gui:
            self.show_result_dialog(results)
        
        return results
    
    def show_result_dialog(self, results):
        """显示结果对话框"""
        root = tk.Tk()
        root.withdraw()
        
        message = "🚀 自动上传结果:\n\n"
        all_success = True
        
        for step, success, detail in results:
            status = "✅" if success else "❌"
            message += f"{status} {step}: {detail[:100]}{'...' if len(detail) > 100 else ''}\n"
            if not success:
                all_success = False
        
        if all_success:
            message += "\n🎉 所有操作完成！更新已成功推送到GitHub。"
            messagebox.showinfo("上传成功", message)
        else:
            message += "\n⚠️ 部分操作失败，请检查错误信息。"
            messagebox.showerror("上传失败", message)
        
        root.destroy()
    
    def interactive_upload(self):
        """交互式上传"""
        root = tk.Tk()
        root.withdraw()
        
        # 询问提交信息
        commit_message = simpledialog.askstring(
            "提交信息",
            "请输入提交信息（留空使用默认）:",
            initialvalue=""
        )
        
        if commit_message is not None:  # 用户没有取消
            self.auto_upload(commit_message=commit_message if commit_message else None)
        
        root.destroy()

def main():
    parser = argparse.ArgumentParser(description='自动上传脚本')
    parser.add_argument('--message', '-m', help='提交信息')
    parser.add_argument('--files', '-f', nargs='+', help='要上传的文件')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    parser.add_argument('--no-gui', action='store_true', help='不显示GUI')
    
    args = parser.parse_args()
    
    uploader = GitAutoUploader()
    
    if args.interactive:
        uploader.interactive_upload()
    else:
        uploader.auto_upload(
            files=args.files,
            commit_message=args.message,
            show_gui=not args.no_gui
        )

if __name__ == "__main__":
    main()