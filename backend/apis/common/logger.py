"""
日志模块 - 统一的日志配置和管理
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')

def ensure_log_dir():
    """确保日志目录存在"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def setup_logger(name='exam_system', level=logging.INFO):
    """
    配置日志记录器
    
    Args:
        name (str): 日志记录器名称
        level: 日志级别
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    ensure_log_dir()
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 文件处理器（按日期滚动，最大10MB，保留5个备份）
    log_file = os.path.join(LOG_DIR, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 创建默认日志记录器
logger = setup_logger()

def log_request(request, response_status=200):
    """记录HTTP请求"""
    logger.info(
        f"HTTP {request.method} {request.path} - Status: {response_status} - "
        f"IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'Unknown')[:50]}"
    )

def log_error(error, context=None):
    """记录错误"""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" - Context: {context}"
    logger.error(error_msg, exc_info=True)

def log_security_event(event_type, details):
    """记录安全相关事件"""
    logger.warning(
        f"Security Event: {event_type} - Details: {details} - "
        f"IP: {request.remote_addr if hasattr(request, 'remote_addr') else 'Unknown'}"
    )

# 便捷函数
def get_logger(name=None):
    """获取日志记录器"""
    if name:
        return logging.getLogger(name)
    return logger
