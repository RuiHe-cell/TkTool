import requests
import threading
import json
import tkinter as tk
from tkinter import messagebox
import webbrowser
import os
import sys
from datetime import datetime

class UpdateChecker:
    def __init__(self, local_update_file=None, config_file=None):
        # 获取程序运行目录（兼容PyInstaller）
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后的路径
            self.base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境路径
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 设置默认路径
        if local_update_file is None:
            local_update_file = os.path.join(self.base_path, "config", "update.json")
        if config_file is None:
            config_file = os.path.join(self.base_path, "config", "update_config.json")
            
        self.local_update_file = local_update_file
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """加载更新配置"""
        default_config = {
            "github_raw_url": "https://raw.githubusercontent.com/your-username/your-repo/main/config/update.json",
            "github_page_url": "https://github.com/your-username/your-repo/blob/main/config/update.json#L9-L9",
            "check_on_startup": True,
            "timeout": 10,
            "auto_update_local": True,
            "show_update_dialog": True,
            "check_interval_hours": 24
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
            print(f"加载配置失败，使用默认配置: {e}")
            return default_config

    def check_for_updates(self):
        """检查是否有更新"""
        try:
            # 检查配置是否有效
            if not self.config.get('github_raw_url') or 'your-username' in self.config['github_raw_url']:
                print("GitHub配置未设置，跳过更新检查")
                return False, None
                
            response = requests.get(self.config['github_raw_url'], timeout=self.config['timeout'])

            if response.status_code == 200:
                remote_data = response.json()

                # 读取本地版本信息
                if os.path.exists(self.local_update_file):
                    with open(self.local_update_file, 'r', encoding='utf-8') as f:
                        local_data = json.load(f)

                    # 比较版本号
                    if self.compare_versions(remote_data.get('level', '1.0.0'), local_data.get('level', '1.0.0')):
                        return True, remote_data

                    # 比较更新时间
                    if self.compare_update_time(remote_data.get('update_time', ''), local_data.get('update_time', '')):
                        return True, remote_data
                else:
                    # 本地文件不存在，创建默认文件
                    self.create_default_local_file()
                    return True, remote_data  # 首次运行，提示有更新

                return False, None
            else:
                print(f"获取远程更新信息失败，状态码: {response.status_code}")
                return False, None
                
        except requests.exceptions.Timeout:
            print("检查更新超时")
            return False, None
        except requests.exceptions.ConnectionError:
            print("网络连接失败，无法检查更新")
            return False, None
        except json.JSONDecodeError:
            print("远程更新文件格式错误")
            return False, None
        except Exception as e:
            print(f"检查更新失败: {e}")
            return False, None

    def create_default_local_file(self):
        """创建默认的本地更新文件"""
        try:
            default_data = {
                "level": "1.0.0",
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": "初始版本",
                "features": ["基础功能"]
            }
            
            os.makedirs(os.path.dirname(self.local_update_file), exist_ok=True)
            with open(self.local_update_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
            print(f"已创建默认更新文件: {self.local_update_file}")
        except Exception as e:
            print(f"创建默认更新文件失败: {e}")

    def compare_versions(self, remote_version, local_version):
        """比较版本号"""
        try:
            def version_tuple(v):
                return tuple(map(int, (v.split("."))))

            return version_tuple(remote_version) > version_tuple(local_version)
        except:
            return False

    def compare_update_time(self, remote_time, local_time):
        """比较更新时间"""
        try:
            if not remote_time or not local_time:
                return False

            remote_dt = datetime.strptime(remote_time, "%Y-%m-%d")
            local_dt = datetime.strptime(local_time, "%Y-%m-%d")

            return remote_dt > local_dt
        except:
            return False

    def show_update_dialog(self, update_data):
        """显示更新对话框"""

        def show_dialog():
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口

            message = f"🎉 发现新版本 {update_data['level']}\n\n"
            message += f"📅 更新时间: {update_data.get('update_time', '未知')}\n\n"
            message += "📋 更新内容:\n"

            for i, content in enumerate(update_data.get('update_content', []), 1):
                message += f"  {i}. {content}\n"

            message += "\n是否立即查看更新详情？"

            result = messagebox.askyesno(
                "发现更新",
                message,
                icon='question'
            )

            if result:
                # 打开更新链接
                webbrowser.open(self.config['github_page_url'])

                # 更新本地文件
                self.update_local_file(update_data)

            root.destroy()

        # 在主线程中显示对话框
        show_dialog()

    def update_local_file(self, remote_data):
        """更新本地文件"""
        try:
            with open(self.local_update_file, 'w', encoding='utf-8') as f:
                json.dump(remote_data, f, indent=4, ensure_ascii=False)
            print("本地更新文件已同步")
        except Exception as e:
            print(f"更新本地文件失败: {e}")

    def start_update_check(self, show_no_update=False):
        """在后台线程中检查更新"""

        def check_thread():
            try:
                if not self.config.get('check_on_startup', True):
                    return

                result = self.check_for_updates()
                if result is None:
                    print("更新检查返回None，跳过处理")
                    return
                    
                has_update, update_data = result
                if has_update and update_data:
                    # 在主线程中显示对话框
                    if self.config.get('show_update_dialog', True):
                        self.show_update_dialog(update_data)
                elif show_no_update:
                    try:
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showinfo("检查更新", "当前已是最新版本！")
                        root.destroy()
                    except Exception as e:
                        print(f"显示无更新对话框失败: {e}")
            except Exception as e:
                print(f"更新检查线程异常: {e}")

        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()

    def manual_check_update(self):
        """手动检查更新"""
        try:
            result = self.check_for_updates()
            if result is None:
                messagebox.showwarning("检查更新", "更新检查失败，请检查网络连接或配置")
                return
                
            has_update, update_data = result
            if has_update and update_data:
                self.show_update_dialog(update_data)
            else:
                messagebox.showinfo("检查更新", "当前已是最新版本！")
        except Exception as e:
            messagebox.showerror("检查更新", f"检查更新时发生错误: {e}")


# 使用示例
if __name__ == "__main__":
    checker = UpdateChecker()
    checker.start_update_check()

    # 保持程序运行以测试
    import time

    time.sleep(2)
