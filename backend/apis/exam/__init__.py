"""
考试系统API模块 - 统一管理考试相关的所有API接口
"""

from flask import Blueprint, request, current_app
from datetime import datetime
import sys
import os
import random

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apis.common.database import get_db_connection
from apis.common.utils import format_response, validate_request

# 创建考试系统主蓝图
exam_bp = Blueprint('exam', __name__, url_prefix='/exam-api')

# 导入子模块以注册路由
# 注意：这些导入必须放在蓝图创建之后，以便路由能够正确注册
# 注意：子模块的导入现在在 app.py 中完成，以确保正确的导入顺序

# ==================== 系统控制路由 ====================

@exam_bp.route('/test', methods=['GET'])
def test_route():
    """测试路由"""
    return format_response(
        success=True,
        data={'message': 'API正常工作'},
        message="测试成功"
    )

@exam_bp.route('/test/professional', methods=['GET'])
def test_professional_questions():
    """测试专业题查询"""
    try:
        conn = get_db_connection()

        # 测试查询专业题表结构
        cursor = conn.execute("PRAGMA table_info(professional_questions)")
        columns = cursor.fetchall()

        # 测试查询前3条专业题
        cursor = conn.execute("SELECT * FROM professional_questions LIMIT 3")
        questions = cursor.fetchall()

        # 测试查询科目列表
        cursor = conn.execute("SELECT DISTINCT subject FROM professional_questions")
        subjects = cursor.fetchall()

        conn.close()

        return format_response(
            success=True,
            data={
                'columns': [{'name': col['name'], 'type': col['type']} for col in columns],
                'sample_questions': [dict(q) for q in questions],
                'subjects': [s['subject'] for s in subjects]
            },
            message="专业题测试成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"专业题测试失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/database/update-structure', methods=['POST'])
def update_database_structure():
    """更新数据库结构，添加is_used字段"""
    try:
        conn = get_db_connection()

        # 检查翻译题表是否已有is_used字段
        cursor = conn.execute('PRAGMA table_info(translation_questions)')
        columns = [col['name'] for col in cursor.fetchall()]

        translation_updated = False
        if 'is_used' not in columns:
            conn.execute('ALTER TABLE translation_questions ADD COLUMN is_used BOOLEAN DEFAULT 0')
            translation_updated = True

        # 检查专业题表是否已有is_used字段
        cursor = conn.execute('PRAGMA table_info(professional_questions)')
        columns = [col['name'] for col in cursor.fetchall()]

        professional_updated = False
        if 'is_used' not in columns:
            conn.execute('ALTER TABLE professional_questions ADD COLUMN is_used BOOLEAN DEFAULT 0')
            professional_updated = True

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'translation_updated': translation_updated,
                'professional_updated': professional_updated
            },
            message="数据库结构更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"数据库结构更新失败: {str(e)}",
            status_code=500
        )

# 注意：健康检查路由已移至 system.py 子模块

# ==================== 考试记录管理路由 (简化版) ====================
# 注意：学生管理路由已移至 students.py 子模块

@exam_bp.route('/records', methods=['GET'])
def get_records():
    """获取考试记录列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, exam_status, created_at, updated_at
            FROM exam_records
            ORDER BY created_at DESC
        ''')

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
            data={'records': result},
            message=f"获取了 {len(result)} 条考试记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试记录失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/records', methods=['POST'])
def create_record():
    """创建考试记录"""
    try:
        data = request.get_json()

        if not data or 'studentNumber' not in data:
            return format_response(
                success=False,
                error="缺少必要参数：studentNumber",
                status_code=400
            )

        student_number = data.get('studentNumber')
        exam_status = data.get('examStatus', 0)

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

@exam_bp.route('/records/<student_number>', methods=['GET'])
def get_record(student_number):
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
            error=f"获取考试记录失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/records/<student_number>', methods=['PUT'])
def update_record(student_number):
    """更新考试记录"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        exam_status = data.get('examStatus')

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

        # 更新考试记录
        if exam_status is not None:
            cursor = conn.execute('''
                UPDATE exam_records
                SET exam_status = ?, updated_at = ?
                WHERE student_number = ?
            ''', (exam_status, datetime.now().isoformat(), student_number))

            conn.commit()

        conn.close()

        return format_response(
            success=True,
            message="考试记录更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新考试记录失败: {str(e)}",
            status_code=500
        )

# 注意：考试流程控制路由已移至 exam_flow.py 子模块

# ==================== 考试记录管理路由 ====================

@exam_bp.route('/exam-records', methods=['GET'])
def get_exam_records():
    """获取考试记录"""
    try:
        student_number = request.args.get('studentNumber')

        conn = get_db_connection()

        if student_number:
            # 获取指定学生的考试记录（通过联合查询获取current_step）
            cursor = conn.execute('''
                SELECT
                    er.id,
                    er.student_number,
                    s.current_step,
                    er.exam_status,
                    er.created_at,
                    er.updated_at
                FROM exam_records er
                LEFT JOIN students s ON er.student_number = s.student_number
                WHERE er.student_number = ?
                ORDER BY er.created_at DESC
            ''', (student_number,))
        else:
            # 获取所有考试记录（通过联合查询获取current_step）
            cursor = conn.execute('''
                SELECT
                    er.id,
                    er.student_number,
                    s.current_step,
                    er.exam_status,
                    er.created_at,
                    er.updated_at
                FROM exam_records er
                LEFT JOIN students s ON er.student_number = s.student_number
                ORDER BY er.created_at DESC
            ''')

        records = cursor.fetchall()
        conn.close()

        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'studentNumber': record['student_number'],
                'currentStep': record['current_step'] if record['current_step'] else 1,  # 默认为步骤1
                'status': record['exam_status'],
                'createdAt': record['created_at'],
                'updatedAt': record['updated_at']
            })

        message = f"获取了 {len(result)} 条考试记录"
        if student_number:
            message = f"获取学生 {student_number} 的 {len(result)} 条考试记录"

        return format_response(
            success=True,
            data=result,
            message=message
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试记录失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/exam-records', methods=['POST'])
def create_exam_record():
    """创建考试记录"""
    try:
        data = request.get_json()

        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['studentNumber'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )

        student_number = data.get('studentNumber')
        current_step = data.get('currentStep', 1)
        status = data.get('status', 'in_progress')

        conn = get_db_connection()

        # 创建考试记录
        cursor = conn.execute('''
            INSERT INTO exam_records (student_number, current_step, exam_date)
            VALUES (?, ?, ?)
        ''', (student_number, current_step, datetime.now().isoformat()))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'id': record_id,
                'studentNumber': student_number,
                'currentStep': current_step,
                'status': status,
                'createdAt': datetime.now().isoformat()
            },
            message="考试记录创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建考试记录失败: {str(e)}",
            status_code=500
        )

# 注意：考试重置路由已移至 exam_flow.py 子模块

@exam_bp.route('/reset', methods=['POST'])
def reset_system():
    """重置整个考试系统 - 按照用户要求的逻辑进行重置"""
    try:
        conn = get_db_connection()

        # 统计重置前的数据
        stats_before = {}

        # 统计考试记录数量
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM exam_records')
            stats_before['exam_records'] = cursor.fetchone()[0]
        except Exception:
            stats_before['exam_records'] = 0

        # 统计学生数量
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM students')
            stats_before['students'] = cursor.fetchone()[0]
        except Exception:
            stats_before['students'] = 0

        # 统计题目使用状态
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM translation_questions WHERE is_used = 1')
            stats_before['translation_used'] = cursor.fetchone()[0]
        except Exception:
            stats_before['translation_used'] = 0

        try:
            cursor = conn.execute('SELECT COUNT(*) FROM professional_questions WHERE is_used = 1')
            stats_before['professional_used'] = cursor.fetchone()[0]
        except Exception:
            stats_before['professional_used'] = 0

        # 开始事务
        conn.execute('BEGIN TRANSACTION')

        try:
            # 1. 清空考试记录表
            conn.execute('DELETE FROM exam_records')

            # 2. 清空学生表
            conn.execute('DELETE FROM students')

            # 3. 重置题目使用状态
            conn.execute('UPDATE translation_questions SET is_used = 0')
            conn.execute('UPDATE professional_questions SET is_used = 0')

            # 4. 重置自增ID
            conn.execute('DELETE FROM sqlite_sequence WHERE name IN (?, ?)',
                        ('students', 'exam_records'))

            # 提交事务
            conn.commit()

            # 统计重置后的数据
            stats_after = {}

            cursor = conn.execute('SELECT COUNT(*) FROM exam_records')
            stats_after['exam_records'] = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(*) FROM students')
            stats_after['students'] = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(*) FROM translation_questions WHERE is_used = 1')
            stats_after['translation_used'] = cursor.fetchone()[0]

            cursor = conn.execute('SELECT COUNT(*) FROM professional_questions WHERE is_used = 1')
            stats_after['professional_used'] = cursor.fetchone()[0]

            conn.close()

            total_records_cleared = stats_before['exam_records'] + stats_before['students']
            total_questions_reset = stats_before['translation_used'] + stats_before['professional_used']

            return format_response(
                success=True,
                data={
                    'resetAt': datetime.now().isoformat(),
                    'operation': 'system_reset',
                    'statsBeforeReset': stats_before,
                    'statsAfterReset': stats_after,
                    'recordsCleared': total_records_cleared,
                    'questionsReset': total_questions_reset
                },
                message=f"系统重置成功！清除了 {total_records_cleared} 条记录，重置了 {total_questions_reset} 个题目的使用状态"
            )

        except Exception as e:
            # 回滚事务
            conn.rollback()
            conn.close()
            raise e

    except Exception as e:
        return format_response(
            success=False,
            error=f"系统重置失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/clear-all-data', methods=['GET'])
def clear_all_data():
    """清空所有数据（GET请求，方便测试）"""
    try:
        conn = get_db_connection()

        # 统计清理前的数据
        cursor = conn.execute('SELECT COUNT(*) FROM students')
        students_count = cursor.fetchone()[0]

        cursor = conn.execute('SELECT COUNT(*) FROM exam_records')
        records_count = cursor.fetchone()[0]

        # 清空所有数据
        cursor = conn.execute('DELETE FROM exam_records')
        cursor = conn.execute('DELETE FROM students')

        # 重置自增ID序列
        cursor = conn.execute('DELETE FROM sqlite_sequence WHERE name IN ("students", "exam_records")')

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'studentsDeleted': students_count,
                'recordsDeleted': records_count,
                'resetAt': datetime.now().isoformat()
            },
            message=f"数据库清理成功！删除了 {students_count} 个学生和 {records_count} 条考试记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"清理数据库失败: {str(e)}",
            status_code=500
        )

# ==================== 统计分析路由 ====================

@exam_bp.route('/statistics/questions', methods=['GET'])
def get_question_statistics():
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

@exam_bp.route('/stats/overview', methods=['GET'])
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
                    'total': professional_count
                },
                'translation': {
                    'total': translation_count
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

# ==================== 考试步骤管理路由 ====================

@exam_bp.route('/exam-steps', methods=['GET'])
def get_exam_steps():
    """获取考试步骤配置"""
    try:
        conn = get_db_connection()

        # 检查exam_steps表是否存在，如果不存在则创建
        cursor = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='exam_steps'
        ''')

        if not cursor.fetchone():
            # 创建exam_steps表
            conn.execute('''
                CREATE TABLE exam_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_number INTEGER NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    step_type TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 插入默认考试步骤
            default_steps = [
                (1, '中文自我介绍', '请用中文进行自我介绍', 180, 'introduction'),
                (2, '英文自我介绍', '请用英文进行自我介绍', 180, 'introduction'),
                (3, '英文翻译', '请翻译以下内容', 300, 'translation'),
                (4, '专业问题', '请回答专业相关问题', 600, 'professional'),
                (5, '综合问答', '综合能力问答环节', 300, 'comprehensive'),
                (6, '考试结束', '总结评分', 0, 'completion')
            ]

            for step in default_steps:
                conn.execute('''
                    INSERT INTO exam_steps (step_number, title, description, duration, step_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', step)


            conn.commit()

        # 检查step_contents表是否存在，如果不存在则创建
        cursor = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='step_contents'
        ''')

        if not cursor.fetchone():
            # 创建内容指导表
            conn.execute('''
                CREATE TABLE step_contents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_number INTEGER NOT NULL,
                    content_type TEXT NOT NULL,
                    content_html TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (step_number) REFERENCES exam_steps (step_number)
                )
            ''')

            # 插入默认内容指导
            default_contents = [
                (1, 'introduction_tips', '''
                    <h4>中文自我介绍要点：</h4>
                    <ul>
                        <li>简要介绍个人基本信息（姓名、专业背景）</li>
                        <li>突出学术成就和研究兴趣</li>
                        <li>说明选择本专业的原因</li>
                        <li>表达对未来学习的期望</li>
                        <li>控制时间在3分钟以内</li>
                    </ul>
                '''),
                (2, 'introduction_tips', '''
                    <h4>English Self-Introduction Guidelines:</h4>
                    <ul>
                        <li>Introduce your name and academic background</li>
                        <li>Highlight your research interests and achievements</li>
                        <li>Explain why you chose this field</li>
                        <li>Express your expectations for future studies</li>
                        <li>Keep it within 3 minutes</li>
                    </ul>
                ''')
            ]

            for content in default_contents:
                conn.execute('''
                    INSERT INTO step_contents (step_number, content_type, content_html)
                    VALUES (?, ?, ?)
                ''', content)

            conn.commit()

        # 获取考试步骤
        cursor = conn.execute('''
            SELECT step_number, title, description, duration, step_type, is_active
            FROM exam_steps
            WHERE is_active = 1
            ORDER BY step_number
        ''')

        steps = cursor.fetchall()
        conn.close()

        result = []
        for step in steps:
            result.append({
                'id': step['step_number'],
                'step_number': step['step_number'],
                'title': step['title'],
                'description': step['description'],
                'duration': step['duration'],
                'step_type': step['step_type'],
                'type': step['step_type']
            })

        return format_response(
            success=True,
            data=result,
            message=f"获取了 {len(result)} 个考试步骤"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取考试步骤失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/exam-steps/<int:step_number>', methods=['PUT'])
def update_exam_step(step_number):
    """更新考试步骤配置"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        conn = get_db_connection()

        # 构建更新字段
        update_fields = []
        update_values = []

        allowed_fields = ['title', 'description', 'duration', 'step_type', 'is_active']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f'{field} = ?')
                update_values.append(data[field])

        if not update_fields:
            conn.close()
            return format_response(
                success=False,
                error="没有提供要更新的字段",
                status_code=400
            )

        # 添加updated_at字段
        update_fields.append('updated_at = ?')
        update_values.append(datetime.now().isoformat())
        update_values.append(step_number)

        # 执行更新
        sql = f"UPDATE exam_steps SET {', '.join(update_fields)} WHERE step_number = ?"
        cursor = conn.execute(sql, update_values)

        if cursor.rowcount == 0:
            conn.close()
            return format_response(
                success=False,
                error="考试步骤不存在",
                status_code=404
            )

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message=f"考试步骤 {step_number} 更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新考试步骤失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/exam-steps/<int:step_number>/content', methods=['GET'])
def get_step_content(step_number):
    """获取考试步骤的内容指导"""
    try:
        conn = get_db_connection()

        cursor = conn.execute('''
            SELECT content_type, content_html
            FROM step_contents
            WHERE step_number = ? AND is_active = 1
            ORDER BY content_type
        ''', (step_number,))

        contents = cursor.fetchall()
        conn.close()

        result = {}
        for content in contents:
            result[content['content_type']] = content['content_html']

        return format_response(
            success=True,
            data=result,
            message=f"获取步骤 {step_number} 的内容指导成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取步骤内容失败: {str(e)}",
            status_code=500
        )

# ==================== 设置管理路由 ====================

@exam_bp.route('/settings', methods=['GET'])
def get_settings():
    """获取考试系统设置"""
    try:
        conn = get_db_connection()

        # 从数据库获取考试步骤配置
        cursor = conn.execute('''
            SELECT step_number, title, description, duration, step_type
            FROM exam_steps
            WHERE is_active = 1
            ORDER BY step_number
        ''')

        steps = cursor.fetchall()
        conn.close()

        # 构建时间设置
        time_settings = {}
        for step in steps:
            time_settings[f'step{step["step_number"]}Time'] = step['duration']

        # 添加其他设置
        time_settings.update({
            'warningTime': 30,  # 警告时间（秒）
            'overtimeAllowed': False,  # 是否允许超时
            'overtimeLimit': 60  # 超时限制（秒）
        })

        settings = {
            'timeSettings': time_settings,
            'examSettings': {
                'totalSteps': len(steps),  # 总步骤数
                'autoSave': True,  # 自动保存
                'autoSaveInterval': 30,  # 自动保存间隔（秒）
                'allowPause': True,  # 允许暂停
                'allowSkip': False,  # 允许跳过
                'showProgress': True,  # 显示进度
                'showTimer': True,  # 显示计时器
                'randomQuestions': True  # 随机题目
            }
        }

        return format_response(
            success=True,
            data=settings,
            message="获取系统设置成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取系统设置失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/settings', methods=['PUT'])
def update_settings():
    """更新考试系统设置"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        # 这里可以添加设置验证和保存逻辑
        # 目前只返回成功响应，表示接收到了设置更新请求

        return format_response(
            success=True,
            data=data,
            message="设置更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新设置失败: {str(e)}",
            status_code=500
        )

# ==================== 步骤内容管理路由 ====================

@exam_bp.route('/step-contents', methods=['GET'])
def get_all_step_contents():
    """获取所有步骤内容列表"""
    try:
        conn = get_db_connection()

        cursor = conn.execute('''
            SELECT id, step_number, content_type, content_html, is_active,
                   created_at, updated_at
            FROM step_contents
            ORDER BY step_number, content_type
        ''')

        contents = cursor.fetchall()
        conn.close()

        result = []
        for content in contents:
            result.append({
                'id': content['id'],
                'stepNumber': content['step_number'],
                'contentType': content['content_type'],
                'contentHtml': content['content_html'],
                'isActive': bool(content['is_active']),
                'createdAt': content['created_at'],
                'updatedAt': content['updated_at']
            })

        return format_response(
            success=True,
            data=result,
            message="获取步骤内容列表成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取步骤内容列表失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/step-contents/<int:content_id>', methods=['GET'])
def get_step_content_by_id(content_id):
    """获取指定ID的步骤内容"""
    try:
        conn = get_db_connection()

        cursor = conn.execute('''
            SELECT id, step_number, content_type, content_html, is_active,
                   created_at, updated_at
            FROM step_contents
            WHERE id = ?
        ''', (content_id,))

        content = cursor.fetchone()
        conn.close()

        if not content:
            return format_response(
                success=False,
                error='步骤内容不存在',
                status_code=404
            )

        result = {
            'id': content['id'],
            'stepNumber': content['step_number'],
            'contentType': content['content_type'],
            'contentHtml': content['content_html'],
            'isActive': bool(content['is_active']),
            'createdAt': content['created_at'],
            'updatedAt': content['updated_at']
        }

        return format_response(
            success=True,
            data=result,
            message="获取步骤内容成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取步骤内容失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/step-contents', methods=['POST'])
def create_step_content():
    """创建新的步骤内容"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        step_number = data.get('stepNumber')
        content_type = data.get('contentType')
        content_html = data.get('contentHtml')
        is_active = data.get('isActive', True)

        # 验证必填字段
        if not all([step_number, content_type, content_html]):
            return format_response(
                success=False,
                error="步骤编号、内容类型和内容HTML不能为空",
                status_code=400
            )

        # 验证步骤编号范围
        if not (1 <= step_number <= 5):
            return format_response(
                success=False,
                error="步骤编号必须在1-5之间",
                status_code=400
            )

        conn = get_db_connection()

        # 检查是否已存在相同的步骤编号和内容类型组合
        cursor = conn.execute('''
            SELECT id FROM step_contents
            WHERE step_number = ? AND content_type = ?
        ''', (step_number, content_type))

        if cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error=f"步骤{step_number}的{content_type}类型内容已存在",
                status_code=400
            )

        # 插入新内容
        cursor = conn.execute('''
            INSERT INTO step_contents (step_number, content_type, content_html, is_active)
            VALUES (?, ?, ?, ?)
        ''', (step_number, content_type, content_html, is_active))

        content_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={'id': content_id},
            message="步骤内容创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建步骤内容失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/step-contents/<int:content_id>', methods=['PUT'])
def update_step_content(content_id):
    """更新步骤内容"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        conn = get_db_connection()

        # 检查内容是否存在
        cursor = conn.execute('''
            SELECT id FROM step_contents WHERE id = ?
        ''', (content_id,))

        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='步骤内容不存在',
                status_code=404
            )

        # 构建更新字段
        update_fields = []
        update_values = []

        allowed_fields = {
            'stepNumber': 'step_number',
            'contentType': 'content_type',
            'contentHtml': 'content_html',
            'isActive': 'is_active'
        }

        for field, db_field in allowed_fields.items():
            if field in data:
                # 特殊验证
                if field == 'stepNumber' and not (1 <= data[field] <= 5):
                    conn.close()
                    return format_response(
                        success=False,
                        error="步骤编号必须在1-5之间",
                        status_code=400
                    )

                update_fields.append(f'{db_field} = ?')
                update_values.append(data[field])

        if not update_fields:
            conn.close()
            return format_response(
                success=False,
                error="没有提供要更新的字段",
                status_code=400
            )

        # 添加updated_at字段
        update_fields.append('updated_at = ?')
        update_values.append(datetime.now().isoformat())
        update_values.append(content_id)

        # 执行更新
        sql = f"UPDATE step_contents SET {', '.join(update_fields)} WHERE id = ?"
        cursor = conn.execute(sql, update_values)

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message="步骤内容更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新步骤内容失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/step-contents/<int:content_id>', methods=['DELETE'])
def delete_step_content(content_id):
    """删除步骤内容"""
    try:
        conn = get_db_connection()

        # 检查内容是否存在
        cursor = conn.execute('''
            SELECT id FROM step_contents WHERE id = ?
        ''', (content_id,))

        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='步骤内容不存在',
                status_code=404
            )

        # 删除内容
        cursor = conn.execute('''
            DELETE FROM step_contents WHERE id = ?
        ''', (content_id,))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message="步骤内容删除成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"删除步骤内容失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/translation/<int:question_id>', methods=['GET'])
def get_translation_question_by_id(question_id):
    """根据ID获取翻译题目"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT * FROM translation_questions
            WHERE id = ?
        ''', (question_id,))

        question = cursor.fetchone()
        conn.close()

        if not question:
            return format_response(
                success=False,
                error="题目不存在",
                status_code=404
            )

        # 格式化题目数据
        from apis.common.utils import format_question_data
        result = format_question_data(question, 'translation')

        return format_response(success=True, data=result)

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取翻译题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/professional/<int:question_id>', methods=['GET'])
def get_professional_question_by_id(question_id):
    """根据ID获取专业题目"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT * FROM professional_questions
            WHERE id = ?
        ''', (question_id,))

        question = cursor.fetchone()
        conn.close()

        if not question:
            return format_response(
                success=False,
                error="题目不存在",
                status_code=404
            )

        # 格式化题目数据
        from apis.common.utils import format_question_data
        result = format_question_data(question, 'professional')

        return format_response(success=True, data=result)

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取专业题目失败: {str(e)}",
            status_code=500
        )


__all__ = ['exam_bp']
