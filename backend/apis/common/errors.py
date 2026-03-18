"""
错误处理模块 - 统一的错误分类和HTTP状态码
"""
from enum import Enum
from flask import jsonify
from functools import wraps

class ErrorCode(Enum):
    """错误代码枚举"""
    # 通用错误 (1xxx)
    UNKNOWN_ERROR = (1000, "未知错误")
    INVALID_PARAMETER = (1001, "参数无效")
    MISSING_PARAMETER = (1002, "缺少必需参数")
    INVALID_FORMAT = (1003, "格式错误")
    
    # 认证错误 (2xxx)
    UNAUTHORIZED = (2001, "未授权")
    INVALID_TOKEN = (2002, "Token无效")
    TOKEN_EXPIRED = (2003, "Token已过期")
    INVALID_CREDENTIALS = (2004, "用户名或密码错误")
    INSUFFICIENT_PERMISSION = (2005, "权限不足")
    
    # 资源错误 (3xxx)
    NOT_FOUND = (3001, "资源不存在")
    ALREADY_EXISTS = (3002, "资源已存在")
    RESOURCE_CONFLICT = (3003, "资源冲突")
    
    # 业务逻辑错误 (4xxx)
    INVALID_STATE = (4001, "状态无效")
    OPERATION_FAILED = (4002, "操作失败")
    DATA_VALIDATION_ERROR = (4003, "数据验证失败")
    
    # 服务器错误 (5xxx)
    INTERNAL_ERROR = (5001, "服务器内部错误")
    DATABASE_ERROR = (5002, "数据库错误")
    EXTERNAL_SERVICE_ERROR = (5003, "外部服务错误")

class AppError(Exception):
    """应用错误基类"""
    def __init__(self, error_code: ErrorCode, message: str = None, details: dict = None):
        self.error_code = error_code
        self.code = error_code.value[0]
        self.message = message or error_code.value[1]
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppError):
    """验证错误"""
    def __init__(self, message: str, field: str = None):
        super().__init__(ErrorCode.INVALID_PARAMETER, message)
        if field:
            self.details['field'] = field

class AuthenticationError(AppError):
    """认证错误"""
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.UNAUTHORIZED, message)

class AuthorizationError(AppError):
    """授权错误"""
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.INSUFFICIENT_PERMISSION, message)

class NotFoundError(AppError):
    """资源不存在错误"""
    def __init__(self, resource: str = "资源"):
        super().__init__(ErrorCode.NOT_FOUND, f"{resource}不存在")

class ConflictError(AppError):
    """资源冲突错误"""
    def __init__(self, message: str = "资源已存在"):
        super().__init__(ErrorCode.ALREADY_EXISTS, message)

class DatabaseError(AppError):
    """数据库错误"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(ErrorCode.DATABASE_ERROR, message)

class InvalidStateError(AppError):
    """状态无效错误"""
    def __init__(self, message: str):
        super().__init__(ErrorCode.INVALID_STATE, message)


def handle_app_error(error: AppError):
    """处理应用错误"""
    response = {
        'success': False,
        'error': {
            'code': error.code,
            'message': error.message,
        }
    }
    if error.details:
        response['error']['details'] = error.details
    
    # 根据错误类型确定HTTP状态码
    if error.error_code in [ErrorCode.UNAUTHORIZED, ErrorCode.INVALID_TOKEN, 
                            ErrorCode.TOKEN_EXPIRED, ErrorCode.INVALID_CREDENTIALS]:
        status_code = 401
    elif error.error_code in [ErrorCode.INSUFFICIENT_PERMISSION]:
        status_code = 403
    elif error.error_code in [ErrorCode.NOT_FOUND, ErrorCode.ALREADY_EXISTS]:
        status_code = 409
    elif error.error_code in [ErrorCode.INVALID_PARAMETER, ErrorCode.MISSING_PARAMETER,
                              ErrorCode.INVALID_FORMAT, ErrorCode.DATA_VALIDATION_ERROR]:
        status_code = 400
    else:
        status_code = 500
    
    return jsonify(response), status_code


def handle_generic_error(error: Exception):
    """处理通用错误"""
    response = {
        'success': False,
        'error': {
            'code': ErrorCode.UNKNOWN_ERROR.value[0],
            'message': str(error)
        }
    }
    return jsonify(response), 500


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(AppError)
    def handle_app_error_handler(error):
        return handle_app_error(error)
    
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            'success': False,
            'error': {
                'code': ErrorCode.NOT_FOUND.value[0],
                'message': '请求的路由不存在'
            }
        }), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({
            'success': False,
            'error': {
                'code': ErrorCode.INTERNAL_ERROR.value[0],
                'message': '服务器内部错误'
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        return handle_generic_error(error)


def require_fields(*fields):
    """装饰器：检查必需字段"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            data = request.get_json() or {}
            missing = [f for f in fields if f not in data or data[f] is None]
            if missing:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': ErrorCode.MISSING_PARAMETER.value[0],
                        'message': f"缺少必需字段: {', '.join(missing)}",
                        'details': {'missing_fields': missing}
                    }
                }), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator
