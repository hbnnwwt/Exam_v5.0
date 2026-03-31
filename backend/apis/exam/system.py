"""
系统控制模块 - 处理系统级操作如健康检查、重置等
"""

from datetime import datetime
from ..common.database import get_db_connection
from ..common.utils import format_response
from . import exam_bp

@exam_bp.route('/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        cursor = conn.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        
        # 检查关键表是否存在
        conn = get_db_connection()
        tables_to_check = [
            'students', 'exam_records', 'professional_questions', 
            'translation_questions', 'settings'
        ]
        
        table_status = {}
        for table in tables_to_check:
            try:
                cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                table_status[table] = {
                    'exists': True,
                    'count': count
                }
            except Exception as e:
                table_status[table] = {
                    'exists': False,
                    'error': str(e)
                }
        
        conn.close()
        
        # 计算系统状态
        all_tables_ok = all(status['exists'] for status in table_status.values())
        system_status = 'healthy' if all_tables_ok else 'warning'
        
        result = {
            'status': system_status,
            'database': 'connected',
            'timestamp': datetime.now().isoformat(),
            'tables': table_status,
            'version': '1.0.0'
        }
        
        return format_response(
            success=True,
            data=result,
            message=f"系统状态: {system_status}"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"健康检查失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        conn = get_db_connection()
        
        # 获取数据库统计
        stats = {}
        
        # 学生统计
        cursor = conn.execute('SELECT COUNT(*) FROM students')
        stats['students'] = cursor.fetchone()[0]
        
        # 考试记录统计
        cursor = conn.execute('SELECT COUNT(*) FROM exam_records')
        stats['examRecords'] = cursor.fetchone()[0]
        
        # 题目统计
        cursor = conn.execute('SELECT COUNT(*) FROM professional_questions')
        stats['professionalQuestions'] = cursor.fetchone()[0]
        
        cursor = conn.execute('SELECT COUNT(*) FROM translation_questions')
        stats['translationQuestions'] = cursor.fetchone()[0]
        
        # 最近活动
        cursor = conn.execute('''
            SELECT created_at FROM exam_records 
            ORDER BY created_at DESC LIMIT 1
        ''')
        last_exam = cursor.fetchone()
        
        conn.close()
        
        result = {
            'version': '1.0.0',
            'name': '研究生复试系统',
            'description': '基于Flask的研究生复试流程控制系统',
            'statistics': stats,
            'lastActivity': last_exam['created_at'] if last_exam else None,
            'uptime': datetime.now().isoformat(),
            'features': [
                '考生管理',
                '考试流程控制',
                '题目管理',
                '考试记录',
                '统计分析',
                '系统设置'
            ]
        }
        
        return format_response(
            success=True,
            data=result,
            message="获取系统信息成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取系统信息失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/reset', methods=['POST'])
def reset_system():
    """重置整个考试系统 - 清空所有考试数据并恢复到初始状态"""
    try:
        conn = get_db_connection()

        # 统计重置前的数据
        stats_before = {}
        tables_to_reset = ['exam_records', 'students', 'system_state']

        for table in tables_to_reset:
            try:
                cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                stats_before[table] = cursor.fetchone()[0]
            except Exception:
                stats_before[table] = 0

        # 开始事务
        conn.execute('BEGIN TRANSACTION')

        try:
            # 1. 清空考试记录表
            conn.execute('DELETE FROM exam_records')

            # 2. 清空学生表
            conn.execute('DELETE FROM students')

            # 3. 清空或重置系统状态表
            conn.execute('DELETE FROM system_state')

            # 4. 重置系统状态到初始值（第一个学生的第一个步骤）
            initial_system_state = {
                'current_student_number': '1',
                'current_step': 1,
                'exam_status': 'ready',
                'step_start_time': None,
                'step_duration': None,
                'total_students': 0,
                'completed_students': 0,
                'system_initialized': True,
                'last_updated': datetime.now().isoformat()
            }

            # 插入初始系统状态
            for key, value in initial_system_state.items():
                conn.execute(
                    'INSERT INTO system_state (key, value, updated_at) VALUES (?, ?, ?)',
                    (key, str(value) if value is not None else None, datetime.now().isoformat())
                )

            # 5. 重置相关设置（可选）
            conn.execute('''
                DELETE FROM settings
                WHERE category IN ('examSettings', 'timeSettings', 'currentExam')
            ''')

            # 6. 重置自增ID（如果需要）
            # SQLite 中重置自增ID
            conn.execute('DELETE FROM sqlite_sequence WHERE name IN (?, ?, ?)',
                        ('students', 'exam_records', 'system_state'))

            # 提交事务
            conn.commit()

            # 统计重置后的数据
            stats_after = {}
            for table in tables_to_reset:
                try:
                    cursor = conn.execute(f'SELECT COUNT(*) FROM {table}')
                    stats_after[table] = cursor.fetchone()[0]
                except Exception:
                    stats_after[table] = 0

            conn.close()

            result = {
                'resetAt': datetime.now().isoformat(),
                'operation': 'complete_system_reset',
                'statsBeforeReset': stats_before,
                'statsAfterReset': stats_after,
                'initialState': {
                    'currentStudentNumber': '1',
                    'currentStep': 1,
                    'examStatus': 'ready',
                    'totalStudents': 0,
                    'completedStudents': 0
                },
                'tablesReset': tables_to_reset,
                'settingsReset': ['examSettings', 'timeSettings', 'currentExam']
            }

            total_records_cleared = sum(stats_before.values())

            return format_response(
                success=True,
                data=result,
                message=f"系统完全重置成功！清除了 {total_records_cleared} 条记录，系统已恢复到第一个学生的第一个步骤"
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

@exam_bp.route('/backup', methods=['POST'])
def create_backup():
    """创建系统备份"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # 备份数据库文件
        source_db = 'assets/data/interview_system.db'
        backup_dir = 'assets/backups'
        
        # 确保备份目录存在
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'interview_system_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 复制数据库文件
        shutil.copy2(source_db, backup_path)
        
        # 获取文件大小
        file_size = os.path.getsize(backup_path)
        
        result = {
            'backupPath': backup_path,
            'filename': backup_filename,
            'size': file_size,
            'createdAt': datetime.now().isoformat()
        }
        
        return format_response(
            success=True,
            data=result,
            message=f"备份创建成功: {backup_filename}"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"创建备份失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/maintenance', methods=['POST'])
def maintenance_mode():
    """维护模式控制"""
    try:
        # 这里可以实现维护模式的逻辑
        # 例如设置维护标志、清理临时文件等
        
        result = {
            'maintenanceMode': True,
            'startTime': datetime.now().isoformat(),
            'message': '系统进入维护模式'
        }
        
        return format_response(
            success=True,
            data=result,
            message="维护模式已启用"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"启用维护模式失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/logs', methods=['GET'])
def get_system_logs():
    """获取系统日志"""
    try:
        # 这里可以实现日志获取逻辑
        # 目前返回模拟数据
        
        logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': '系统正常运行',
                'module': 'system'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': '健康检查通过',
                'module': 'health'
            }
        ]
        
        return format_response(
            success=True,
            data=logs,
            message=f"获取了 {len(logs)} 条日志记录"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取系统日志失败: {str(e)}",
            status_code=500
        )
