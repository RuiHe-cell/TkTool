#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心数据生成器
功能：根据配置生成各种类型的测试数据
"""

import random
import string
from typing import List, Dict, Any, Union


class DataGeneratorCore:
    """核心数据生成器类"""

    def __init__(self):
        self.random = random.Random()

    def set_seed(self, seed: int):
        """设置随机种子"""
        self.random.seed(seed)

    def generate_test_data(self, configs: List[Dict[str, Any]], count: int, no_duplicate: bool = False) -> List[str]:
        """生成测试数据
        
        Args:
            configs: 变量配置列表
            count: 生成数据组数
            no_duplicate: 是否避免生成重复数据
            
        Returns:
            生成的测试数据列表，每个元素是一组完整的测试数据
        """
        test_data = []
        generated_set = set() if no_duplicate else None
        max_attempts = count * 10  # 最大尝试次数，避免无限循环
        attempts = 0

        while len(test_data) < count and attempts < max_attempts:
            data_group = self._generate_single_group(configs)

            if no_duplicate:
                if data_group not in generated_set:
                    generated_set.add(data_group)
                    test_data.append(data_group)
            else:
                test_data.append(data_group)

            attempts += 1

        # 如果无法生成足够的不重复数据，给出警告
        if no_duplicate and len(test_data) < count:
            print(f"警告: 只能生成 {len(test_data)} 个不重复的数据组，少于请求的 {count} 个")

        return test_data

    def generate_preview_data(self, configs: List[Dict[str, Any]], count: int = 3, no_duplicate: bool = False) -> List[
        str]:
        """生成预览数据
        
        Args:
            configs: 变量配置列表
            count: 生成数据组数
            no_duplicate: 是否避免生成重复数据
            
        Returns:
            生成的预览数据列表
        """
        return self.generate_test_data(configs, count, no_duplicate)

    def _generate_single_group(self, configs: List[Dict[str, Any]]) -> str:
        """生成单组数据
        
        Args:
            configs: 变量配置列表
            
        Returns:
            单组测试数据字符串
        """
        parts = []
        variable_values = {}  # 存储已生成的变量值，用于动态引用

        for config_index, config in enumerate(configs):
            loop_count = self._resolve_loop_count(config, variable_values)
            separator = self._get_separator(config['separator'])

            # 生成循环次数个值
            generated_values = []
            for i in range(loop_count):
                value = self._generate_single_value(config, variable_values)
                generated_values.append(value)

                # 添加值
                parts.append(str(value))

                # 判断是否需要添加分隔符
                # 规则：每个值后面都添加分隔符，除了整个数据组的最后一个值
                is_last_value_in_loop = (i == loop_count - 1)
                is_last_config = (config_index == len(configs) - 1)
                is_very_last_value = is_last_value_in_loop and is_last_config

                if not is_very_last_value:
                    parts.append(separator)

            # 存储变量值供后续引用
            var_name = config.get('name', '')
            if var_name:
                if len(generated_values) == 1:
                    variable_values[var_name] = generated_values[0]
                else:
                    variable_values[var_name] = generated_values

        return ''.join(parts)

    def _resolve_loop_count(self, config: Dict[str, Any], variable_values: Dict[str, Any]) -> int:
        """解析循环次数，支持引用变量
        
        Args:
            config: 变量配置
            variable_values: 已生成的变量值字典
            
        Returns:
            解析后的循环次数
        """
        loop_count = config.get('loop_count', 1)

        # 如果loop_count是字符串，尝试解析为变量引用
        if isinstance(loop_count, str):
            loop_count_str = loop_count.strip()

            # 检查是否是数字
            if loop_count_str.isdigit():
                return int(loop_count_str)

            # 检查是否是变量引用
            if loop_count_str in variable_values:
                ref_value = variable_values[loop_count_str]
                if isinstance(ref_value, (int, float)):
                    return int(ref_value)
                elif isinstance(ref_value, str) and ref_value.isdigit():
                    return int(ref_value)

            # 如果无法解析，返回默认值1
            return 1

        # 如果是数字，直接返回
        if isinstance(loop_count, (int, float)):
            return int(loop_count)

        return 1

    def _resolve_range_value(self, value: Union[str, int, float], variable_values: Dict[str, Any]) -> Union[int, float]:
        """解析范围值，支持变量引用
        
        Args:
            value: 范围值（可能是数字或变量名）
            variable_values: 已生成的变量值字典
            
        Returns:
            解析后的数值
        """
        # 如果是数字，直接返回
        if isinstance(value, (int, float)):
            return value

        # 如果是字符串，尝试解析
        if isinstance(value, str):
            value_str = value.strip()

            # 检查是否是数字字符串
            try:
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                pass

            # 检查是否是变量引用
            if value_str in variable_values:
                ref_value = variable_values[value_str]
                if isinstance(ref_value, (int, float)):
                    return ref_value
                elif isinstance(ref_value, str):
                    try:
                        if '.' in ref_value:
                            return float(ref_value)
                        else:
                            return int(ref_value)
                    except ValueError:
                        pass

            # 如果无法解析，尝试转换为数字，失败则返回0
            try:
                return int(value_str)
            except ValueError:
                return 0

        return 0

    def _generate_single_value(self, config: Dict[str, Any], variable_values: Dict[str, Any] = None) -> Union[
        int, float, str]:
        """生成单个值
        
        Args:
            config: 变量配置
            variable_values: 已生成的变量值字典
            
        Returns:
            生成的值
        """
        if variable_values is None:
            variable_values = {}

        data_type = config['data_type']
        source_type = config['source_type']

        if source_type == "数据范围":
            return self._generate_from_range(config, variable_values)
        elif source_type == "选择列表":
            return self._generate_from_choices(config)
        elif source_type == "字符集合":
            return self._generate_from_charset(config, variable_values)
        elif source_type == "来自代码":
            return self._generate_from_code(config)
        else:
            raise ValueError(f"未知的数据源类型: {source_type}")

    def _generate_from_range(self, config: Dict[str, Any], variable_values: Dict[str, Any] = None) -> Union[
        int, float, str]:
        """从数据范围生成值"""
        if variable_values is None:
            variable_values = {}

        data_type = config['data_type']
        min_val = self._resolve_range_value(config['min_value'], variable_values)
        max_val = self._resolve_range_value(config['max_value'], variable_values)

        # 确保 max_val > min_val
        if max_val <= min_val:
            # 如果最大值不大于最小值，交换它们或调整
            if max_val == min_val:
                max_val = min_val + 1  # 至少保证有1的差距
            else:
                min_val, max_val = max_val, min_val

        if data_type == "整数":
            return self.random.randint(int(min_val), int(max_val))
        elif data_type == "浮点数":
            return round(self.random.uniform(float(min_val), float(max_val)), 2)
        elif data_type == "字符串":
            # 对于字符串，范围表示ASCII码范围
            length = self._parse_string_length(config.get('string_length', '10'), variable_values)
            result = []
            for _ in range(length):
                char_code = self.random.randint(int(min_val), int(max_val))
                result.append(chr(char_code))
            return ''.join(result)
        else:
            raise ValueError(f"数据范围不支持数据类型: {data_type}")

    def _generate_from_choices(self, config: Dict[str, Any]) -> Union[int, float, str]:
        """从选择列表生成值"""
        choices = config['choices']
        if not choices:
            raise ValueError("选择列表不能为空")

        selected = self.random.choice(choices)
        data_type = config['data_type']

        # 根据数据类型转换
        if data_type == "整数":
            return int(selected)
        elif data_type == "浮点数":
            return float(selected)
        else:
            return selected

    def _generate_from_code(self, config: Dict[str, Any]) -> Any:
        """从自定义代码生成值"""
        custom_code = config['custom_code']

        try:
            # 创建更完整的安全执行环境
            import math
            import datetime
            import re
            import itertools

            safe_globals = {
                '__builtins__': {
                    '__import__': __import__,
                    'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'range': range, 'enumerate': enumerate, 'zip': zip,
                    'min': min, 'max': max, 'sum': sum, 'abs': abs, 'round': round,
                    'chr': chr, 'ord': ord, 'print': print, 'sorted': sorted,
                    'reversed': reversed, 'any': any, 'all': all
                },
                # 直接提供常用模块，避免import问题
                'random': random,
                'string': string,
                'math': math,
                'datetime': datetime,
                're': re,
                'itertools': itertools,
            }

            # 执行用户代码
            local_vars = {}
            exec(custom_code, safe_globals, local_vars)

            # 将local_vars中的内容合并到safe_globals中，这样函数可以互相访问
            combined_globals = {**safe_globals, **local_vars}

            # 查找生成函数
            generate_func = None

            # 优先查找 generate_data 函数
            if 'generate_data' in local_vars and callable(local_vars['generate_data']):
                generate_func = local_vars['generate_data']
            else:
                # 查找任何以 generate 开头的函数
                for name, obj in local_vars.items():
                    if callable(obj) and name.startswith('generate'):
                        generate_func = obj
                        break

            if generate_func is None:
                raise ValueError("代码中未找到生成函数，请确保定义了generate_data函数")

            # 更新函数的全局命名空间，使其能访问辅助函数
            if hasattr(generate_func, '__globals__'):
                generate_func.__globals__.update(combined_globals)

            # 调用生成函数
            result = generate_func()

            # 根据数据类型转换结果
            data_type = config.get('data_type', '字符串')
            if data_type == "整数":
                return int(result)
            elif data_type == "浮点数":
                return float(result)
            else:
                return str(result)

        except Exception as e:
            raise ValueError(f"执行自定义代码时出错: {str(e)}")

    def _generate_from_charset(self, config: Dict[str, Any], variable_values: Dict[str, Any] = None) -> str:
        """从字符集合生成值"""
        if variable_values is None:
            variable_values = {}
            
        charset_def = config['charset']
        charset = self._expand_charset(charset_def)

        if not charset:
            raise ValueError("字符集不能为空")

        data_type = config['data_type']

        if data_type == "字符":
            return self.random.choice(charset)
        elif data_type == "字符串":
            length = self._parse_string_length(config.get('string_length', '10'), variable_values)
            return ''.join(self.random.choices(charset, k=length))
        else:
            raise ValueError(f"字符集合不支持数据类型: {data_type}")

    def _parse_string_length(self, length_str: str, variable_values: Dict[str, Any] = None) -> int:
        """解析字符串长度配置
        
        Args:
            length_str: 长度配置字符串，支持固定长度（如"10"）、随机长度（如"1,10"）或变量引用（如"n"、"1,n"）
            variable_values: 已生成的变量值字典
            
        Returns:
            解析后的长度值
        """
        if variable_values is None:
            variable_values = {}
            
        length_str = str(length_str).strip()

        if ',' in length_str:
            # 随机长度格式："1,10" 或 "1,n" 或 "m,n"
            try:
                parts = length_str.split(',')
                if len(parts) != 2:
                    raise ValueError(f"随机长度格式错误，应为 'min,max'，实际为: {length_str}")

                min_len = self._resolve_length_value(parts[0].strip(), variable_values)
                max_len = self._resolve_length_value(parts[1].strip(), variable_values)

                if min_len < 0 or max_len < 0:
                    raise ValueError(f"长度不能为负数: {length_str}")
                if min_len > max_len:
                    raise ValueError(f"最小长度不能大于最大长度: {length_str}")

                return self.random.randint(min_len, max_len)
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"长度配置包含非数字字符: {length_str}")
                raise e
        else:
            # 固定长度格式："10" 或变量引用 "n"
            try:
                length = self._resolve_length_value(length_str, variable_values)
                if length < 0:
                    raise ValueError(f"长度不能为负数: {length}")
                return length
            except ValueError:
                raise ValueError(f"长度配置格式错误: {length_str}")
    
    def _resolve_length_value(self, value: str, variable_values: Dict[str, Any]) -> int:
        """解析长度值，支持变量引用
        
        Args:
            value: 长度值（可能是数字或变量名）
            variable_values: 已生成的变量值字典
            
        Returns:
            解析后的长度值
        """
        value_str = str(value).strip()
        
        # 检查是否是数字字符串
        if value_str.isdigit():
            return int(value_str)
        
        # 检查是否是变量引用
        if value_str in variable_values:
            ref_value = variable_values[value_str]
            if isinstance(ref_value, (int, float)):
                return int(ref_value)
            elif isinstance(ref_value, str) and ref_value.isdigit():
                return int(ref_value)
        
        # 如果无法解析，尝试转换为数字，失败则返回默认值
        try:
            return int(value_str)
        except ValueError:
            # 如果是无法识别的变量名，返回默认长度
            return 10

    def _expand_charset(self, charset_def: str) -> str:
        """展开字符集定义
        
        Args:
            charset_def: 字符集定义，如 'a-z', 'A-Z', '0-9', 'abc123'
            
        Returns:
            展开后的字符集字符串
        """
        result = []
        i = 0

        while i < len(charset_def):
            if i + 2 < len(charset_def) and charset_def[i + 1] == '-':
                # 处理范围，如 'a-z'
                start_char = charset_def[i]
                end_char = charset_def[i + 2]

                start_code = ord(start_char)
                end_code = ord(end_char)

                for code in range(start_code, end_code + 1):
                    result.append(chr(code))

                i += 3
            else:
                # 单个字符
                result.append(charset_def[i])
                i += 1

        return ''.join(result)

    def _get_separator(self, separator_name: str) -> str:
        """获取分隔符字符
        
        Args:
            separator_name: 分隔符名称
            
        Returns:
            实际的分隔符字符
        """
        separator_map = {
            "无": "",
            "换行": "\n",
            "空格": " ",
            "制表符": "\t",
            "逗号": ",",
            "分号": ";"
        }
        return separator_map.get(separator_name, " ")

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效
        
        Args:
            config: 变量配置
            
        Returns:
            配置是否有效
        """
        try:
            # 尝试生成一个值来验证配置
            self._generate_single_value(config)
            return True
        except Exception:
            return False

    def get_config_description(self, config: Dict[str, Any]) -> str:
        """获取配置描述
        
        Args:
            config: 变量配置
            
        Returns:
            配置的文字描述
        """
        name = config['name']
        data_type = config['data_type']
        source_type = config['source_type']
        separator = config['separator']

        desc_parts = [f"变量 '{name}' ({data_type})"]

        if source_type == "数据范围":
            min_val = config.get('min_value', '')
            max_val = config.get('max_value', '')
            desc_parts.append(f"范围: {min_val} 到 {max_val}")

            if data_type == "字符串":
                length = config.get('string_length', 10)
                desc_parts.append(f"长度: {length}")

        elif source_type == "选择列表":
            choices = config.get('choices', [])
            desc_parts.append(f"选项: {', '.join(map(str, choices[:3]))}{'...' if len(choices) > 3 else ''}")

        elif source_type == "字符集合":
            charset = config.get('charset', '')
            desc_parts.append(f"字符集: {charset}")

            if data_type == "字符串":
                length = config.get('string_length', 10)
                desc_parts.append(f"长度: {length}")

        elif source_type == "来自代码":
            code = config.get('custom_code', '')
            # 显示代码的前30个字符作为预览
            code_preview = code[:30] + '...' if len(code) > 30 else code
            desc_parts.append(f"自定义代码: {code_preview}")

        desc_parts.append(f"分隔符: {separator}")

        return ", ".join(desc_parts)
