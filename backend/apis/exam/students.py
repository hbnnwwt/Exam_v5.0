"""
考生管理模块 - 处理学生信息的CRUD操作
"""

from flask import request
from datetime import datetime
from ..common.database import get_db_connection
from ..common.utils import format_response, validate_request
from ..common.operation_logger import log_operation, OPERATION_START_EXAM, OPERATION_NEXT_STUDENT
from apis.exam import exam_bp

@exam_bp.route('/students/max-number', methods=['GET'])
def get_max_student_number():
    """获取最大学生编号"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT MAX(CAST(student_number AS INTEGER)) as max_number
            FROM students
        ''')
        result = cursor.fetchone()
        conn.close()

        max_number = result['max_number'] if result['max_number'] is not None else 0

        return format_response(
            success=True,
            data={'maxNumber': max_number}
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取最大学生编号失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students/next', methods=['POST'])
def create_next_student():
    """自动创建下一个考生（编号为当前最大编号+1）"""
    try:
        conn = get_db_connection()

        # 获取最大编号 - 优先从 students 表获取，如果为空则从 exam_records 获取
        cursor = conn.execute('SELECT MAX(CAST(student_number AS INTEGER)) as max_number FROM students')
        result = cursor.fetchone()
        max_number = result['max_number'] if result['max_number'] is not None else 0

        # 如果 students 表为空，尝试从 exam_records 获取
        if max_number == 0:
            cursor = conn.execute('SELECT MAX(CAST(student_number AS INTEGER)) as max_number FROM exam_records')
            result = cursor.fetchone()
            max_number = result['max_number'] if result['max_number'] is not None else 0

        next_number = max_number + 1

        # 格式化为两位字符串（01, 02, ...）
        student_number = str(next_number).zfill(2)

        # 创建新考生
        cursor = conn.execute('''
            INSERT INTO students (student_number, name, current_step, exam_status, created_at)
            VALUES (?, ?, 1, 'ready', datetime('now'))
        ''', (student_number, ''))

        student_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 记录操作日志
        ip_address = request.remote_addr
        log_operation(
            student_number=student_number,
            operation_type=OPERATION_START_EXAM,
            operation_detail=f'创建考生 {student_number}，开始考试',
            step_number=1,
            ip_address=ip_address
        )

        return format_response(
            success=True,
            data={
                'id': student_id,
                'studentNumber': student_number,
                'message': f'新考生 {student_number} 创建成功'
            },
            message=f'新考生 {student_number} 创建成功'
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建下一个考生失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students', methods=['GET'])
def get_students():
    """获取学生列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, name, current_step, exam_status,
                   start_time, end_time, total_duration, created_at
            FROM students
            ORDER BY CAST(student_number AS INTEGER)
        ''')
        students = cursor.fetchall()
        conn.close()

        result = []
        for student in students:
            result.append({
                'studentNumber': student['student_number'],
                'name': student['name'] or '',
                'currentStep': student['current_step'],
                'examStatus': student['exam_status'],
                'startTime': student['start_time'],
                'endTime': student['end_time'],
                'totalDuration': student['total_duration'],
                'createdAt': student['created_at']
            })

        return format_response(
            success=True,
            data=result,
            message=f"获取了 {len(result)} 个学生信息"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取学生列表失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students', methods=['POST'])
def create_student():
    """创建学生（如果存在则返回现有记录）"""
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
        name = data.get('name', '')
        current_step = data.get('currentStep', 1)
        exam_status = data.get('examStatus', 'ready')
        translation_question = data.get('translationQuestion')
        professional_question = data.get('professionalQuestion')
        professional_subject = data.get('professionalSubject', 'computer_science')
        step_data = data.get('stepData', '{}')
        start_time = data.get('startTime')

        conn = get_db_connection()

        # 检查学生编号是否已存在 - 如果存在则返回现有记录
        cursor = conn.execute('''
            SELECT id, student_number, name, current_step, exam_status,
                   translation_question, professional_question, professional_subject,
                   step_data, start_time, created_at
            FROM students WHERE student_number = ?
        ''', (student_number,))

        existing = cursor.fetchone()

        if existing:
            # 考生已存在，返回现有信息
            conn.close()
            return format_response(
                success=True,
                data={
                    'id': existing['id'],
                    'studentNumber': existing['student_number'],
                    'name': existing['name'] or '',
                    'currentStep': existing['current_step'],
                    'examStatus': existing['exam_status'],
                    'isExisting': True,
                    'message': '考生已存在，继续考试'
                },
                message="考生已存在，继续考试"
            )

        # 创建学生记录
        cursor = conn.execute('''
            INSERT INTO students (
                student_number, name, current_step, exam_status,
                translation_question, professional_question, professional_subject,
                step_data, start_time, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_number, name, current_step, exam_status,
            translation_question, professional_question, professional_subject,
            step_data, start_time,
            datetime.now().isoformat(), datetime.now().isoformat()
        ))

        student_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'id': student_id,
                'studentNumber': student_number,
                'name': name,
                'isExisting': False,
                'message': '新考生创建成功'
            },
            message="新考生创建成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建学生失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students/<student_number>', methods=['GET'])
def get_student(student_number):
    """获取指定学生信息"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT student_number, name, current_step, exam_status,
                   translation_question, professional_question, professional_subject,
                   step_data, start_time, end_time, total_duration,
                   created_at, updated_at
            FROM students
            WHERE student_number = ?
        ''', (student_number,))

        student = cursor.fetchone()
        conn.close()

        if not student:
            return format_response(
                success=False,
                error='学生不存在'
            )

        result = {
            'studentNumber': student['student_number'],
            'name': student['name'] or '',
            'currentStep': student['current_step'],
            'examStatus': student['exam_status'],
            'translationQuestion': student['translation_question'],
            'professionalQuestion': student['professional_question'],
            'professionalSubject': student['professional_subject'],
            'stepData': student['step_data'],
            'startTime': student['start_time'],
            'endTime': student['end_time'],
            'totalDuration': student['total_duration'],
            'createdAt': student['created_at'],
            'updatedAt': student['updated_at']
        }

        return format_response(
            success=True,
            data=result
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取学生信息失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students/<student_number>', methods=['PUT'])
def update_student(student_number):
    """更新学生信息"""
    try:
        data = request.get_json()

        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )

        # 获取更新字段
        name = data.get('name')
        current_step = data.get('currentStep')
        exam_status = data.get('examStatus')
        translation_question = data.get('translationQuestion')
        translation_question_id = data.get('translationQuestionId')
        professional_question = data.get('professionalQuestion')
        professional_question_id = data.get('professionalQuestionId')
        professional_subject = data.get('professionalSubject')
        step_data = data.get('stepData')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        total_duration = data.get('totalDuration')

        conn = get_db_connection()

        # 自动迁移：检查并添加缺失的字段
        try:
            cursor = conn.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]

            # 如果字段不存在，则添加
            if 'translation_question_id' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN translation_question_id INTEGER')
            if 'professional_question_id' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN professional_question_id INTEGER')
            if 'translation_question' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN translation_question TEXT')
            if 'professional_question' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN professional_question TEXT')
            if 'professional_subject' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN professional_subject TEXT')
            if 'step_data' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN step_data TEXT')
            if 'start_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN start_time TEXT')
            if 'end_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN end_time TEXT')
            if 'total_duration' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN total_duration INTEGER')

            conn.commit()
        except Exception as e:
            # 如果ALTER TABLE失败（字段已存在），忽略错误
            pass

        # 检查学生是否存在
        cursor = conn.execute('''
            SELECT id FROM students WHERE student_number = ?
        ''', (student_number,))

        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='学生不存在',
                status_code=404
            )

        # 构建动态更新语句
        update_fields = []
        update_values = []

        if name is not None:
            update_fields.append('name = ?')
            update_values.append(name)
        if current_step is not None:
            update_fields.append('current_step = ?')
            update_values.append(current_step)
        if exam_status is not None:
            update_fields.append('exam_status = ?')
            update_values.append(exam_status)
        if translation_question is not None:
            update_fields.append('translation_question = ?')
            update_values.append(translation_question)
        if translation_question_id is not None:
            update_fields.append('translation_question_id = ?')
            update_values.append(translation_question_id)
        if professional_question is not None:
            update_fields.append('professional_question = ?')
            update_values.append(professional_question)
        if professional_question_id is not None:
            update_fields.append('professional_question_id = ?')
            update_values.append(professional_question_id)
        if professional_subject is not None:
            update_fields.append('professional_subject = ?')
            update_values.append(professional_subject)
        if step_data is not None:
            update_fields.append('step_data = ?')
            update_values.append(step_data)
        if start_time is not None:
            update_fields.append('start_time = ?')
            update_values.append(start_time)
        if end_time is not None:
            update_fields.append('end_time = ?')
            update_values.append(end_time)
        if total_duration is not None:
            update_fields.append('total_duration = ?')
            update_values.append(total_duration)

        # 总是更新updated_at
        update_fields.append('updated_at = ?')
        update_values.append(datetime.now().isoformat())
        update_values.append(student_number)

        if not update_fields:
            conn.close()
            return format_response(
                success=False,
                error="没有提供要更新的字段",
                status_code=400
            )

        # 更新学生信息
        sql = f"UPDATE students SET {', '.join(update_fields)} WHERE student_number = ?"
        cursor = conn.execute(sql, update_values)

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            data={
                'studentNumber': student_number,
                'name': name
            },
            message="学生信息更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新学生信息失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/students/<student_number>', methods=['DELETE'])
def delete_student(student_number):
    """删除学生"""
    try:
        conn = get_db_connection()
        
        # 检查学生是否存在
        cursor = conn.execute('''
            SELECT id FROM students WHERE student_number = ?
        ''', (student_number,))
        
        if not cursor.fetchone():
            conn.close()
            return format_response(
                success=False,
                error='学生不存在',
                status_code=404
            )

        # 删除学生记录
        cursor = conn.execute('''
            DELETE FROM students WHERE student_number = ?
        ''', (student_number,))

        conn.commit()
        conn.close()

        return format_response(
            success=True,
            message="学生删除成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"删除学生失败: {str(e)}",
            status_code=500
        )
