#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 客户端
功能：处理与DeepSeek API的通信
"""

import requests
import json
import time
from typing import Generator, Optional, Dict, Any


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def check_network(self) -> bool:
        """检查网络连接"""
        try:
            response = requests.get("https://www.baidu.com", timeout=5)
            return response.status_code == 200
        except:
            return False

    def chat_completion_stream(self, messages: list, model: str = "deepseek-chat") -> Generator[str, None, None]:
        """流式聊天完成"""
        print("[DEBUG] DeepSeek API chat_completion_stream() 被调用")
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "temperature": 0.1,  # 降低温度以获得更稳定的代码输出
            "max_tokens": 4000
        }

        print(f"[DEBUG] 发送API请求到: {url}")
        print(f"[DEBUG] 请求消息数量: {len(messages)}")

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=30
            )

            print(f"[DEBUG] API响应状态码: {response.status_code}")

            if response.status_code != 200:
                yield f"API调用失败: {response.status_code} - {response.text}"
                return

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 去掉 'data: ' 前缀

                        if data_str.strip() == '[DONE]':
                            break

                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            yield f"网络请求错误: {str(e)}"
        except Exception as e:
            yield f"未知错误: {str(e)}"

    def validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "hello"}],
            "stream": False,
            "max_tokens": 10
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
