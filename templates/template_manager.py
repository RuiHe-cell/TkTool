#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理器
功能：管理数据生成模板的加载、保存和应用
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class TemplateManager:
    """模板管理器类"""

    def __init__(self):
        self.templates_dir = Path(__file__).parent
        self.default_templates_file = self.templates_dir / "default_templates.json"
        self.user_templates_dir = self.templates_dir / "user_templates"
        self.user_templates_dir.mkdir(exist_ok=True)

    def load_default_templates(self) -> List[Dict[str, Any]]:
        """加载默认模板
        
        Returns:
            默认模板列表
        """
        try:
            with open(self.default_templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('templates', [])
        except Exception as e:
            print(f"加载默认模板失败: {e}")
            return []

    def load_user_templates(self) -> List[Dict[str, Any]]:
        """加载用户自定义模板
        
        Returns:
            用户模板列表
        """
        templates = []

        try:
            for template_file in self.user_templates_dir.glob("*.json"):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_data['file_path'] = str(template_file)
                    templates.append(template_data)
        except Exception as e:
            print(f"加载用户模板失败: {e}")

        return templates

    def get_all_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有模板
        
        Returns:
            包含默认模板和用户模板的字典
        """
        return {
            'default': self.load_default_templates(),
            'user': self.load_user_templates()
        }

    def save_user_template(self, template_name: str, variables: List[Dict[str, Any]],
                           description: str = "") -> bool:
        """保存用户模板
        
        Args:
            template_name: 模板名称
            variables: 变量配置列表
            description: 模板描述
            
        Returns:
            是否保存成功
        """
        try:
            # 生成安全的文件名
            safe_name = self._make_safe_filename(template_name)
            template_file = self.user_templates_dir / f"{safe_name}.json"

            template_data = {
                'name': template_name,
                'description': description,
                'created_time': self._get_current_time(),
                'variables': variables
            }

            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"保存用户模板失败: {e}")
            return False

    def delete_user_template(self, template_name: str) -> bool:
        """删除用户模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            safe_name = self._make_safe_filename(template_name)
            template_file = self.user_templates_dir / f"{safe_name}.json"

            if template_file.exists():
                template_file.unlink()
                return True
            else:
                return False
        except Exception as e:
            print(f"删除用户模板失败: {e}")
            return False

    def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板数据，如果不存在返回None
        """
        all_templates = self.get_all_templates()

        # 先在默认模板中查找
        for template in all_templates['default']:
            if template['name'] == template_name:
                return template

        # 再在用户模板中查找
        for template in all_templates['user']:
            if template['name'] == template_name:
                return template

        return None

    def validate_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证模板数据
        
        Args:
            template_data: 模板数据
            
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': []
        }

        # 检查必需字段
        required_fields = ['name', 'variables']
        for field in required_fields:
            if field not in template_data:
                result['valid'] = False
                result['errors'].append(f"缺少必需字段: {field}")

        # 检查变量配置
        if 'variables' in template_data:
            variables = template_data['variables']
            if not isinstance(variables, list) or len(variables) == 0:
                result['valid'] = False
                result['errors'].append("变量配置必须是非空列表")
            else:
                for i, var in enumerate(variables):
                    var_errors = self._validate_variable(var, i)
                    result['errors'].extend(var_errors)
                    if var_errors:
                        result['valid'] = False

        return result

    def _validate_variable(self, variable: Dict[str, Any], index: int) -> List[str]:
        """验证单个变量配置
        
        Args:
            variable: 变量配置
            index: 变量索引
            
        Returns:
            错误信息列表
        """
        errors = []

        # 检查必需字段
        required_fields = ['name', 'data_type', 'source_type', 'separator']
        for field in required_fields:
            if field not in variable:
                errors.append(f"变量 {index + 1} 缺少必需字段: {field}")

        # 检查数据类型
        if 'data_type' in variable:
            valid_types = ['整数', '浮点数', '字符串', '字符']
            if variable['data_type'] not in valid_types:
                errors.append(f"变量 {index + 1} 数据类型无效: {variable['data_type']}")

        # 检查来源类型
        if 'source_type' in variable:
            valid_sources = ['数据范围', '选择列表', '字符集合']
            if variable['source_type'] not in valid_sources:
                errors.append(f"变量 {index + 1} 来源类型无效: {variable['source_type']}")

        # 根据来源类型检查相应配置
        source_type = variable.get('source_type')
        if source_type == '数据范围':
            if 'min_value' not in variable or 'max_value' not in variable:
                errors.append(f"变量 {index + 1} 数据范围配置不完整")
        elif source_type == '选择列表':
            if 'choices' not in variable or not variable['choices']:
                errors.append(f"变量 {index + 1} 选择列表不能为空")
        elif source_type == '字符集合':
            if 'charset' not in variable or not variable['charset']:
                errors.append(f"变量 {index + 1} 字符集合不能为空")

        return errors

    def export_template(self, template_name: str, export_path: str) -> bool:
        """导出模板
        
        Args:
            template_name: 模板名称
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            template = self.get_template_by_name(template_name)
            if not template:
                return False

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False

    def import_template(self, import_path: str) -> bool:
        """导入模板
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            # 验证模板
            validation_result = self.validate_template(template_data)
            if not validation_result['valid']:
                print(f"模板验证失败: {validation_result['errors']}")
                return False

            # 保存为用户模板
            return self.save_user_template(
                template_data['name'],
                template_data['variables'],
                template_data.get('description', '')
            )
        except Exception as e:
            print(f"导入模板失败: {e}")
            return False

    def _make_safe_filename(self, name: str) -> str:
        """生成安全的文件名
        
        Args:
            name: 原始名称
            
        Returns:
            安全的文件名
        """
        # 移除或替换不安全的字符
        unsafe_chars = '<>:"/\\|?*'
        safe_name = name
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')

        # 限制长度
        if len(safe_name) > 50:
            safe_name = safe_name[:50]

        return safe_name

    def _get_current_time(self) -> str:
        """获取当前时间字符串
        
        Returns:
            ISO格式的时间字符串
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def get_template_names(self) -> Dict[str, List[str]]:
        """获取所有模板名称
        
        Returns:
            包含默认模板和用户模板名称的字典
        """
        all_templates = self.get_all_templates()

        return {
            'default': [t['name'] for t in all_templates['default']],
            'user': [t['name'] for t in all_templates['user']]
        }
