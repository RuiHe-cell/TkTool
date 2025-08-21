#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试提示词模板和代码提取功能
"""

from deepseek_api.prompt_template import generate_coding_prompt
from deepseek_api.code_extractor import extract_code_from_response, clean_and_extract_code

def test_prompt_template():
    """测试提示词模板"""
    print("=== 测试提示词模板 ===")
    print()
    
    problem_description = "将开尔文温度转换为摄氏度和华氏度，如果华氏度超过212度则输出警告"
    test_data = "373.15"
    
    prompt = generate_coding_prompt(problem_description, test_data)
    print("生成的提示词:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()

def test_code_extraction():
    """测试代码提取功能"""
    print("=== 测试代码提取功能 ===")
    print()
    
    # 测试用例1: 包含```python```代码块的响应
    response1 = """根据您的要求，我来为您生成代码：

```python
input_data = "373.15"
K = float(input_data)
C = K - 273.15
F = C * 1.8 + 32
if F > 212:
    print("Temperature is too high!")
else:
    print(f"{C:.2f} {F:.2f}")
```

这段代码可以正确处理温度转换。"""
    
    print("测试用例1 - 标准代码块:")
    extracted1 = extract_code_from_response(response1)
    print("提取结果:")
    print(extracted1)
    print()
    
    # 测试用例2: 包含input()的错误代码
    response2 = """```python
input_data = float(input())
C = input_data - 273.15
F = C * 1.8 + 32
if F > 212:
    print("Temperature is too high!")
else:
    print("{:.2f} {:.2f}".format(C, F))
```"""
    
    print("测试用例2 - 包含input()的错误代码:")
    extracted2 = extract_code_from_response(response2)
    print("提取并修复结果:")
    print(extracted2)
    print()
    
    # 测试用例3: 混合文本和代码
    response3 = """好的，我来帮您解决这个问题。

首先分析题目要求：
- 输入开尔文温度
- 转换为摄氏度和华氏度
- 判断华氏度是否超过212度

input_data = "373.15"
K = float(input_data)
C = K - 273.15
F = C * 1.8 + 32
if F > 212:
    print("Temperature is too high!")
else:
    print(f"{C:.2f} {F:.2f}")

这样就可以了。"""
    
    print("测试用例3 - 混合文本和代码:")
    extracted3 = clean_and_extract_code(response3)
    print("清理并提取结果:")
    print(extracted3)
    print()

def test_input_replacement():
    """测试input()替换功能"""
    print("=== 测试input()替换功能 ===")
    print()
    
    test_codes = [
        "x = input()",
        "x = int(input())",
        "x = float(input())",
        "data = input().strip()",
        "parts = input().split()",
        'name = input("Enter name: ")',
        "x = input('Enter number: ')"
    ]
    
    from deepseek_api.code_extractor import CodeExtractor
    
    for code in test_codes:
        fixed = CodeExtractor.fix_common_issues(code)
        print(f"原始: {code}")
        print(f"修复: {fixed}")
        print()

def main():
    """主函数"""
    print("提示词模板和代码提取功能测试")
    print("=" * 50)
    print()
    
    test_prompt_template()
    test_code_extraction()
    test_input_replacement()
    
    print("测试完成！")

if __name__ == "__main__":
    main()