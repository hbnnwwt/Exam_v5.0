"""
批量操作模块 - 处理批量导入等操作
"""

from flask import Blueprint, request
from datetime import datetime
import json
from ..common.database import get_db_connection
from ..common.utils import format_response, validate_request

batch_bp = Blueprint('batch', __name__, url_prefix='/batch')

@batch_bp.route('/import', methods=['POST'])
def batch_import():
    """批量导入题目"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['type', 'questions'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )
        
        question_type = data.get('type')
        questions = data.get('questions', [])
        
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )
        
        if not questions:
            return format_response(
                success=False,
                error='题目列表不能为空',
                status_code=400
            )
        
        conn = get_db_connection()
        
        # 获取当前最大编号
        table_name = f"{question_type}_questions"
        cursor = conn.execute(f'''
            SELECT MAX(question_index) FROM {table_name}
        ''')
        max_index = cursor.fetchone()[0] or 0
        
        # 批量插入
        success_count = 0
        error_count = 0
        errors = []
        
        for i, question_data in enumerate(questions):
            try:
                next_index = max_index + i + 1
                content = question_data.get('content', [])
                content_json = json.dumps(content, ensure_ascii=False)
                
                if question_type == 'translation':
                    cursor = conn.execute('''
                        INSERT INTO translation_questions (question_index, question_data, created_at)
                        VALUES (?, ?, ?)
                    ''', (next_index, content_json, datetime.now().isoformat()))
                else:
                    difficulty = question_data.get('difficulty', 'medium')
                    subject = question_data.get('subject', 'computer_science')
                    
                    cursor = conn.execute('''
                        INSERT INTO professional_questions (question_index, question_data, difficulty, subject, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (next_index, content_json, difficulty, subject, datetime.now().isoformat()))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"第{i+1}题导入失败: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={
                'successCount': success_count,
                'errorCount': error_count,
                'errors': errors
            },
            message=f"批量导入完成，成功 {success_count} 题，失败 {error_count} 题"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"批量导入失败: {str(e)}",
            status_code=500
        )
