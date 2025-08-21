#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
功能：管理用户偏好设置的保存和加载
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 获取配置目录路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件，使用exe所在目录
            base_path = Path(os.path.dirname(sys.executable))
        else:
            # 开发环境
            base_path = Path(__file__).parent.parent

        self.config_dir = base_path / 'config'
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / 'user_preferences.json'

        # 默认配置
        self.default_config = {
            'test_count': '10',
            'no_duplicate': False,
            'delete_temp_files': False,
            'output_dir': './test_data'
        }

    def load_config(self) -> Dict[str, Any]:
        """加载配置
        
        Returns:
            配置字典
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保所有必需的键都存在
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
        except Exception as e:
            print(f"加载配置失败: {e}")

        return self.default_config.copy()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置
        
        Args:
            config: 要保存的配置字典
            
        Returns:
            是否保存成功
        """
        try:
            # 确保配置目录存在
            self.config_dir.mkdir(exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_config_value(self, key: str, default=None) -> Any:
        """获取单个配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        config = self.load_config()
        return config.get(key, default)

    def set_config_value(self, key: str, value: Any) -> bool:
        """设置单个配置值
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            是否设置成功
        """
        config = self.load_config()
        config[key] = value
        return self.save_config(config)

    def reset_to_default(self) -> bool:
        """重置为默认配置
        
        Returns:
            是否重置成功
        """
        return self.save_config(self.default_config.copy())

    def get_config_file_path(self) -> str:
        """获取配置文件路径
        
        Returns:
            配置文件路径字符串
        """
        return str(self.config_file)
