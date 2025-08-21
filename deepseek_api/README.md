# DeepSeek API 集成功能

## 功能概述

本模块为数据生成器添加了DeepSeek AI助手功能，可以帮助用户自动生成解题代码。

## 功能特性

- 🤖 **智能代码生成**: 基于问题描述和测试数据生成高质量Python代码
- 🔄 **流式响应**: 实时显示AI生成过程，提供更好的用户体验
- 🔒 **安全存储**: 使用keyring库和系统密钥环加密存储API密钥
- 🌐 **网络检测**: 自动检测网络连接和API可用性
- 📋 **便捷操作**: 支持代码复制功能
- 🔧 **错误处理**: 完善的异常处理和用户提示
- 🛡️ **隐私保护**: 用户级密钥隔离，系统级加密

## 使用方法

### 1. 获取API密钥

1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 注册并登录账户
3. 在API密钥页面创建新的密钥
4. 复制密钥备用

### 2. 使用DeepSeek功能

1. 在数据生成器中生成测试数据
2. 在解题代码编辑器中点击"问问DeepSeek"按钮
3. 首次使用时输入API密钥（会自动保存）
4. 输入题目描述
5. 等待AI生成代码
6. 复制或直接应用生成的代码

### 3. 提示词模板

系统会自动生成包含以下信息的提示词：
- 使用方式说明
- 当前测试数据（保持格式）
- 题目描述
- 代码要求

## 文件结构

```
deepseek_api/
├── __init__.py              # 模块初始化
├── deepseek_client.py       # DeepSeek API客户端
├── deepseek_dialog.py       # 对话窗口界面
├── prompt_template.py       # 提示词模板
├── api_key_manager.py       # API密钥管理
└── README.md               # 说明文档
```

## 模块说明

### deepseek_client.py
- `DeepSeekClient`: 处理与DeepSeek API的通信
- 支持流式响应
- 网络连接检测
- API密钥验证

### deepseek_dialog.py
- `DeepSeekDialog`: 主对话窗口
- `ApiKeyDialog`: API密钥输入对话框
- 实时显示生成过程
- 代码复制和应用功能

### prompt_template.py
- `generate_coding_prompt`: 生成编程题提示词
- `generate_debug_prompt`: 生成调试提示词
- `generate_optimization_prompt`: 生成优化提示词

### api_key_manager.py
**API密钥管理模块**
- 使用keyring库进行API密钥的安全存储和读取
- 基于Windows系统密钥环（WinVault）加密存储
- 提供密钥验证和管理功能
- 支持用户级密钥隔离

## 安全说明

- API密钥使用Windows系统密钥环（WinVault）加密存储
- 密钥经过系统级加密，安全性更高
- 不会上传到任何远程服务器
- 用户级密钥隔离，保护隐私
- 建议定期更换API密钥
- 请妥善保管您的API密钥

## 注意事项

1. **API密钥安全**：密钥会加密存储在系统密钥环中，请勿泄露
2. **网络要求**：需要稳定的网络连接访问DeepSeek API
3. **使用限制**：请遵守DeepSeek API的使用条款和限制
4. **代码验证**：AI生成的代码仅供参考，请验证后使用

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查密钥格式是否正确
   - 确认密钥是否已激活
   - 验证账户余额是否充足

2. **密钥存储失败**
   - 确认keyring库已正确安装
   - 检查Windows凭据管理器是否可用
   - 尝试以管理员权限运行

3. **网络连接失败**
   - 检查网络连接
   - 确认防火墙设置
   - 尝试使用代理

4. **生成结果不理想**
   - 提供更详细的问题描述
   - 检查测试数据格式
   - 尝试重新生成

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的代码生成功能
- 集成流式响应界面
- 添加API密钥管理