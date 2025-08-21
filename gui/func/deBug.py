import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import traceback

# 全局配置
DE_BUG = False  # 是否启用调试模式
DEBUG_LEVEL = 0  # 调试级别，数字越大，输出的信息越详细
SAVE_LOG = False  # 是否保存日志到文件
CONSOLE_OUTPUT = True  # 是否在控制台输出日志

# 日志文件配置
LOG_DIR = "logs"  # 日志目录
LOG_FILE = "app.log"  # 日志文件名
MAX_LOG_SIZE = 5 * 1024 * 1024  # 单个日志文件最大大小（5MB）
BACKUP_COUNT = 3  # 保留的日志文件数量

# 日志级别映射
LEVEL_MAP = {
    0: logging.ERROR,    # 只记录错误
    1: logging.WARNING,  # 记录警告和错误
    2: logging.INFO,     # 记录信息、警告和错误
    3: logging.DEBUG     # 记录所有内容，包括调试信息
}

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志记录器
logger = None


def init(debug_mode=None, debug_level=None, save_log=None, console_output=None, log_dir=None):
    """
    初始化日志系统
    
    Args:
        debug_mode (bool, optional): 是否启用调试模式
        debug_level (int, optional): 调试级别 (0-3)
        save_log (bool, optional): 是否保存日志到文件
        console_output (bool, optional): 是否在控制台输出日志
        log_dir (str, optional): 日志目录路径
    """
    global DE_BUG, DEBUG_LEVEL, SAVE_LOG, CONSOLE_OUTPUT, LOG_DIR, logger
    
    # 更新全局配置（如果提供了参数）
    if debug_mode is not None:
        DE_BUG = debug_mode
    if debug_level is not None:
        DEBUG_LEVEL = max(0, min(3, debug_level))  # 确保级别在0-3之间
    if save_log is not None:
        SAVE_LOG = save_log
    if console_output is not None:
        CONSOLE_OUTPUT = console_output
    if log_dir is not None:
        LOG_DIR = log_dir
    
    # 创建日志记录器
    logger = logging.getLogger("TKTool")
    logger.setLevel(LEVEL_MAP.get(DEBUG_LEVEL, logging.ERROR))
    logger.handlers = []  # 清除所有处理器，防止重复初始化
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 添加控制台处理器
    if CONSOLE_OUTPUT:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 添加文件处理器
    if SAVE_LOG:
        try:
            # 确保日志目录存在
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), LOG_DIR)
            if not os.path.exists(log_path):
                os.makedirs(log_path)
            
            # 创建日志文件路径
            log_file_path = os.path.join(log_path, LOG_FILE)
            
            # 创建旋转文件处理器
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=MAX_LOG_SIZE,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # 如果创建文件处理器失败，记录错误并继续
            if CONSOLE_OUTPUT:
                print(f"无法创建日志文件: {str(e)}")
    
    # 记录初始化信息
    if DE_BUG:
        logger.info(f"日志系统初始化完成 [级别: {DEBUG_LEVEL}, 文件记录: {SAVE_LOG}, 控制台输出: {CONSOLE_OUTPUT}]")


def debug(message: str, title: str = None, level: int = 0, exc_info=None):
    """
    记录调试信息
    
    Args:
        message (str): 调试信息内容
        title (str, optional): 调试信息标题
        level (int, optional): 调试级别，只有当全局DEBUG_LEVEL >= level时才会记录
        exc_info (Exception, optional): 异常信息，如果提供则会记录异常堆栈
    """
    global logger
    
    # 如果日志系统未初始化，则初始化
    if logger is None:
        init()
    
    # 如果调试模式关闭或级别不足，则不记录
    if not DE_BUG or level > DEBUG_LEVEL:
        return
    
    # 格式化消息
    formatted_message = message
    if title:
        formatted_message = f"[{title}] {formatted_message}"
    
    # 根据级别记录日志
    if level == 0:
        logger.error(formatted_message, exc_info=exc_info)
    elif level == 1:
        logger.warning(formatted_message, exc_info=exc_info)
    elif level == 2:
        logger.info(formatted_message, exc_info=exc_info)
    else:  # level >= 3
        logger.debug(formatted_message, exc_info=exc_info)


def error(message: str, title: str = None, exc_info=None):
    """
    记录错误信息
    
    Args:
        message (str): 错误信息内容
        title (str, optional): 错误信息标题
        exc_info (Exception, optional): 异常信息，如果提供则会记录异常堆栈
    """
    debug(message, title, 0, exc_info)


def warning(message: str, title: str = None):
    """
    记录警告信息
    
    Args:
        message (str): 警告信息内容
        title (str, optional): 警告信息标题
    """
    debug(message, title, 1)


def info(message: str, title: str = None):
    """
    记录一般信息
    
    Args:
        message (str): 一般信息内容
        title (str, optional): 一般信息标题
    """
    debug(message, title, 2)


def verbose(message: str, title: str = None):
    """
    记录详细信息
    
    Args:
        message (str): 详细信息内容
        title (str, optional): 详细信息标题
    """
    debug(message, title, 3)


def exception(message: str, title: str = None, exc_info=None):
    """
    记录异常信息，包括堆栈跟踪
    
    Args:
        message (str): 异常信息内容
        title (str, optional): 异常信息标题
        exc_info (Exception, optional): 异常对象，如果为None则使用sys.exc_info()
    """
    if exc_info is None:
        exc_info = sys.exc_info()
    
    # 获取异常堆栈信息
    stack_trace = "".join(traceback.format_exception(*exc_info)) if exc_info[0] is not None else ""
    full_message = f"{message}\n{stack_trace}"
    
    debug(full_message, title, 0, False)  # 不使用exc_info参数，因为我们已经手动格式化了堆栈


def get_log_path():
    """
    获取当前日志文件的完整路径
    
    Returns:
        str: 日志文件的完整路径
    """
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), LOG_DIR, LOG_FILE)
    return log_path


def set_debug(enabled: bool):
    """
    设置调试模式
    
    Args:
        enabled (bool): 是否启用调试模式
    """
    global DE_BUG
    DE_BUG = enabled
    init()  # 重新初始化日志系统


def set_debug_level(level: int):
    """
    设置调试级别
    
    Args:
        level (int): 调试级别 (0-3)
    """
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, level))  # 确保级别在0-3之间
    init()  # 重新初始化日志系统


def set_save_log(enabled: bool):
    """
    设置是否保存日志到文件
    
    Args:
        enabled (bool): 是否保存日志到文件
    """
    global SAVE_LOG
    SAVE_LOG = enabled
    init()  # 重新初始化日志系统


def set_console_output(enabled: bool):
    """
    设置是否在控制台输出日志
    
    Args:
        enabled (bool): 是否在控制台输出日志
    """
    global CONSOLE_OUTPUT
    CONSOLE_OUTPUT = enabled
    init()  # 重新初始化日志系统
