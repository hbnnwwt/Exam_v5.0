"""
考试流程控制模块 - 处理考试的开始、步骤更新、完成等流程控制
"""

from flask import request
from datetime import datetime
from ..common.database import get_db_connection
from ..common.utils import format_response, validate_request
from ..common.operation_logger import log_operation, OPERATION_COMPLETE_EXAM, OPERATION_RESET_SYSTEM, OPERATION_NEXT_STEP
from . import exam_bp

@exam_bp.route('/current-student', methods=['GET'])
def get_current_student():
    """获取当前考试学生信息"""
    try:
        conn = get_db_connection()
        
        # 查找最新的未完成考试记录
        cursor = conn.execute('''
            SELECT student_number, current_step, exam_status, created_at
            FROM exam_records
            WHERE exam_status != 'completed'
            ORDER BY created_at DESC
            LIMIT 1
        ''')
        
        current_exam = cursor.fetchone()
        
        if current_exam:
            result = {
                'studentNumber': current_exam['student_number'],
                'currentStep': current_exam['current_step'],
                'examStatus': current_exam['exam_status'],
                'startTime': current_exam['created_at']
            }
        else:
            # 如果没有进行中的考试，生成下一个学生编号
            cursor = conn.execute('''
                SELECT MAX(CAST(student_number AS INTEGER)) as max_number
                FROM exam_records
            ''')
            max_result = cursor.fetchone()
            next_number = (max_result['max_number'] or 0) + 1
            
            result = {
                'studentNumber': str(next_number),
                'currentStep': 1,
                'examStatus': 'ready',
                'startTime': None
            }
        
        conn.close()
        
        return format_response(
            success=True,
            data=result
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取当前学生信息失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/start', methods=['POST'])
def start_exam():
    """开始考试"""
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
        
        conn = get_db_connection()
        
        # 检查是否已有进行中的考试
        cursor = conn.execute('''
            SELECT id FROM exam_records
            WHERE student_number = ? AND exam_status != 'completed'
        ''', (student_number,))
        
        existing_exam = cursor.fetchone()
        
        if existing_exam:
            conn.close()
            return format_response(
                success=False,
                error='该学生已有进行中的考试',
                status_code=400
            )

        # 自动迁移：检查并添加 students 表缺失的字段
        try:
            cursor = conn.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'start_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN start_time TEXT')
            if 'end_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN end_time TEXT')
            if 'total_duration' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN total_duration INTEGER')
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

            conn.commit()
        except Exception:
            pass

        # 创建新的考试记录
        cursor = conn.execute('''
            INSERT INTO exam_records (
                student_number, current_step, exam_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (student_number, 1, 'in_progress', datetime.now().isoformat(), datetime.now().isoformat()))

        exam_id = cursor.lastrowid

        # 同步更新 students 表的 start_time 和 exam_status
        now = datetime.now().isoformat()

        # 检查 students 表中是否存在该考生记录
        cursor = conn.execute('SELECT id FROM students WHERE student_number = ?', (student_number,))
        existing_student = cursor.fetchone()

        if existing_student:
            # 更新已有记录
            cursor = conn.execute('''
                UPDATE students
                SET start_time = ?, exam_status = 'in_progress', updated_at = ?
                WHERE student_number = ?
            ''', (now, now, student_number))
        else:
            # 插入新记录
            cursor = conn.execute('''
                INSERT INTO students (student_number, start_time, exam_status, current_step, created_at, updated_at)
                VALUES (?, ?, 'in_progress', 1, ?, ?)
            ''', (student_number, now, now, now))

        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={
                'examId': exam_id,
                'studentNumber': student_number,
                'currentStep': 1,
                'examStatus': 'in_progress'
            },
            message="考试开始成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"开始考试失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/update-step', methods=['POST'])
def update_step():
    """更新考试步骤"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['studentNumber', 'currentStep'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )
        
        student_number = data.get('studentNumber')
        current_step = data.get('currentStep')
        step_data = data.get('stepData', {})
        
        conn = get_db_connection()
        
        # 更新考试记录
        update_fields = ['current_step = ?', 'updated_at = ?']
        update_values = [current_step, datetime.now().isoformat()]
        
        # 根据步骤更新相应字段
        if current_step == 3 and 'translationQuestion' in step_data:
            update_fields.append('translation_question = ?')
            update_values.append(step_data['translationQuestion'])
        elif current_step == 4 and 'professionalQuestion' in step_data:
            update_fields.append('professional_question = ?')
            update_values.append(step_data['professionalQuestion'])
        
        update_values.append(student_number)
        
        cursor = conn.execute(f'''
            UPDATE exam_records 
            SET {', '.join(update_fields)}
            WHERE student_number = ? AND exam_status != 'completed'
        ''', update_values)
        
        if cursor.rowcount == 0:
            conn.close()
            return format_response(
                success=False,
                error='考试记录不存在或已完成',
                status_code=404
            )
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={
                'studentNumber': student_number,
                'currentStep': current_step,
                'updated': True
            },
            message="考试步骤更新成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新考试步骤失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/complete', methods=['POST'])
def complete_exam():
    """完成考试"""
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

        conn = get_db_connection()

        # 自动迁移：检查并添加 students 表缺失的字段
        try:
            cursor = conn.execute("PRAGMA table_info(students)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'start_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN start_time TEXT')
            if 'end_time' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN end_time TEXT')
            if 'total_duration' not in columns:
                conn.execute('ALTER TABLE students ADD COLUMN total_duration INTEGER')
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

            conn.commit()
        except Exception:
            pass

        # 自动迁移：检查并添加缺失的字段
        try:
            cursor = conn.execute("PRAGMA table_info(exam_records)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'completed_at' not in columns:
                conn.execute('ALTER TABLE exam_records ADD COLUMN completed_at TEXT')
            if 'current_step_remaining_time' not in columns:
                conn.execute('ALTER TABLE exam_records ADD COLUMN current_step_remaining_time INTEGER DEFAULT 0')
            if 'translation_question_id' not in columns:
                conn.execute('ALTER TABLE exam_records ADD COLUMN translation_question_id INTEGER')
            if 'professional_question_id' not in columns:
                conn.execute('ALTER TABLE exam_records ADD COLUMN professional_question_id INTEGER')
            if 'used_question_ids' not in columns:
                conn.execute('ALTER TABLE exam_records ADD COLUMN used_question_ids TEXT')

            conn.commit()
        except Exception:
            pass

        # 动态获取最大步骤数
        cursor = conn.execute('SELECT MAX(step_number) as max_step FROM exam_steps WHERE is_active = 1')
        max_step = cursor.fetchone()['max_step'] or 6

        cursor = conn.execute('''
            UPDATE exam_records
            SET exam_status = 'completed',
                current_step = ?,
                completed_at = ?,
                updated_at = ?
            WHERE student_number = ? AND exam_status != 'completed'
        ''', (max_step, datetime.now().isoformat(), datetime.now().isoformat(), student_number))

        # 同时更新 students 表的 exam_status 和时长
        # 计算考试时长（秒）
        cursor = conn.execute('''
            SELECT start_time FROM students WHERE student_number = ?
        ''', (student_number,))
        student = cursor.fetchone()
        start_time = student['start_time'] if student else None
        total_duration = 0
        if start_time:
            end_time = datetime.now()
            start_dt = datetime.fromisoformat(start_time)
            total_duration = int((end_time - start_dt).total_seconds())
        else:
            # 如果没有开始时间记录，尝试从 exam_records 获取创建时间
            cursor = conn.execute('''
                SELECT created_at FROM exam_records WHERE student_number = ? ORDER BY created_at ASC LIMIT 1
            ''', (student_number,))
            exam_record = cursor.fetchone()
            if exam_record and exam_record['created_at']:
                # 设置开始时间
                start_time = exam_record['created_at']
                end_time = datetime.now()
                start_dt = datetime.fromisoformat(start_time)
                total_duration = int((end_time - start_dt).total_seconds())

        # 检查 students 表中是否存在该考生记录
        cursor = conn.execute('SELECT id FROM students WHERE student_number = ?', (student_number,))
        existing_student = cursor.fetchone()

        if existing_student:
            cursor = conn.execute('''
                UPDATE students
                SET exam_status = 'completed',
                    current_step = ?,
                    end_time = ?,
                    total_duration = ?,
                    updated_at = ?
                WHERE student_number = ?
            ''', (max_step, datetime.now().isoformat(), total_duration, datetime.now().isoformat(), student_number))

            if cursor.rowcount == 0:
                conn.close()
                return format_response(
                    success=False,
                    error='考试记录不存在或已完成',
                    status_code=404
                )
        else:
            # 插入新记录
            cursor = conn.execute('''
                INSERT INTO students (student_number, exam_status, current_step, end_time, total_duration, created_at, updated_at)
                VALUES (?, 'completed', ?, ?, ?, ?, ?)
            ''', (student_number, max_step, datetime.now().isoformat(), total_duration, datetime.now().isoformat(), datetime.now().isoformat()))

        conn.commit()
        conn.close()

        # 记录操作日志
        ip_address = request.remote_addr
        log_operation(
            student_number=student_number,
            operation_type=OPERATION_COMPLETE_EXAM,
            operation_detail=f'考生 {student_number} 完成考试',
            step_number=max_step,
            ip_address=ip_address
        )

        return format_response(
            success=True,
            data={
                'studentNumber': student_number,
                'examStatus': 'completed',
                'completedAt': datetime.now().isoformat()
            },
            message="考试完成成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"完成考试失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/reset', methods=['POST'])
def reset_exam():
    """重置考试系统"""
    try:
        conn = get_db_connection()

        # 清空考试记录
        cursor = conn.execute('DELETE FROM exam_records')
        deleted_exam_records = cursor.rowcount

        # 清空考生记录（确保下一个考生从头开始）
        cursor = conn.execute('DELETE FROM students')
        deleted_students = cursor.rowcount

        conn.commit()
        conn.close()

        # 记录操作日志
        ip_address = request.remote_addr
        log_operation(
            student_number=None,
            operation_type=OPERATION_RESET_SYSTEM,
            operation_detail=f'重置系统，删除了 {deleted_exam_records} 条考试记录和 {deleted_students} 条考生记录',
            ip_address=ip_address
        )

        return format_response(
            success=True,
            data={
                'deletedExamRecords': deleted_exam_records,
                'deletedStudents': deleted_students,
                'resetAt': datetime.now().isoformat()
            },
            message=f"考试系统重置成功，删除了 {deleted_exam_records} 条考试记录和 {deleted_students} 条考生记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"重置考试系统失败: {str(e)}",
            status_code=500
        )

# ==================== 考试进度保存和恢复 ====================

@exam_bp.route('/progress/save', methods=['POST'])
def save_exam_progress():
    """保存考试进度"""
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
        remaining_time = data.get('remainingTime', 0)
        translation_question_id = data.get('translationQuestionId')
        professional_question_id = data.get('professionalQuestionId')
        used_question_ids = data.get('usedQuestionIds', [])
        exam_status = data.get('examStatus', 'in_progress')
        
        import json
        
        conn = get_db_connection()
        
        # 查找该学生的考试记录
        cursor = conn.execute('''
            SELECT id FROM exam_records
            WHERE student_number = ?
        ''', (student_number,))
        
        existing_record = cursor.fetchone()
        
        if existing_record:
            # 更新已有记录
            cursor = conn.execute('''
                UPDATE exam_records 
                SET current_step = ?,
                    current_step_remaining_time = ?,
                    translation_question_id = ?,
                    professional_question_id = ?,
                    used_question_ids = ?,
                    exam_status = ?,
                    updated_at = ?
                WHERE student_number = ?
            ''', (current_step, remaining_time, translation_question_id, 
                  professional_question_id, json.dumps(used_question_ids),
                  exam_status, datetime.now().isoformat(), student_number))
        else:
            # 创建新记录
            cursor = conn.execute('''
                INSERT INTO exam_records (
                    student_number, current_step, current_step_remaining_time,
                    translation_question_id, professional_question_id,
                    used_question_ids, exam_status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_number, current_step, remaining_time,
                  translation_question_id, professional_question_id,
                  json.dumps(used_question_ids), exam_status,
                  datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={
                'studentNumber': student_number,
                'savedAt': datetime.now().isoformat()
            },
            message="考试进度保存成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"保存考试进度失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/progress/load', methods=['GET'])
def load_exam_progress():
    """加载考试进度"""
    try:
        import sys
        print('[DEBUG] load_exam_progress called', flush=True)
        sys.stdout.flush()
        conn = get_db_connection()
        
        # 查找最新的未完成考试记录
        cursor = conn.execute('''
            SELECT student_number, current_step, current_step_remaining_time,
                   translation_question_id, professional_question_id,
                   used_question_ids, exam_status, created_at
            FROM exam_records
            WHERE exam_status != 'completed'
            ORDER BY updated_at DESC
            LIMIT 1
        ''')
        
        record = cursor.fetchone()
        
        if record:
            import json
            used_ids = json.loads(record['used_question_ids']) if record['used_question_ids'] else []
            print(f'[DEBUG] load_exam_progress: hasProgress=True, usedQuestionIds={used_ids}', flush=True)
            result = {
                'hasProgress': True,
                'studentNumber': record['student_number'],
                'currentStep': record['current_step'] or 1,
                'remainingTime': record['current_step_remaining_time'] or 0,
                'translationQuestionId': record['translation_question_id'],
                'professionalQuestionId': record['professional_question_id'],
                'usedQuestionIds': used_ids,
                'examStatus': record['exam_status'],
                'startTime': record['created_at']
            }
        else:
            # 没有进行中的考试，返回下一个考生编号
            # 同时获取所有已使用题目ID（用于新考生时标记已使用题目）
            import json
            all_used_ids = set()
            cursor = conn.execute('''
                SELECT used_question_ids FROM exam_records
                WHERE used_question_ids IS NOT NULL AND used_question_ids != ''
            ''')
            for row in cursor.fetchall():
                try:
                    ids = json.loads(row['used_question_ids'])
                    if isinstance(ids, list):
                        all_used_ids.update(ids)
                except:
                    pass

            cursor = conn.execute('''
                SELECT MAX(CAST(student_number AS INTEGER)) as max_number
                FROM exam_records
            ''')
            max_result = cursor.fetchone()
            next_number = (max_result['max_number'] or 0) + 1

            # 检查最后一个考生是否已完成考试（从 students 表查询）
            cursor = conn.execute('''
                SELECT student_number, exam_status FROM students
                ORDER BY CAST(student_number AS INTEGER) DESC LIMIT 1
            ''')
            last_student = cursor.fetchone()
            last_student_num = last_student['student_number'] if last_student else None
            last_exam_status = last_student['exam_status'] if last_student else None

            print(f'[DEBUG] last_student_num={last_student_num}, last_exam_status={last_exam_status}', flush=True)

            # 如果最后一个考生已完成考试，需要手动开始新的考试
            result_exam_status = 'ready'
            if last_exam_status == 'completed':
                result_exam_status = 'completed'

            result = {
                'hasProgress': False,
                'studentNumber': str(next_number),
                'currentStep': 1,
                'remainingTime': 0,
                'examStatus': result_exam_status,
                'startTime': None,
                'allUsedQuestionIds': list(all_used_ids)  # 所有已使用的题目ID
            }
            print(f'[DEBUG] load_exam_progress: hasProgress=False, examStatus={result_exam_status}, allUsedQuestionIds={list(all_used_ids)}', flush=True)
        
        conn.close()
        
        return format_response(
            success=True,
            data=result
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"加载考试进度失败: {str(e)}",
            status_code=500
        )

# ==================== 操作日志 ====================

@exam_bp.route('/operation-logs', methods=['GET'])
def get_operation_logs():
    """获取操作日志列表"""
    try:
        student_number = request.args.get('studentNumber')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # 确保表存在
        from ..common.operation_logger import ensure_operation_logs_table
        ensure_operation_logs_table()

        conn = get_db_connection()

        # 构建查询条件
        sql = 'SELECT * FROM operation_logs'
        params = []

        if student_number:
            sql += ' WHERE student_number = ?'
            params.append(student_number)

        sql += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        cursor = conn.execute(sql, params)
        logs = cursor.fetchall()

        # 获取总数
        count_sql = 'SELECT COUNT(*) as total FROM operation_logs'
        if student_number:
            count_sql += ' WHERE student_number = ?'
            count_params = [student_number]
        else:
            count_params = []

        cursor = conn.execute(count_sql, count_params)
        total = cursor.fetchone()['total']

        conn.close()

        result = []
        for log in logs:
            result.append({
                'id': log['id'],
                'studentNumber': log['student_number'],
                'operationType': log['operation_type'],
                'operationDetail': log['operation_detail'],
                'stepNumber': log['step_number'],
                'createdAt': log['created_at'],
                'ipAddress': log['ip_address']
            })

        return format_response(
            success=True,
            data={
                'logs': result,
                'total': total,
                'limit': limit,
                'offset': offset
            },
            message=f"获取了 {len(result)} 条操作日志"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取操作日志失败: {str(e)}",
            status_code=500
        )
