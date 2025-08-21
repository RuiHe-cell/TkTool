import keyring
import getpass
from typing import Optional


class ApiKeyManager:
    """API密钥管理器，使用keyring库进行安全存储"""

    SERVICE_NAME = "TKTool_DeepSeek"
    USERNAME = "deepseek_api_key"

    @classmethod
    def save_api_key(cls, api_key: str) -> bool:
        """保存API密钥到系统密钥环
        
        Args:
            api_key: DeepSeek API密钥
            
        Returns:
            bool: 保存是否成功
        """
        try:
            keyring.set_password(cls.SERVICE_NAME, cls.USERNAME, api_key)
            return True
        except Exception as e:
            print(f"保存API密钥失败: {e}")
            return False

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """从系统密钥环获取API密钥
        
        Returns:
            Optional[str]: API密钥，如果不存在则返回None
        """
        try:
            api_key = keyring.get_password(cls.SERVICE_NAME, cls.USERNAME)
            return api_key
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            return None

    @classmethod
    def delete_api_key(cls) -> bool:
        """删除保存的API密钥
        
        Returns:
            bool: 删除是否成功
        """
        try:
            keyring.delete_password(cls.SERVICE_NAME, cls.USERNAME)
            return True
        except Exception as e:
            print(f"删除API密钥失败: {e}")
            return False

    @classmethod
    def has_api_key(cls) -> bool:
        """检查是否已保存API密钥
        
        Returns:
            bool: 是否存在API密钥
        """
        api_key = cls.get_api_key()
        return api_key is not None and api_key.strip() != ""

    @classmethod
    def prompt_for_api_key(cls) -> Optional[str]:
        """提示用户输入API密钥
        
        Returns:
            Optional[str]: 用户输入的API密钥，如果取消则返回None
        """
        try:
            print("请输入您的DeepSeek API密钥:")
            api_key = getpass.getpass("API Key: ")
            if api_key and api_key.strip():
                return api_key.strip()
            return None
        except KeyboardInterrupt:
            print("\n用户取消输入")
            return None
        except Exception as e:
            print(f"输入API密钥时出错: {e}")
            return None


# 便捷函数
def get_deepseek_api_key() -> Optional[str]:
    """获取DeepSeek API密钥的便捷函数
    
    Returns:
        Optional[str]: API密钥，如果不存在则返回None
    """
    return ApiKeyManager.get_api_key()


def save_deepseek_api_key(api_key: str) -> bool:
    """保存DeepSeek API密钥的便捷函数
    
    Args:
        api_key: API密钥
        
    Returns:
        bool: 保存是否成功
    """
    return ApiKeyManager.save_api_key(api_key)


def setup_api_key() -> Optional[str]:
    """设置API密钥的便捷函数
    
    如果已存在密钥则直接返回，否则提示用户输入并保存
    
    Returns:
        Optional[str]: API密钥
    """
    # 先尝试获取已保存的密钥
    api_key = ApiKeyManager.get_api_key()
    if api_key:
        return api_key

    # 如果没有保存的密钥，提示用户输入
    api_key = ApiKeyManager.prompt_for_api_key()
    if api_key:
        if ApiKeyManager.save_api_key(api_key):
            print("API密钥已安全保存")
            return api_key
        else:
            print("保存API密钥失败，但仍可使用当前会话")
            return api_key

    return None
