#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek 提示词模板
功能：生成发送给DeepSeek的提示词
"""


def generate_coding_prompt(problem_description: str, test_data: str) -> str:
    """生成编程题解题提示词
    
    Args:
        problem_description: 题目描述
        test_data: 当前测试数据
        
    Returns:
        完整的提示词
    """

    prompt = f"""你是一个编程助手，我正在写一个刷题网站的测试数据生成器，请根据以下信息为我生成解题代码。

**重要：数据输入方式**
- 输入数据是字符串 input_data，main函数外已经被我定义，我会直接调用你给的函数得到返回值作为解题结果，你不能给它重新赋值，也不需要额外引入
- 绝对禁止使用 input、print 函数
- 如一定必要，允许main调用函数辅助

**题目描述：**
{problem_description.strip()}

**代码要求：**
1. 只返回可执行的Python代码，不要包含任何解释或注释
2. 确保代码能够正确处理给定的测试数据格式
3. 代码要简洁高效

"""

    return prompt


def generate_debug_prompt(problem_description: str, test_data: str, current_code: str, error_message: str) -> str:
    """生成调试代码的提示词
    
    Args:
        problem_description: 题目描述
        test_data: 测试数据
        current_code: 当前代码
        error_message: 错误信息
        
    Returns:
        调试提示词
    """

    prompt = f"""请帮我修复以下代码中的错误。

**题目描述：**
{problem_description.strip()}

**测试数据：**
```
{test_data.strip()}
```

**当前代码：**
```python
{current_code.strip()}
```

**错误信息：**
{error_message}

**要求：**
1. 只返回修复后的完整Python代码
2. 不要包含任何解释或注释
3. 确保代码能够正确处理测试数据
4. 使用print()输出最终结果

请直接返回修复后的代码："""

    return prompt


def generate_optimization_prompt(problem_description: str, test_data: str, current_code: str) -> str:
    """生成代码优化的提示词
    
    Args:
        problem_description: 题目描述
        test_data: 测试数据
        current_code: 当前代码
        
    Returns:
        优化提示词
    """

    prompt = f"""请帮我优化以下代码，使其更加高效和简洁。

**题目描述：**
{problem_description.strip()}

**测试数据：**
```
{test_data.strip()}
```

**当前代码：**
```python
{current_code.strip()}
```

**要求：**
1. 只返回优化后的完整Python代码
2. 保持功能不变，但提高效率和可读性
3. 不要包含任何解释或注释
4. 使用print()输出最终结果

请直接返回优化后的代码："""

    return prompt


def generate_test_data_prompt(topic):
    prompt = f"""请生成一个名为generate_data的Python函数，该函数用于生成刷题网站的测试数据。要求如下：
1. 严格考虑边界情况（包括最小/最大值、特殊条件等）。
2. 函数名必须为generate_data且不能更改。
3. 返回结果必须严格保留题目要求的空格和换行格式。
4. 禁止使用map函数。
5. 所有依赖包必须在函数内部导入。

题目要求：{topic.strip()}

输出完整generate_data函数代码，不要包含任何额外解释。
    """
    return prompt
