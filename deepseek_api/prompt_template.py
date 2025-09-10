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

    prompt = f"""你是一个编程助手，正在为刷题网站生成测试数据对应的解题代码。请严格遵循以下要求：

**输入数据说明：**
- 变量 `input_data` 已在主函数外部定义为字符串，你的代码中可直接使用该变量，无需重新定义或赋值
- 绝对禁止使用 `input()`、`print()` 或任何外部输入输出函数
- 绝对禁止使用  `map()` 函数
- 如需要，可在 `main` 函数内部调用其他辅助函数

**代码生成要求：**
1. 只输出可执行的Python代码，不含任何注释或解释性文本
2. 代码需准确处理字符串格式的输入数据，非必要不做算法优化，需要返回正确结果
3. 函数结构必须为无参数且有返回值的 `main()` 函数，返回值即你的解题结果，直接使用已定义的 `input_data` 变量

**绝对禁止的输出示例：**
```python
# 这是一段解题代码 （任何注释都不允许）
def main(input_data): # 错误：函数不能带参数
    data = input_data.split()
    result = sum(map(int, data)) # 错误：禁止使用map函数
    print(result) # 错误：禁止使用print函数
    # 错误: 没有返回值
```

**题目描述：**
{problem_description.strip()}

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
