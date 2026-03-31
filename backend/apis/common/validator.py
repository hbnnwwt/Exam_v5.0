"""
输入验证模块 - 统一的输入验证和清理
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(message)

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_student_number(value: str) -> Tuple[bool, str]:
        """验证学生编号"""
        if not value:
            return False, "学生编号不能为空"
        if not re.match(r'^\d{1,3}$', value):
            return False, "学生编号必须是1-3位数字"
        return True, None
    
    @staticmethod
    def validate_name(value: str) -> Tuple[bool, str]:
        """验证姓名"""
        if value and len(value) > 50:
            return False, "姓名长度不能超过50个字符"
        return True, None
    
    @staticmethod
    def validate_email(value: str) -> Tuple[bool, str]:
        """验证邮箱"""
        if not value:
            return True, None  # 邮箱可选
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "邮箱格式不正确"
        return True, None
    
    @staticmethod
    def validate_phone(value: str) -> Tuple[bool, str]:
        """验证手机号"""
        if not value:
            return True, None  # 手机号可选
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, value):
            return False, "手机号格式不正确"
        return True, None
    
    @staticmethod
    def validate_id_card(value: str) -> Tuple[bool, str]:
        """验证身份证号"""
        if not value:
            return True, None  # 身份证号可选
        pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
        if not re.match(pattern, value):
            return False, "身份证号格式不正确"
        return True, None
    
    @staticmethod
    def validate_question_index(value: int) -> Tuple[bool, str]:
        """验证题目编号"""
        if not isinstance(value, int):
            return False, "题目编号必须是整数"
        if value < 1 or value > 999:
            return False, "题目编号必须在1-999之间"
        return True, None
    
    @staticmethod
    def validate_subject(value: str) -> Tuple[bool, str]:
        """验证专业科目"""
        valid_subjects = ['computer_science', 'software_engineering', 
                         'information_security', 'data_science']
        if value and value not in valid_subjects:
            return False, f"无效的专业科目: {value}"
        return True, None
    
    @staticmethod
    def validate_difficulty(value: str) -> Tuple[bool, str]:
        """验证难度等级"""
        valid_difficulties = ['easy', 'medium', 'hard']
        if value and value not in valid_difficulties:
            return False, f"无效的难度等级: {value}"
        return True, None
    
    @staticmethod
    def validate_exam_status(value: str) -> Tuple[bool, str]:
        """验证考试状态"""
        valid_statuses = ['ready', 'in_progress', 'paused', 'completed', 'abandoned']
        if value and value not in valid_statuses:
            return False, f"无效的考试状态: {value}"
        return True, None
    
    @staticmethod
    def validate_json_string(value: str, max_length: int = 10000) -> Tuple[bool, str]:
        """验证JSON字符串"""
        if not value:
            return True, None
        if len(value) > max_length:
            return False, f"JSON数据长度不能超过{max_length}个字符"
        try:
            import json
            json.loads(value)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"无效的JSON格式: {str(e)}"
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """清理字符串输入"""
        if not value:
            return ""
        # 移除控制字符
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        # 限制长度
        return value[:max_length]
    
    @staticmethod
    def validate_positive_integer(value: Any) -> Tuple[bool, str]:
        """验证正整数"""
        try:
            num = int(value)
            if num < 1:
                return False, "必须是正整数"
            return True, None
        except (ValueError, TypeError):
            return False, "必须是有效的整数"
    
    @staticmethod
    def validate_range(value: Any, min_val: int, max_val: int) -> Tuple[bool, str]:
        """验证数值范围"""
        try:
            num = int(value)
            if num < min_val or num > max_val:
                return False, f"数值必须在{min_val}-{max_val}之间"
            return True, None
        except (ValueError, TypeError):
            return False, "必须是有效的整数"


def validate_student_data(data: Dict) -> Tuple[bool, str, Dict]:
    """
    验证学生数据
    
    Args:
        data: 学生数据字典
        
    Returns:
        tuple: (is_valid, error_message, cleaned_data)
    """
    if not data:
        return False, "数据不能为空", {}
    
    cleaned = {}
    errors = []
    
    # 学生编号
    if 'studentNumber' in data:
        valid, err = InputValidator.validate_student_number(data['studentNumber'])
        if not valid:
            errors.append(err)
        else:
            cleaned['studentNumber'] = data['studentNumber']
    
    # 姓名
    if 'name' in data:
        valid, err = InputValidator.validate_name(data['name'])
        if not valid:
            errors.append(err)
        else:
            cleaned['name'] = InputValidator.sanitize_string(data['name'])
    
    # 邮箱
    if 'email' in data:
        valid, err = InputValidator.validate_email(data['email'])
        if not valid:
            errors.append(err)
        else:
            cleaned['email'] = data['email']
    
    # 手机号
    if 'phone' in data:
        valid, err = InputValidator.validate_phone(data['phone'])
        if not valid:
            errors.append(err)
        else:
            cleaned['phone'] = data['phone']
    
    # 身份证号
    if 'idCard' in data:
        valid, err = InputValidator.validate_id_card(data['idCard'])
        if not valid:
            errors.append(err)
        else:
            cleaned['idCard'] = data['idCard']
    
    # 当前步骤
    if 'currentStep' in data:
        valid, err = InputValidator.validate_range(data['currentStep'], 1, 10)
        if not valid:
            errors.append(err)
        else:
            cleaned['currentStep'] = data['currentStep']
    
    # 考试状态
    if 'examStatus' in data:
        valid, err = InputValidator.validate_exam_status(data['examStatus'])
        if not valid:
            errors.append(err)
        else:
            cleaned['examStatus'] = data['examStatus']
    
    # 其他字段直接复制
    for key in ['translationQuestion', 'professionalQuestion', 
                'professionalSubject', 'stepData', 'startTime', 'endTime']:
        if key in data:
            cleaned[key] = data[key]
    
    if errors:
        return False, "; ".join(errors), cleaned
    
    return True, None, cleaned


def validate_question_data(data: Dict, question_type: str) -> Tuple[bool, str, Dict]:
    """
    验证题目数据
    
    Args:
        data: 题目数据字典
        question_type: 题目类型 ('translation' 或 'professional')
        
    Returns:
        tuple: (is_valid, error_message, cleaned_data)
    """
    if not data:
        return False, "数据不能为空", {}
    
    cleaned = {}
    errors = []
    
    # 题目编号
    if 'questionIndex' in data:
        valid, err = InputValidator.validate_question_index(data['questionIndex'])
        if not valid:
            errors.append(err)
        else:
            cleaned['questionIndex'] = data['questionIndex']
    
    if question_type == 'professional':
        # 专业题：验证科目和难度
        if 'subject' in data:
            valid, err = InputValidator.validate_subject(data['subject'])
            if not valid:
                errors.append(err)
            else:
                cleaned['subject'] = data['subject']
        
        if 'difficulty' in data:
            valid, err = InputValidator.validate_difficulty(data['difficulty'])
            if not valid:
                errors.append(err)
            else:
                cleaned['difficulty'] = data['difficulty']
    
    # 题目数据JSON
    if 'questionData' in data:
        if isinstance(data['questionData'], str):
            valid, err = InputValidator.validate_json_string(data['questionData'])
            if not valid:
                errors.append(err)
            else:
                cleaned['questionData'] = data['questionData']
        else:
            # 如果是字典，转换为JSON字符串
            import json
            cleaned['questionData'] = json.dumps(data['questionData'], ensure_ascii=False)
    
    if errors:
        return False, "; ".join(errors), cleaned
    
    return True, None, cleaned
