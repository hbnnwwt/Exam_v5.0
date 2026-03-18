"""
考试记录模块 - 处理考试记录的查询和管理
"""

from flask import Blueprint, request
from ..common.database import get_db_connection
from ..common.utils import format_response

records_bp = Blueprint('records', __name__, url_prefix='/records')

@records_bp.route('', methods=['GET'])
def get_exam_records():
    """获取考试记录列表"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status')
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        
        # 构建查询条件
        where_clause = ""
        params = []
        
        if status_filter:
            where_clause = " WHERE exam_status = ?"
            params.append(status_filter)
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) FROM exam_records{where_clause}"
        cursor = conn.execute(count_sql, params)
        total_count = cursor.fetchone()[0]
        
        # 获取分页数据
        sql = f'''
            SELECT student_number, exam_status, created_at, updated_at
            FROM exam_records{where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        cursor = conn.execute(sql, params + [limit, offset])
        records = cursor.fetchall()
        conn.close()

        result = []
        for record in records:
            result.append({
                'studentNumber': record['student_number'],
                'examStatus': record['exam_status'],
                'createdAt': record['created_at'],
                'updatedAt': record['updated_at']
            })

        # 计算分页信息
        total_pages = (total_count + limit - 1) // limit

        return format_response(
            success=True,
            data={
                'records': result,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'limit': limit,
                    'totalPages': total_pages,
                    'hasNext': page < total_pages,
                    'hasPrev': page > 1
                }
            },
            message=f"获取了 {len(result)} 条考试记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试记录失败: {str(e)}",
            status_code=500
        )

@records_bp.route('/<student_number>', methods=['GET'])
def get_student_record(student_number):
    """获取指定学生的考试记录"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, exam_status, created_at, updated_at
            FROM exam_records
            WHERE student_number = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (student_number,))

        record = cursor.fetchone()
        conn.close()

        if not record:
            return format_response(
                success=False,
                error='考试记录不存在',
                status_code=404
            )

        result = {
            'studentNumber': record['student_number'],
            'examStatus': record['exam_status'],
            'createdAt': record['created_at'],
            'updatedAt': record['updated_at']
        }

        return format_response(
            success=True,
            data=result
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取学生考试记录失败: {str(e)}",
            status_code=500
        )

@records_bp.route('/<student_number>/history', methods=['GET'])
def get_student_history(student_number):
    """获取学生的所有考试历史记录"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, current_step, exam_status,
                   translation_question, professional_question,
                   created_at, updated_at, completed_at
            FROM exam_records
            WHERE student_number = ?
            ORDER BY created_at DESC
        ''', (student_number,))
        
        records = cursor.fetchall()
        conn.close()

        result = []
        for record in records:
            result.append({
                'studentNumber': record['student_number'],
                'currentStep': record['current_step'],
                'examStatus': record['exam_status'],
                'translationQuestion': record['translation_question'],
                'professionalQuestion': record['professional_question'],
                'createdAt': record['created_at'],
                'updatedAt': record['updated_at'],
                'completedAt': record['completed_at']
            })

        return format_response(
            success=True,
            data=result,
            message=f"获取了学生 {student_number} 的 {len(result)} 条历史记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取学生历史记录失败: {str(e)}",
            status_code=500
        )

@records_bp.route('/status/<status>', methods=['GET'])
def get_records_by_status(status):
    """根据状态获取考试记录"""
    try:
        valid_statuses = ['ready', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            return format_response(
                success=False,
                error=f'无效的状态，有效状态: {", ".join(valid_statuses)}',
                status_code=400
            )

        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, exam_status, created_at, updated_at
            FROM exam_records
            WHERE exam_status = ?
            ORDER BY created_at DESC
        ''', (status,))
        
        records = cursor.fetchall()
        conn.close()

        result = []
        for record in records:
            result.append({
                'studentNumber': record['student_number'],
                'examStatus': record['exam_status'],
                'createdAt': record['created_at'],
                'updatedAt': record['updated_at']
            })

        return format_response(
            success=True,
            data=result,
            message=f"获取了 {len(result)} 条状态为 {status} 的考试记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试记录失败: {str(e)}",
            status_code=500
        )

@records_bp.route('', methods=['POST'])
def create_exam_record():
    """创建考试记录"""
    try:
        from flask import request
        from datetime import datetime

        data = request.get_json()

        if not data or 'studentNumber' not in data:
            return format_response(
                success=False,
                error="缺少必要参数：studentNumber",
                status_code=400
            )

        student_number = data.get('studentNumber')
        exam_status = data.get('examStatus', 0)  # 默认0=未完成

        conn = get_db_connection()

        # 检查是否已存在记录
        cursor = conn.execute('''
            SELECT id FROM exam_records WHERE student_number = ?
        ''', (student_number,))

        if cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='该学生的考试记录已存在',
                status_code=400
            )

        # 创建考试记录
        cursor = conn.execute('''
            INSERT INTO exam_records (student_number, exam_status, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (student_number, exam_status, datetime.now().isoformat(), datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message="考试记录创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建考试记录失败: {str(e)}",
            status_code=500
        )

@records_bp.route('/<student_number>', methods=['DELETE'])
def delete_student_record(student_number):
    """删除学生的考试记录"""
    try:
        conn = get_db_connection()
        
        # 检查记录是否存在
        cursor = conn.execute('''
            SELECT id FROM exam_records WHERE student_number = ?
        ''', (student_number,))
        
        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='考试记录不存在',
                status_code=404
            )

        # 删除记录
        cursor = conn.execute('''
            DELETE FROM exam_records WHERE student_number = ?
        ''', (student_number,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={'deletedCount': deleted_count},
            message=f"删除了学生 {student_number} 的 {deleted_count} 条考试记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"删除考试记录失败: {str(e)}",
            status_code=500
        )
