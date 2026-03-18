"""
工具函数模块 - 通用的工具函数
"""

from flask import jsonify
from datetime import datetime
import json

def format_response(success=True, data=None, message=None, error=None, status_code=200):
    """
    格式化API响应
    
    Args:
        success (bool): 是否成功
        data: 响应数据
        message (str): 成功消息
        error (str): 错误消息
        status_code (int): HTTP状态码
        
    Returns:
        Flask Response对象
    """
    response_data = {
        'success': success,
        'timestamp': datetime.now().isoformat()
    }
    
    if success:
        if data is not None:
            response_data['data'] = data
        if message:
            response_data['message'] = message
    else:
        response_data['error'] = {
            'message': error or '未知错误'
        }
    
    return jsonify(response_data), status_code

def validate_request(request_data, required_fields):
    """
    验证请求数据
    
    Args:
        request_data (dict): 请求数据
        required_fields (list): 必需字段列表
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not request_data:
        return False, "请求数据不能为空"
    
    missing_fields = []
    for field in required_fields:
        if field not in request_data or request_data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    return True, None

def parse_json_field(json_str, default=None):
    """
    解析JSON字段
    
    Args:
        json_str: JSON字符串
        default: 默认值
        
    Returns:
        解析后的数据
    """
    if not json_str:
        return default
    
    try:
        if isinstance(json_str, str):
            return json.loads(json_str)
        return json_str
    except (json.JSONDecodeError, TypeError):
        return default

def format_question_data(question_row, question_type):
    """
    格式化题目数据
    
    Args:
        question_row: 数据库查询结果行
        question_type (str): 题目类型
        
    Returns:
        dict: 格式化后的题目数据
    """
    content = parse_json_field(question_row['question_data'], [])
    
    # 处理sqlite3.Row对象，使用try-except来安全访问字段
    def safe_get(row, key, default=None):
        try:
            return row[key]
        except (KeyError, IndexError):
            return default

    result = {
        'id': question_row['id'],
        'index': question_row['question_index'],
        'type': question_type,
        'content': content,
        'isActive': True,
        'is_used': safe_get(question_row, 'is_used', 0)
    }

    # 专业题额外字段
    if question_type == 'professional':
        result.update({
            'difficulty': safe_get(question_row, 'difficulty', 'medium'),
            'subject': safe_get(question_row, 'subject', 'computer_science')
        })
    
    return result

def calculate_pagination(total_count, page, limit):
    """
    计算分页信息
    
    Args:
        total_count (int): 总记录数
        page (int): 当前页码
        limit (int): 每页记录数
        
    Returns:
        dict: 分页信息
    """
    total_pages = (total_count + limit - 1) // limit
    offset = (page - 1) * limit
    
    return {
        'total': total_count,
        'page': page,
        'limit': limit,
        'totalPages': total_pages,
        'offset': offset,
        'hasNext': page < total_pages,
        'hasPrev': page > 1
    }
