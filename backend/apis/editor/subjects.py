"""
科目管理模块 - 处理专业课科目的管理
"""

from flask import Blueprint, request
from ..common.database import get_db_connection
from ..common.utils import format_response

subjects_bp = Blueprint('subjects', __name__, url_prefix='/subjects')

@subjects_bp.route('', methods=['GET'])
def get_subjects():
    """获取所有科目"""
    try:
        conn = get_db_connection()

        # 检查 subjects 表是否存在
        cursor = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='subjects'
        ''')
        table_exists = cursor.fetchone() is not None

        subjects = []

        if table_exists:
            # 从 subjects 表获取预设的科目列表
            cursor = conn.execute('''
                SELECT s.code, s.name,
                       COALESCE(pq.question_count, 0) as question_count
                FROM subjects s
                LEFT JOIN (
                    SELECT subject, COUNT(*) as question_count
                    FROM professional_questions
                    WHERE subject IS NOT NULL
                    GROUP BY subject
                ) pq ON s.code = pq.subject
                WHERE s.is_active = 1
                ORDER BY s.name
            ''')
            subjects = cursor.fetchall()

        # 如果 subjects 表不存在或没有数据，回退到从 professional_questions 查询
        if not subjects:
            cursor = conn.execute('''
                SELECT DISTINCT subject as code,
                       subject as name,
                       COUNT(*) as question_count
                FROM professional_questions
                WHERE subject IS NOT NULL
                GROUP BY subject
                ORDER BY subject
            ''')
            subjects = cursor.fetchall()

        conn.close()

        # 科目映射（用于美化显示）
        subject_mapping = {
            'computer_science': '计算机科学',
            'data_structure': '数据结构',
            'ai_introduction': '人工智能导论',
            'accounting': '会计学',
            'marketing': '市场营销'
        }

        result = []
        for subject in subjects:
            # 使用映射美化科目名称
            name = subject_mapping.get(subject['code'], subject['name'])
            result.append({
                'code': subject['code'],
                'name': name,
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
