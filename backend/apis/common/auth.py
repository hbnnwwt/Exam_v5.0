"""
认证授权模块 - 提供API认证和授权功能
"""
import os
import hashlib
import secrets
import functools
from flask import request, g, current_app
from datetime import datetime, timedelta

# 简单的内存Token存储（生产环境建议使用Redis）
_token_store = {}

def generate_token():
    """生成随机Token"""
    return secrets.token_hex(32)

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash

def create_token(user_id, expires_hours=24):
    """创建认证Token"""
    token = generate_token()
    expires_at = datetime.now() + timedelta(hours=expires_hours)
    _token_store[token] = {
        'user_id': user_id,
        'expires_at': expires_at.isoformat()
    }
    return token

def verify_token(token):
    """验证Token是否有效"""
    if not token:
        return None
    
    token_data = _token_store.get(token)
    if not token_data:
        return None
    
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    if datetime.now() > expires_at:
        # Token过期，删除它
        del _token_store[token]
        return None
    
    return token_data['user_id']

def get_token_from_header():
    """从请求头获取Token"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

def login_required(f):
    """登录_required装饰器 - 保护API接口"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        user_id = verify_token(token)
        
        if not user_id:
            from flask import jsonify
            return jsonify({
                'success': False,
                'error': {'message': '未授权访问，请先登录'}
            }), 401
        
        g.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """optional_auth装饰器 - 可选的认证（不强制要求登录）"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        user_id = verify_token(token)
        g.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function

# 默认管理员账户（开发环境使用）
# 生产环境请通过环境变量设置
DEFAULT_ADMIN = {
    'username': os.environ.get('ADMIN_USERNAME', 'admin'),
    'password_hash': hash_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
}

def authenticate(username, password):
    """验证用户名密码"""
    # 检查默认管理员
    if username == DEFAULT_ADMIN['username'] and verify_password(password, DEFAULT_ADMIN['password_hash']):
        return 'admin'
    return None

def get_authBlueprint():
    """创建认证蓝图"""
    from flask import Blueprint, jsonify
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        """登录接口"""
        from apis.common.utils import format_response
        data = request.get_json()
        
        if not data:
            return format_response(success=False, error='请求数据不能为空', status_code=400)
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return format_response(success=False, error='用户名和密码不能为空', status_code=400)
        
        user_id = authenticate(username, password)
        if user_id:
            token = create_token(user_id)
            return format_response(
                success=True,
                data={'token': token, 'user': user_id},
                message='登录成功'
            )
        
        return format_response(success=False, error='用户名或密码错误', status_code=401)
    
    @auth_bp.route('/logout', methods=['POST'])
    @login_required
    def logout():
        """登出接口"""
        from apis.common.utils import format_response
        token = get_token_from_header()
        if token in _token_store:
            del _token_store[token]
        return format_response(success=True, message='登出成功')
    
    @auth_bp.route('/verify', methods=['GET'])
    @login_required
    def verify():
        """验证Token"""
        from apis.common.utils import format_response
        return format_response(
            success=True,
            data={'user': g.user_id},
            message='Token有效'
        )
    
    @auth_bp.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        """修改密码"""
        from apis.common.utils import format_response
        data = request.get_json()
        
        if not data:
            return format_response(success=False, error='请求数据不能为空', status_code=400)
        
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')
        
        if not old_password or not new_password:
            return format_response(success=False, error='旧密码和新密码不能为空', status_code=400)
        
        # 验证旧密码
        if not verify_password(old_password, DEFAULT_ADMIN['password_hash']):
            return format_response(success=False, error='旧密码错误', status_code=400)
        
        # 更新密码（仅对默认管理员有效）
        DEFAULT_ADMIN['password_hash'] = hash_password(new_password)
        
        return format_response(success=True, message='密码修改成功')
    
    return auth_bp
