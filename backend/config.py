"""
后端配置模块
"""
import os
import secrets

class Config:
    """基础配置"""
    # SECRET_KEY: 生产环境必须设置环境变量 SECRET_KEY
    # 开发环境使用自动生成的随机密钥
    _secret_key = os.environ.get('SECRET_KEY')
    if _secret_key:
        SECRET_KEY = _secret_key
    else:
        # 开发环境：生成临时密钥
        SECRET_KEY = secrets.token_hex(32)
        print("WARNING: Running in development mode. Set SECRET_KEY environment variable for production.")

    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'data', 'interview_system.db')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    # 上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
