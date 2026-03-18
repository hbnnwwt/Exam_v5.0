"""
统计分析模块 - 提供各种统计数据和分析功能
"""

from flask import Blueprint, request
from ..common.database import get_db_connection
from ..common.utils import format_response

statistics_bp = Blueprint('statistics', __name__, url_prefix='/stats')

@statistics_bp.route('/overview', methods=['GET'])
def get_overview_stats():
    """获取系统概览统计"""
    try:
        conn = get_db_connection()
        
        # 获取总学生数
        cursor = conn.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        
        # 获取考试记录统计
        cursor = conn.execute('''
            SELECT 
                COUNT(*) as total_exams,
                COUNT(CASE WHEN exam_status = 'completed' THEN 1 END) as completed_exams,
                COUNT(CASE WHEN exam_status = 'in_progress' THEN 1 END) as in_progress_exams,
                COUNT(CASE WHEN exam_status = 'ready' THEN 1 END) as ready_exams
            FROM exam_records
        ''')
        exam_stats = cursor.fetchone()
        
        # 获取题目统计
        cursor = conn.execute('SELECT COUNT(*) FROM professional_questions')
        professional_count = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT COUNT(*) FROM translation_questions')
        translation_count = cursor.fetchone()[0]
        
        # 获取已使用题目统计
        cursor = conn.execute('''
            SELECT 
                COUNT(DISTINCT translation_question) as used_translation,
                COUNT(DISTINCT professional_question) as used_professional
            FROM exam_records
            WHERE translation_question IS NOT NULL OR professional_question IS NOT NULL
        ''')
        used_stats = cursor.fetchone()
        
        conn.close()
        
        result = {
            'students': {
                'total': total_students
            },
            'exams': {
                'total': exam_stats['total_exams'],
                'completed': exam_stats['completed_exams'],
                'inProgress': exam_stats['in_progress_exams'],
                'ready': exam_stats['ready_exams']
            },
            'questions': {
                'professional': {
                    'total': professional_count,
                    'used': used_stats['used_professional'] or 0,
                    'available': professional_count - (used_stats['used_professional'] or 0)
                },
                'translation': {
                    'total': translation_count,
                    'used': used_stats['used_translation'] or 0,
                    'available': translation_count - (used_stats['used_translation'] or 0)
                }
            }
        }
        
        return format_response(
            success=True,
            data=result,
            message="获取系统概览统计成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取系统统计失败: {str(e)}",
            status_code=500
        )

@statistics_bp.route('/questions', methods=['GET'])
def get_question_stats():
    """获取题目统计"""
    try:
        question_type = request.args.get('type', 'all')
        
        conn = get_db_connection()
        
        if question_type == 'professional':
            # 专业题统计
            cursor = conn.execute('''
                SELECT 
                    subject,
                    COUNT(*) as count,
                    COUNT(CASE WHEN difficulty = 'easy' THEN 1 END) as easy_count,
                    COUNT(CASE WHEN difficulty = 'medium' THEN 1 END) as medium_count,
                    COUNT(CASE WHEN difficulty = 'hard' THEN 1 END) as hard_count
                FROM professional_questions
                GROUP BY subject
            ''')
            stats = cursor.fetchall()
            
            result = []
            for stat in stats:
                result.append({
                    'subject': stat['subject'],
                    'total': stat['count'],
                    'difficulty': {
                        'easy': stat['easy_count'],
                        'medium': stat['medium_count'],
                        'hard': stat['hard_count']
                    }
                })
                
        elif question_type == 'translation':
            # 翻译题统计
            cursor = conn.execute('SELECT COUNT(*) as total FROM translation_questions')
            total = cursor.fetchone()['total']
            
            result = {
                'total': total,
                'type': 'translation'
            }
            
        else:
            # 全部统计
            cursor = conn.execute('SELECT COUNT(*) as total FROM professional_questions')
            professional_total = cursor.fetchone()['total']
            
            cursor = conn.execute('SELECT COUNT(*) as total FROM translation_questions')
            translation_total = cursor.fetchone()['total']
            
            result = {
                'professional': professional_total,
                'translation': translation_total,
                'total': professional_total + translation_total
            }
        
        conn.close()
        
        return format_response(
            success=True,
            data=result,
            message=f"获取{question_type}题目统计成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取题目统计失败: {str(e)}",
            status_code=500
        )

@statistics_bp.route('/exams', methods=['GET'])
def get_exam_stats():
    """获取考试统计"""
    try:
        # 获取时间范围参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        
        # 构建查询条件
        where_clause = ""
        params = []
        
        if start_date:
            where_clause += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND created_at <= ?"
            params.append(end_date)
        
        # 基础统计
        sql = f'''
            SELECT 
                COUNT(*) as total_exams,
                COUNT(CASE WHEN exam_status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN exam_status = 'in_progress' THEN 1 END) as in_progress,
                COUNT(CASE WHEN exam_status = 'ready' THEN 1 END) as ready,
                AVG(CASE WHEN exam_status = 'completed' AND completed_at IS NOT NULL 
                    THEN (julianday(completed_at) - julianday(created_at)) * 24 * 60 END) as avg_duration_minutes
            FROM exam_records
            WHERE 1=1{where_clause}
        '''
        
        cursor = conn.execute(sql, params)
        basic_stats = cursor.fetchone()
        
        # 按日期统计
        date_sql = f'''
            SELECT 
                DATE(created_at) as exam_date,
                COUNT(*) as count,
                COUNT(CASE WHEN exam_status = 'completed' THEN 1 END) as completed_count
            FROM exam_records
            WHERE 1=1{where_clause}
            GROUP BY DATE(created_at)
            ORDER BY exam_date DESC
            LIMIT 30
        '''
        
        cursor = conn.execute(date_sql, params)
        daily_stats = cursor.fetchall()
        
        # 按步骤统计
        step_sql = f'''
            SELECT 
                current_step,
                COUNT(*) as count
            FROM exam_records
            WHERE 1=1{where_clause}
            GROUP BY current_step
            ORDER BY current_step
        '''
        
        cursor = conn.execute(step_sql, params)
        step_stats = cursor.fetchall()
        
        conn.close()
        
        result = {
            'basic': {
                'totalExams': basic_stats['total_exams'],
                'completed': basic_stats['completed'],
                'inProgress': basic_stats['in_progress'],
                'ready': basic_stats['ready'],
                'avgDurationMinutes': round(basic_stats['avg_duration_minutes'] or 0, 2)
            },
            'daily': [
                {
                    'date': row['exam_date'],
                    'total': row['count'],
                    'completed': row['completed_count']
                }
                for row in daily_stats
            ],
            'steps': [
                {
                    'step': row['current_step'],
                    'count': row['count']
                }
                for row in step_stats
            ]
        }
        
        return format_response(
            success=True,
            data=result,
            message="获取考试统计成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试统计失败: {str(e)}",
            status_code=500
        )

@statistics_bp.route('/usage', methods=['GET'])
def get_usage_stats():
    """获取系统使用统计"""
    try:
        conn = get_db_connection()
        
        # 题目使用频率统计
        cursor = conn.execute('''
            SELECT 
                'translation' as type,
                translation_question as question,
                COUNT(*) as usage_count
            FROM exam_records
            WHERE translation_question IS NOT NULL
            GROUP BY translation_question
            
            UNION ALL
            
            SELECT 
                'professional' as type,
                professional_question as question,
                COUNT(*) as usage_count
            FROM exam_records
            WHERE professional_question IS NOT NULL
            GROUP BY professional_question
            
            ORDER BY usage_count DESC
        ''')
        
        question_usage = cursor.fetchall()
        
        # 科目使用统计（专业题）
        cursor = conn.execute('''
            SELECT 
                pq.subject,
                COUNT(er.professional_question) as usage_count
            FROM exam_records er
            JOIN professional_questions pq ON er.professional_question LIKE '%' || pq.question_index || '%'
            WHERE er.professional_question IS NOT NULL
            GROUP BY pq.subject
            ORDER BY usage_count DESC
        ''')
        
        subject_usage = cursor.fetchall()
        
        conn.close()
        
        result = {
            'questionUsage': [
                {
                    'type': row['type'],
                    'question': row['question'],
                    'usageCount': row['usage_count']
                }
                for row in question_usage
            ],
            'subjectUsage': [
                {
                    'subject': row['subject'],
                    'usageCount': row['usage_count']
                }
                for row in subject_usage
            ]
        }
        
        return format_response(
            success=True,
            data=result,
            message="获取使用统计成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取使用统计失败: {str(e)}",
            status_code=500
        )
