"""
题库编辑 - 题目管理模块
"""

import logging
from flask import Blueprint, request
from datetime import datetime
import json
from ..common.database import get_db_connection
from ..common.utils import format_response, validate_request, calculate_pagination

logger = logging.getLogger(__name__)

editor_questions_bp = Blueprint('editor_questions', __name__, url_prefix='/questions')

@editor_questions_bp.route('/<question_type>/max-index', methods=['GET'])
def get_max_question_index(question_type):
    """获取指定类型题目的最大编号"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        table_name = f"{question_type}_questions"

        cursor = conn.execute(f'''
            SELECT MAX(question_index) as max_index
            FROM {table_name}
        ''')
        result = cursor.fetchone()
        conn.close()

        max_index = result['max_index'] if result['max_index'] is not None else 0

        return format_response(
            success=True,
            data={'maxIndex': max_index},
            message=f"当前{question_type}题最大编号: {max_index}"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取最大题目编号失败: {str(e)}",
            status_code=500
        )

@editor_questions_bp.route('/<question_type>', methods=['GET'])
def get_questions(question_type):
    """获取题目列表（支持分页）"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '')
        subject_filter = request.args.get('subject', '')

        conn = get_db_connection()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("question_data LIKE ?")
            params.append(f'%{search}%')
            
        if question_type == 'professional' and subject_filter:
            where_conditions.append("subject = ?")
            params.append(subject_filter)
        
        where_clause = " AND ".join(where_conditions)
        if where_clause:
            where_clause = f" WHERE {where_clause}"

        # 安全验证：白名单验证表名
        allowed_tables = {'translation_questions', 'professional_questions'}
        if question_type == 'translation':
            table_name = 'translation_questions'
        elif question_type == 'professional':
            table_name = 'professional_questions'
        else:
            return format_response(success=False, error='无效的题目类型', status_code=400)

        if table_name not in allowed_tables:
            return format_response(success=False, error='无效的表名', status_code=400)

        # 获取总数
        count_sql = f"SELECT COUNT(*) FROM {table_name}{where_clause}"
        cursor = conn.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # 计算分页
        pagination = calculate_pagination(total_count, page, limit)
        
        # 获取分页数据
        if question_type == 'translation':
            sql = f'''
                SELECT id, question_index, question_data, created_at
                FROM translation_questions{where_clause}
                ORDER BY question_index
                LIMIT ? OFFSET ?
            '''
        else:
            sql = f'''
                SELECT id, question_index, question_data, difficulty, subject, created_at
                FROM professional_questions{where_clause}
                ORDER BY question_index
                LIMIT ? OFFSET ?
            '''
        
        cursor = conn.execute(sql, params + [limit, pagination['offset']])
        questions = cursor.fetchall()
        conn.close()
        
        # 格式化数据
        result = []
        for q in questions:
            try:
                content = json.loads(q['question_data']) if q['question_data'] else []
                
                question_item = {
                    'id': q['id'],
                    'index': q['question_index'],
                    'content': content,
                    'createdAt': q['created_at']
                }
                
                if question_type == 'professional':
                    question_item.update({
                        'difficulty': q['difficulty'],
                        'subject': q['subject']
                    })
                
                result.append(question_item)
            except Exception as e:
                logger.warning(f"格式化题目数据失败 (ID: {q['id']}): {e}")
                continue
        
        return format_response(
            success=True,
            data={
                'questions': result,
                'pagination': pagination
            },
            message=f"获取了 {len(result)} 道{question_type}题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取题目列表失败: {str(e)}",
            status_code=500
        )

@editor_questions_bp.route('', methods=['POST'])
def create_question():
    """创建题目"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['type', 'content'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )
        
        question_type = data.get('type')
        content = data.get('content', [])

        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        # 验证 content 格式
        if not isinstance(content, list):
            return format_response(success=False, error='content 必须是数组', status_code=400)

        # 检查是否是套题格式
        if len(content) > 0 and isinstance(content[0], dict) and 'content' in content[0]:
            # 套题格式验证
            if len(content) > 50:
                return format_response(success=False, error='子题数量不能超过50道', status_code=400)
            for i, sub in enumerate(content):
                if not isinstance(sub.get('content'), list) or len(sub.get('content', [])) == 0:
                    return format_response(success=False, error=f'第{i+1}道子题内容不能为空', status_code=400)
                for item in sub['content']:
                    if not isinstance(item, list) or len(item) != 2:
                        return format_response(success=False, error=f'内容格式错误', status_code=400)
                    if item[0] not in ['txt', 'img']:
                        return format_response(success=False, error=f'不支持的内容类型: {item[0]}', status_code=400)
                    if item[0] == 'img':
                        image_data = item[1]
                        if not isinstance(image_data, dict):
                            return format_response(success=False, error='图片内容必须为对象', status_code=400)
                        if not isinstance(image_data.get('src'), str) or not image_data['src']:
                            return format_response(success=False, error='图片原图路径不能为空', status_code=400)
                        if not isinstance(image_data.get('thumb'), str) or not image_data['thumb']:
                            return format_response(success=False, error='图片缩略图路径不能为空', status_code=400)

        conn = get_db_connection()

        # 获取下一个题目编号
        table_name = f"{question_type}_questions"
        cursor = conn.execute(f'''
            SELECT MAX(question_index) FROM {table_name}
        ''')
        max_index = cursor.fetchone()[0] or 0
        next_index = max_index + 1
        
        # 准备插入数据
        content_json = json.dumps(content, ensure_ascii=False)
        
        if question_type == 'translation':
            cursor = conn.execute('''
                INSERT INTO translation_questions (question_index, question_data, created_at)
                VALUES (?, ?, ?)
            ''', (next_index, content_json, datetime.now().isoformat()))
        else:
            difficulty = data.get('difficulty', 'medium')
            subject = data.get('subject', 'computer_science')
            
            cursor = conn.execute('''
                INSERT INTO professional_questions (question_index, question_data, difficulty, subject, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (next_index, content_json, difficulty, subject, datetime.now().isoformat()))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={
                'id': question_id,
                'index': next_index,
                'type': question_type
            },
            message=f"{question_type}题目创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建题目失败: {str(e)}",
            status_code=500
        )

@editor_questions_bp.route('/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """更新题目"""
    try:
        data = request.get_json()
        
        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )
        
        question_type = data.get('type')
        content = data.get('content', [])
        
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )
        
        conn = get_db_connection()
        
        # 检查题目是否存在
        table_name = f"{question_type}_questions"
        cursor = conn.execute(f'''
            SELECT id FROM {table_name} WHERE id = ?
        ''', (question_id,))
        
        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='题目不存在',
                status_code=404
            )
        
        # 更新题目
        content_json = json.dumps(content, ensure_ascii=False)
        
        if question_type == 'translation':
            conn.execute('''
                UPDATE translation_questions 
                SET question_data = ?, updated_at = ?
                WHERE id = ?
            ''', (content_json, datetime.now().isoformat(), question_id))
        else:
            difficulty = data.get('difficulty', 'medium')
            subject = data.get('subject', 'computer_science')
            
            conn.execute('''
                UPDATE professional_questions 
                SET question_data = ?, difficulty = ?, subject = ?, updated_at = ?
                WHERE id = ?
            ''', (content_json, difficulty, subject, datetime.now().isoformat(), question_id))
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={'id': question_id},
            message=f"{question_type}题目更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新题目失败: {str(e)}",
            status_code=500
        )

@editor_questions_bp.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """删除题目"""
    try:
        question_type = request.args.get('type')

        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()

        # 检查题目是否存在
        table_name = f"{question_type}_questions"
        cursor = conn.execute(f'''
            SELECT id FROM {table_name} WHERE id = ?
        ''', (question_id,))

        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='题目不存在',
                status_code=404
            )

        # 删除题目
        cursor = conn.execute(f'''
            DELETE FROM {table_name} WHERE id = ?
        ''', (question_id,))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message=f"{question_type}题目删除成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"删除题目失败: {str(e)}",
            status_code=500
        )
