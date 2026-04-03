"""
题库编辑系统API模块 - 统一管理题库编辑相关的所有API接口
"""

import logging
from flask import Blueprint, request
from datetime import datetime
import json
import sys
import os

logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apis.common.database import get_db_connection
from apis.common.utils import format_response, validate_request, calculate_pagination

# 创建题库编辑系统主蓝图
editor_bp = Blueprint('editor', __name__, url_prefix='/api')

# ==================== 题目管理路由 ====================

@editor_bp.route('/questions/<question_type>/max-index', methods=['GET'])
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

# ==================== 批量导出题目 ====================
@editor_bp.route('/questions/batch-export', methods=['GET'])
def batch_export_questions():
    """批量导出题目"""
    try:
        question_type = request.args.get('type')

        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        table_name = f"{question_type}_questions"

        # 专业题可以按科目筛选
        subject = request.args.get('subject', '')

        if question_type == 'translation':
            cursor = conn.execute(f'''
                SELECT question_index, question_data
                FROM {table_name}
                ORDER BY question_index
            ''')
        else:
            if subject:
                cursor = conn.execute(f'''
                    SELECT question_index, question_data, difficulty, subject
                    FROM {table_name}
                    WHERE subject = ?
                    ORDER BY question_index
                ''', (subject,))
            else:
                cursor = conn.execute(f'''
                    SELECT question_index, question_data, difficulty, subject
                    FROM {table_name}
                    ORDER BY question_index
                ''')

        questions = cursor.fetchall()
        conn.close()

        if not questions:
            return format_response(
                success=True,
                data={
                    'type': question_type,
                    'subject': subject,
                    'content': ''
                },
                message='没有可导出的题目'
            )

        # 构建导出文本：用空行分隔不同题目
        export_lines = []

        for q in questions:
            try:
                question_data = json.loads(q['question_data']) if q['question_data'] else []
                text_content = ''
                if isinstance(question_data, list):
                    if question_data and isinstance(question_data[0], dict) and 'content' in question_data[0]:
                        # 套题格式: [{'content': [['txt', 'text']]}, ...]
                        for sub_item in question_data:
                            if isinstance(sub_item, dict) and 'content' in sub_item:
                                for content_item in sub_item['content']:
                                    if isinstance(content_item, list) and len(content_item) >= 2 and content_item[0] == 'txt' and content_item[1]:
                                        text_content += content_item[1] + '\n'
                    else:
                        # 扁平格式: [['txt', 'text'], ['img', {...}]]
                        for item in question_data:
                            if isinstance(item, list) and len(item) >= 2 and item[0] == 'txt' and item[1]:
                                text_content += item[1] + '\n'

                if text_content:
                    export_lines.append(text_content.strip())
            except Exception:
                continue

        # 用空行分隔不同题目
        export_content = '\n\n'.join(export_lines)

        return format_response(
            success=True,
            data={
                'type': question_type,
                'subject': subject,
                'count': len(export_lines),
                'content': export_content
            },
            message=f"成功导出 {len(export_lines)} 道题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"批量导出失败: {str(e)}",
            status_code=500
        )


# ==================== 获取题目列表 ====================
@editor_bp.route('/questions/<question_type>', methods=['GET'])
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

        # 安全验证：白名单验证表名，防止 SQL 注入
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
                    'index': q['question_index'],  # 保持兼容性
                    'question_index': q['question_index'],  # 明确的题目编号字段
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

# ==================== 科目管理路由 ====================

@editor_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """获取所有科目"""
    try:
        # 检查是否是科目管理页面的请求（有分页参数）
        page = request.args.get('page')
        limit = request.args.get('limit')
        search = request.args.get('search', '')

        conn = get_db_connection()

        if page is not None and limit is not None:
            # 科目管理页面的分页请求
            page = int(page)
            limit = int(limit)

            # 构建查询条件
            where_conditions = []
            params = []

            if search:
                where_conditions.append("(cs.code LIKE ? OR cs.name LIKE ?)")
                params.extend([f'%{search}%', f'%{search}%'])

            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

            # 获取总数
            count_query = f'''
                WITH combined_subjects AS (
                    SELECT s.id, s.code, s.name, s.description, s.is_active, s.created_at
                    FROM subjects s
                    UNION ALL
                    SELECT NULL as id, pq.subject as code, pq.subject as name,
                           '' as description, 1 as is_active, '' as created_at
                    FROM (
                        SELECT DISTINCT subject
                        FROM professional_questions
                        WHERE subject IS NOT NULL AND TRIM(subject) != ''
                    ) pq
                    LEFT JOIN subjects s ON s.code = pq.subject
                    WHERE s.code IS NULL
                )
                SELECT COUNT(*)
                FROM combined_subjects cs
                {where_clause}
            '''
            cursor = conn.execute(count_query, params)
            total = cursor.fetchone()[0]

            # 获取分页数据
            offset = (page - 1) * limit
            data_query = f'''
                WITH combined_subjects AS (
                    SELECT s.id, s.code, s.name, s.description, s.is_active, s.created_at
                    FROM subjects s
                    UNION ALL
                    SELECT NULL as id, pq.subject as code, pq.subject as name,
                           '' as description, 1 as is_active, '' as created_at
                    FROM (
                        SELECT DISTINCT subject
                        FROM professional_questions
                        WHERE subject IS NOT NULL AND TRIM(subject) != ''
                    ) pq
                    LEFT JOIN subjects s ON s.code = pq.subject
                    WHERE s.code IS NULL
                )
                SELECT cs.id, cs.code, cs.name, cs.description, cs.is_active, cs.created_at,
                       COALESCE(pq.question_count, 0) as question_count
                FROM combined_subjects cs
                LEFT JOIN (
                    SELECT subject, COUNT(*) as question_count
                    FROM professional_questions
                    GROUP BY subject
                ) pq ON cs.code = pq.subject
                {where_clause}
                ORDER BY cs.created_at DESC, cs.code ASC
                LIMIT ? OFFSET ?
            '''
            cursor = conn.execute(data_query, params + [limit, offset])
            subjects = cursor.fetchall()
            conn.close()

            # 转换为字典格式
            result = []
            for subject in subjects:
                result.append({
                    'id': subject['id'] if subject['id'] is not None else f"virtual:{subject['code']}",
                    'code': subject['code'],
                    'name': subject['name'],
                    'description': subject['description'],
                    'is_active': bool(subject['is_active']),
                    'question_count': subject['question_count'],
                    'created_at': subject['created_at'],
                    'updated_at': subject['created_at']  # 使用created_at作为updated_at的默认值
                })

            return format_response(
                success=True,
                data={
                    'subjects': result,
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit if total > 0 else 1
                },
                message=f"获取了 {len(result)} 个科目"
            )
        else:
            # 简单的科目列表请求（用于下拉选择等）
            # 从subjects表获取所有启用的科目，并统计题目数量
            cursor = conn.execute('''
                SELECT s.code, s.name, s.is_active,
                       COALESCE(pq.question_count, 0) as question_count
                FROM subjects s
                LEFT JOIN (
                    SELECT subject, COUNT(*) as question_count
                    FROM professional_questions
                    GROUP BY subject
                ) pq ON s.code = pq.subject
                WHERE s.is_active = 1
                ORDER BY s.name
            ''')
            subjects = cursor.fetchall()
            conn.close()

            result = []
            for subject in subjects:
                result.append({
                    'value': subject['code'],
                    'label': subject['name'],
                    'questionCount': subject['question_count']
                })

            return format_response(
                success=True,
                data=result,
                message=f"获取了 {len(result)} 个科目"
            )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取科目列表失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/editor/subjects', methods=['POST'])
def create_subject():
    """创建科目"""
    try:
        data = request.get_json()

        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['code', 'name'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )

        code = data.get('code')
        name = data.get('name')
        description = data.get('description', '')
        is_active = data.get('is_active', True)

        conn = get_db_connection()

        # 检查科目代码是否已存在
        cursor = conn.execute('SELECT id FROM subjects WHERE code = ?', (code,))
        if cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='科目代码已存在',
                status_code=400
            )

        # 插入新科目
        cursor = conn.execute('''
            INSERT INTO subjects (code, name, description, is_active, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (code, name, description, is_active, datetime.now().isoformat()))

        subject_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={'id': subject_id, 'code': code, 'name': name},
            message="科目创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建科目失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/editor/subjects/<int:subject_id>', methods=['PUT'])
def update_subject(subject_id):
    """更新科目"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        conn = get_db_connection()

        # 检查科目是否存在
        cursor = conn.execute('SELECT id FROM subjects WHERE id = ?', (subject_id,))
        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='科目不存在',
                status_code=404
            )

        # 更新科目
        code = data.get('code')
        name = data.get('name')
        description = data.get('description', '')
        is_active = data.get('is_active', True)

        # 如果更新代码，检查是否与其他科目冲突
        if code:
            cursor = conn.execute('SELECT id FROM subjects WHERE code = ? AND id != ?', (code, subject_id))
            if cursor.fetchone():
                conn.close()
                return format_response(
                    success=False,
                    error='科目代码已存在',
                    status_code=400
                )

        conn.execute('''
            UPDATE subjects
            SET code = ?, name = ?, description = ?, is_active = ?
            WHERE id = ?
        ''', (code, name, description, is_active, subject_id))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={'id': subject_id},
            message="科目更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新科目失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/editor/subjects/<subject_code>', methods=['GET'])
def get_subject_by_code(subject_code):
    """通过科目代码获取科目详情"""
    try:
        conn = get_db_connection()

        # 首先尝试从数据库中获取科目信息
        cursor = conn.execute('''
            SELECT id, code, name, description, is_active
            FROM subjects
            WHERE code = ?
        ''', (subject_code,))
        subject = cursor.fetchone()

        if subject:
            # 获取该科目的题目统计
            cursor = conn.execute('''
                SELECT COUNT(*) as question_count
                FROM professional_questions
                WHERE subject = ?
            ''', (subject_code,))
            result = cursor.fetchone()
            question_count = result['question_count'] if result else 0

            subject_detail = {
                'id': subject['id'],
                'code': subject['code'],
                'name': subject['name'],
                'description': subject['description'],
                'is_active': bool(subject['is_active']),
                'questionCount': question_count
            }
        else:
            # 如果数据库中没有，使用默认映射（向后兼容）
            subject_mapping = {
                'computer_science': '计算机科学',
                'data_structure': '数据结构',
                'ai_introduction': '人工智能导论',
                'accouting': '会计学',
                'accounting': '会计学',
                'marketing': '市场营销'
            }

            # 获取该科目的题目统计
            cursor = conn.execute('''
                SELECT COUNT(*) as question_count
                FROM professional_questions
                WHERE subject = ?
            ''', (subject_code,))
            result = cursor.fetchone()
            question_count = result['question_count'] if result else 0

            subject_detail = {
                'id': None,  # 没有数据库记录
                'code': subject_code,
                'name': subject_mapping.get(subject_code, subject_code),
                'description': f'{subject_mapping.get(subject_code, subject_code)}相关题目',
                'is_active': True,  # 默认启用
                'questionCount': question_count
            }

        conn.close()

        return format_response(
            success=True,
            data=subject_detail,
            message="获取科目详情成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取科目详情失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/editor/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """删除科目"""
    try:
        conn = get_db_connection()

        # 检查科目是否存在
        cursor = conn.execute('SELECT id, code FROM subjects WHERE id = ?', (subject_id,))
        subject = cursor.fetchone()
        if not subject:
            conn.close()
            return format_response(
                success=False,
                error='科目不存在',
                status_code=404
            )

        # 检查是否有题目使用该科目
        cursor = conn.execute('SELECT COUNT(*) FROM professional_questions WHERE subject = ?', (subject['code'],))
        question_count = cursor.fetchone()[0]

        if question_count > 0:
            conn.close()
            return format_response(
                success=False,
                error=f'无法删除科目，还有 {question_count} 道题目使用该科目',
                status_code=400
            )

        # 删除科目
        conn.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={'id': subject_id},
            message="科目删除成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"删除科目失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/editor/subjects/<int:subject_id>/toggle', methods=['POST'])
def toggle_subject_status(subject_id):
    """切换科目启用状态"""
    try:
        conn = get_db_connection()

        # 检查科目是否存在
        cursor = conn.execute('SELECT id, is_active FROM subjects WHERE id = ?', (subject_id,))
        subject = cursor.fetchone()
        if not subject:
            conn.close()
            return format_response(
                success=False,
                error='科目不存在',
                status_code=404
            )

        # 切换状态
        new_status = not bool(subject['is_active'])
        cursor = conn.execute('''
            UPDATE subjects
            SET is_active = ?
            WHERE id = ?
        ''', (new_status, subject_id))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message=f"科目状态已{'启用' if new_status else '禁用'}"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"切换科目状态失败: {str(e)}",
            status_code=500
        )

# ==================== 题目CRUD路由 ====================

@editor_bp.route('/questions', methods=['POST'])
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

        conn = get_db_connection()

        # 获取题目编号（优先使用前端传递的编号，否则自动生成）
        question_index = data.get('index')
        if question_index is None:
            # 如果前端没有传递编号，则自动生成
            table_name = f"{question_type}_questions"
            cursor = conn.execute(f'''
                SELECT MAX(question_index) FROM {table_name}
            ''')
            max_index = cursor.fetchone()[0] or 0
            question_index = max_index + 1

        # 准备插入数据
        content_json = json.dumps(content, ensure_ascii=False)

        if question_type == 'translation':
            cursor = conn.execute('''
                INSERT INTO translation_questions (question_index, question_data, created_at)
                VALUES (?, ?, ?)
            ''', (question_index, content_json, datetime.now().isoformat()))
        else:
            difficulty = data.get('difficulty', 'medium')
            subject = data.get('subject', 'computer_science')

            cursor = conn.execute('''
                INSERT INTO professional_questions (question_index, question_data, difficulty, subject, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (question_index, content_json, difficulty, subject, datetime.now().isoformat()))

        question_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'id': question_id,
                'index': question_index,
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

@editor_bp.route('/questions/question/<int:question_id>', methods=['PUT'])
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
        question_index = data.get('index')  # 获取题目编号

        if question_type == 'translation':
            # 构建更新字段
            update_fields = ['question_data = ?']
            update_values = [content_json]

            if question_index is not None:
                update_fields.append('question_index = ?')
                update_values.append(question_index)

            update_values.append(question_id)  # WHERE条件的ID

            conn.execute(f'''
                UPDATE translation_questions
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)
        else:
            difficulty = data.get('difficulty', 'medium')
            subject = data.get('subject', 'computer_science')

            # 构建更新字段
            update_fields = ['question_data = ?', 'difficulty = ?', 'subject = ?']
            update_values = [content_json, difficulty, subject]

            if question_index is not None:
                update_fields.append('question_index = ?')
                update_values.append(question_index)

            update_values.append(question_id)  # WHERE条件的ID

            conn.execute(f'''
                UPDATE professional_questions
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', update_values)

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

@editor_bp.route('/questions/question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """删除题目"""
    try:
        conn = get_db_connection()

        # 先尝试在翻译题表中查找
        cursor = conn.execute('SELECT id FROM translation_questions WHERE id = ?', (question_id,))
        translation_question = cursor.fetchone()

        # 再尝试在专业题表中查找
        cursor = conn.execute('SELECT id FROM professional_questions WHERE id = ?', (question_id,))
        professional_question = cursor.fetchone()

        if translation_question:
            # 删除翻译题
            conn.execute('DELETE FROM translation_questions WHERE id = ?', (question_id,))
            question_type = 'translation'
        elif professional_question:
            # 删除专业题
            conn.execute('DELETE FROM professional_questions WHERE id = ?', (question_id,))
            question_type = 'professional'
        else:
            conn.close()
            return format_response(
                success=False,
                error='题目不存在',
                status_code=404
            )

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

# ==================== 页头设置路由 ====================

@editor_bp.route('/header-settings', methods=['GET'])
def get_header_settings():
    """获取页头设置（Logo、标题等）"""
    try:
        conn = get_db_connection()

        # 尝试从数据库获取页头设置（使用 attribute 列名）
        cursor = conn.execute('SELECT attribute, value FROM settings')
        db_settings = cursor.fetchall()
        conn.close()

        # 默认页头设置（不再硬编码标题和版权，从数据库读取）
        default_settings = {
            'title': '',
            'instituteLogo': '/backend-assets/logos/logo_institute.png',
            'collegeLogo': '/backend-assets/logos/logo_college.png',
            'footerCopyright': ''
        }

        # 合并数据库设置
        for setting in db_settings:
            attr = setting['attribute']
            value = setting['value']
            # 映射数据库字段到 API 字段
            if attr == 'header_title':
                default_settings['title'] = value or ''
            elif attr == 'institute_logo_path':
                # 确保URL以 / 开头
                if value and not value.startswith('/'):
                    value = '/' + value
                default_settings['instituteLogo'] = value
            elif attr == 'college_logo_path':
                # 确保URL以 / 开头
                if value and not value.startswith('/'):
                    value = '/' + value
                default_settings['collegeLogo'] = value
            elif attr == 'footer_copyright':
                default_settings['footerCopyright'] = value or ''
            else:
                default_settings[attr] = value

        return format_response(
            success=True,
            data=default_settings,
            message="获取页头设置成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取页头设置失败: {str(e)}",
            status_code=500
        )

@editor_bp.route('/header-settings', methods=['PUT'])
def update_header_settings():
    """更新页头设置"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        conn = get_db_connection()

        # 映射 API 字段到数据库字段
        field_mapping = {
            'title': 'header_title',
            'instituteLogo': 'institute_logo_path',
            'collegeLogo': 'college_logo_path',
            'footerCopyright': 'footer_copyright'
        }

        # 允许的URL前缀（白名单）
        allowed_url_prefixes = ('/backend-assets/', '/assets/', '/uploads/', 'http://', 'https://')

        for api_key, value in data.items():
            # 验证URL安全性（仅针对Logo字段）
            if api_key in ('instituteLogo', 'collegeLogo') and value:
                # 自动添加前导斜杠（如果缺少）
                if not value.startswith('/') and not value.startswith('http'):
                    value = '/' + value
                if not value.startswith(allowed_url_prefixes):
                    return format_response(
                        success=False,
                        error=f"无效的Logo URL格式: {api_key}",
                        status_code=400
                    )

            # 转换为数据库字段名
            db_attr = field_mapping.get(api_key, api_key)

            # 检查设置是否存在
            cursor = conn.execute(
                'SELECT id FROM settings WHERE attribute = ?',
                (db_attr,)
            )

            if cursor.fetchone():
                conn.execute('''
                    UPDATE settings
                    SET value = ?, updated_at = datetime('now')
                    WHERE attribute = ?
                ''', (value, db_attr))
            else:
                conn.execute('''
                    INSERT INTO settings (attribute, value, created_at, updated_at)
                    VALUES (?, ?, datetime('now'), datetime('now'))
                ''', (db_attr, value))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message="页头设置更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新页头设置失败: {str(e)}",
            status_code=500
        )

# ==================== 批量导入导出路由 ====================

@editor_bp.route('/questions/batch-import', methods=['POST'])
def batch_import_questions():
    """批量导入题目"""
    try:
        data = request.get_json()

        # 验证请求数据
        if not data:
            return format_response(
                success=False,
                error='请求数据不能为空',
                status_code=400
            )

        question_type = data.get('type')
        content = data.get('content', '')

        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        if not content or not content.strip():
            return format_response(
                success=False,
                error='导入内容不能为空',
                status_code=400
            )

        # 解析文本内容：
        # - 每一行 = 一个子题目
        # - 空行 = 分隔不同题目组（套题）
        lines = content.split('\n')
        question_sets = []  # 题目组列表
        current_sub_questions = []  # 当前题目的子题目列表

        for line in lines:
            if line.strip() == '':
                # 空行：表示题目组之间分隔
                if current_sub_questions:
                    question_sets.append(current_sub_questions)
                    current_sub_questions = []
            else:
                # 非空行：当前题目的一个子题目
                current_sub_questions.append(line)

        # 处理最后一部分
        if current_sub_questions:
            question_sets.append(current_sub_questions)

        if not question_sets:
            return format_response(
                success=False,
                error='未能解析出有效题目',
                status_code=400
            )

        conn = get_db_connection()
        table_name = f"{question_type}_questions"

        # 获取下一个题目编号
        cursor = conn.execute(f'SELECT MAX(question_index) FROM {table_name}')
        max_index = cursor.fetchone()[0] or 0

        # 专业题时的科目
        subject = data.get('subject', 'computer_science')
        difficulty = data.get('difficulty', 'medium')

        imported_count = 0
        failed_questions = []

        for idx, sub_questions in enumerate(question_sets):
            if not sub_questions:
                continue

            try:
                max_index += 1

                # 构建题目数据：
                # - 如果只有一个子题目，直接存储为单题格式 [['txt', 内容]]
                # - 如果有多个子题目，存储为套题格式 [{'content': [['txt', 内容]]}, ...]
                if len(sub_questions) == 1:
                    # 单题格式
                    question_data = json.dumps([['txt', sub_questions[0]]], ensure_ascii=False)
                else:
                    # 套题格式
                    question_data = json.dumps([
                        {'content': [['txt', sq]]} for sq in sub_questions
                    ], ensure_ascii=False)

                if question_type == 'translation':
                    cursor = conn.execute('''
                        INSERT INTO translation_questions (question_index, question_data, created_at)
                        VALUES (?, ?, ?)
                    ''', (max_index, question_data, datetime.now().isoformat()))
                else:
                    cursor = conn.execute('''
                        INSERT INTO professional_questions (question_index, question_data, difficulty, subject, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (max_index, question_data, difficulty, subject, datetime.now().isoformat()))

                imported_count += 1
            except Exception as e:
                failed_questions.append({
                    'index': idx + 1,
                    'error': str(e)
                })

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'imported': imported_count,
                'failed': failed_questions,
                'total': len(question_sets)
            },
            message=f"成功导入 {imported_count} 道题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"批量导入失败: {str(e)}",
            status_code=500
        )


# ==================== 批量操作路由 ====================

@editor_bp.route('/questions/batch-delete', methods=['POST'])
def batch_delete_questions():
    """批量删除题目"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error='请求数据不能为空',
                status_code=400
            )

        question_ids = data.get('question_ids', [])
        question_type = data.get('question_type', 'translation')

        if not question_ids:
            return format_response(
                success=False,
                error='请选择要删除的题目',
                status_code=400
            )

        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        table_name = f"{question_type}_questions"

        # 构建删除语句
        placeholders = ','.join(['?'] * len(question_ids))
        cursor = conn.execute(f'DELETE FROM {table_name} WHERE id IN ({placeholders})', question_ids)

        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()

        return format_response(
            success=True,
            data={'deleted_count': deleted_count},
            message=f"成功删除 {deleted_count} 道题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"批量删除失败: {str(e)}",
            status_code=500
        )


@editor_bp.route('/questions/batch-update-subject', methods=['POST'])
def batch_update_subject():
    """批量修改题目科目"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error='请求数据不能为空',
                status_code=400
            )

        question_ids = data.get('question_ids', [])
        subject = data.get('subject', '')

        if not question_ids:
            return format_response(
                success=False,
                error='请选择要修改的题目',
                status_code=400
            )

        if not subject:
            return format_response(
                success=False,
                error='请选择科目',
                status_code=400
            )

        conn = get_db_connection()

        # 构建更新语句
        placeholders = ','.join(['?'] * len(question_ids))
        cursor = conn.execute(f'UPDATE professional_questions SET subject = ? WHERE id IN ({placeholders})',
                            [subject] + question_ids)

        conn.commit()
        updated_count = cursor.rowcount
        conn.close()

        return format_response(
            success=True,
            data={'updated_count': updated_count},
            message=f"成功修改 {updated_count} 道题目的科目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"批量修改失败: {str(e)}",
            status_code=500
        )


# ==================== 健康检查路由 ====================

@editor_bp.route('/health', methods=['GET'])
def health_check():
    """题库编辑系统健康检查"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('SELECT 1')
        cursor.fetchone()
        conn.close()

        return format_response(
            success=True,
            data={
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now().isoformat(),
                'system': 'editor_system',
                'version': '1.0.0'
            },
            message="题库编辑系统运行正常"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"健康检查失败: {str(e)}",
            status_code=500
        )

# 导入并注册子模块蓝图
from .subjects import subjects_bp
editor_bp.register_blueprint(subjects_bp)

# 导入上传蓝图
try:
    from .upload import upload_bp
    editor_bp.register_blueprint(upload_bp)
    logger.info("upload API registered")
except ImportError as e:
    logger.info(f"upload module not found: {e}")

__all__ = ['editor_bp']
