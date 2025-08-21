#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码提取工具
功能：从DeepSeek返回的文本中提取纯Python代码
"""

import re
from typing import Optional


class CodeExtractor:
    """代码提取器"""

    @staticmethod
    def extract_python_code(text: str) -> Optional[str]:
        """从文本中提取Python代码
        
        Args:
            text: 包含代码的文本
            
        Returns:
            提取的Python代码，如果没有找到则返回None
        """
        if not text or not text.strip():
            return None

        # 方法1: 提取```python```代码块
        python_blocks = re.findall(r'```python\s*\n(.*?)\n```', text, re.DOTALL | re.IGNORECASE)
        if python_blocks:
            return python_blocks[-1].strip()  # 返回最后一个代码块

        # 方法2: 提取```代码块（不指定语言）
        code_blocks = re.findall(r'```\s*\n(.*?)\n```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[-1].strip()  # 返回最后一个代码块

        # 方法3: 提取以常见Python关键字开头的行
        lines = text.split('\n')
        code_lines = []
        in_code_section = False

        python_keywords = [
            'import', 'from', 'def', 'class', 'if', 'for', 'while', 'try', 'with',
            'input_data', 'print(', '=', 'return'
        ]

        for line in lines:
            stripped_line = line.strip()

            # 跳过空行和注释
            if not stripped_line or stripped_line.startswith('#'):
                if in_code_section:
                    code_lines.append(line)
                continue

            # 检查是否是Python代码行
            is_code_line = any(keyword in stripped_line for keyword in python_keywords)

            if is_code_line:
                in_code_section = True
                code_lines.append(line)
            elif in_code_section:
                # 如果已经在代码段中，继续添加（可能是代码的一部分）
                if stripped_line and not stripped_line.startswith('**') and not stripped_line.startswith('##'):
                    code_lines.append(line)
                else:
                    # 遇到格式化文本，停止代码提取
                    break

        if code_lines:
            return '\n'.join(code_lines).strip()

        # 方法4: 如果以上都失败，尝试清理文本
        cleaned_text = CodeExtractor.clean_text(text)
        if cleaned_text and CodeExtractor.looks_like_python_code(cleaned_text):
            return cleaned_text

        return None

    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本，移除非代码内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # 跳过明显的非代码行
            if (
                    stripped.startswith('**') or
                    stripped.startswith('##') or
                    stripped.startswith('###') or
                    stripped.startswith('请') or
                    stripped.startswith('以下') or
                    stripped.startswith('根据') or
                    '代码如下' in stripped or
                    '解决方案' in stripped or
                    '实现如下' in stripped
            ):
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    @staticmethod
    def looks_like_python_code(text: str) -> bool:
        """判断文本是否看起来像Python代码
        
        Args:
            text: 要判断的文本
            
        Returns:
            是否像Python代码
        """
        if not text:
            return False

        # 检查是否包含Python特征
        python_features = [
            'input_data',
            'print(',
            'def ',
            'import ',
            'from ',
            'if ',
            'for ',
            'while ',
            '=',
            ':'
        ]

        feature_count = sum(1 for feature in python_features if feature in text)
        return feature_count >= 2

    @staticmethod
    def fix_common_issues(code: str) -> str:
        """修复常见的代码问题
        
        Args:
            code: 原始代码
            
        Returns:
            修复后的代码
        """
        if not code:
            return code

        # 替换input()为input_data的使用
        # 匹配各种input()的使用模式
        patterns = [
            (r'input\(\)', 'input_data'),
            (r'input\(".*?"\)', 'input_data'),
            (r'input\(\'.*?\'\)', 'input_data'),
            (r'float\(input\(\)\)', 'float(input_data)'),
            (r'int\(input\(\)\)', 'int(input_data)'),
            (r'input\(\)\.strip\(\)', 'input_data.strip()'),
            (r'input\(\)\.split\(\)', 'input_data.split()'),
        ]

        fixed_code = code
        for pattern, replacement in patterns:
            fixed_code = re.sub(pattern, replacement, fixed_code)

        return fixed_code


# 便捷函数
def extract_code_from_response(response_text: str) -> Optional[str]:
    """从DeepSeek响应中提取代码的便捷函数
    
    Args:
        response_text: DeepSeek的响应文本
        
    Returns:
        提取并修复的Python代码
    """
    extracted = CodeExtractor.extract_python_code(response_text)
    if extracted:
        return CodeExtractor.fix_common_issues(extracted)
    return None


def clean_and_extract_code(response_text: str) -> str:
    """清理并提取代码，如果提取失败则返回原文本
    
    Args:
        response_text: DeepSeek的响应文本
        
    Returns:
        提取的代码或清理后的原文本
    """
    extracted = extract_code_from_response(response_text)
    if extracted:
        return extracted

    # 如果提取失败，至少清理一下文本
    cleaned = CodeExtractor.clean_text(response_text)
    return CodeExtractor.fix_common_issues(cleaned) if cleaned else response_text
