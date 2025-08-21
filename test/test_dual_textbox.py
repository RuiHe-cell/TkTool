#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试双文本框界面功能
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_api.deepseek_dialog import DeepSeekDialog
from deepseek_api.api_key_manager import ApiKeyManager
import tkinter as tk

def test_dual_textbox_interface():
    """测试双文本框界面"""
    print("=== 测试双文本框界面 ===")
    print()
    
    # 检查是否有保存的API密钥
    api_key = ApiKeyManager.get_api_key()
    if not api_key:
        print("未找到保存的API密钥，请先在主程序中设置API密钥")
        return
    
    print(f"使用API密钥: {api_key[:10]}...")
    
    # 创建根窗口
    root = tk.Tk()
    root.title("双文本框界面测试")
    root.geometry("900x700")
    
    try:
        print("\n创建DeepSeek对话窗口...")
        
        # 创建DeepSeek对话
        dialog = DeepSeekDialog(
            parent=root,
            api_key=api_key,
            problem_description="编写一个函数，计算两个数的最大公约数",
            test_data="12 18"
        )
        
        print("DeepSeek对话窗口创建完成")
        print("\n界面说明:")
        print("- 上方文本框：显示DeepSeek原始返回结果（可编辑）")
        print("- 下方文本框：显示精炼后的代码（只读）")
        print("- 复制精炼代码：只复制下方精炼后的代码")
        print("- 手动提取代码：从上方文本框重新提取代码到下方")
        print("- 重新生成：清空两个文本框并重新调用API")
        print("\n开始生成代码...")
        
        # 开始生成（这会触发API调用）
        dialog.start_generation()
        
        # 运行主循环
        root.mainloop()
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        if root.winfo_exists():
            root.destroy()

def main():
    """主函数"""
    print("DeepSeek双文本框界面测试")
    print("=" * 40)
    print()
    
    print("功能说明:")
    print("1. 原始返回结果文本框（上方）：")
    print("   - 显示DeepSeek的原始返回内容")
    print("   - 生成完成后可以编辑")
    print("   - 背景色：浅灰色")
    print()
    print("2. 精炼代码文本框（下方）：")
    print("   - 显示提取和清理后的纯代码")
    print("   - 只读，不可编辑")
    print("   - 背景色：浅蓝色")
    print()
    print("3. 按钮功能：")
    print("   - 复制精炼代码：复制下方文本框的内容")
    print("   - 手动提取代码：从上方重新提取到下方")
    print("   - 重新生成：清空并重新调用API")
    print()
    
    input("按回车键开始测试...")
    
    test_dual_textbox_interface()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()