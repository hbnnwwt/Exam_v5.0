"""
操作日志模块 - 记录考生关键操作到数据库
"""

from datetime import datetime
import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from apis.common.database import get_db_connection


def ensure_operation_logs_table():
    """确保操作日志表存在"""
    conn = get_db_connection()
    try:
        # 检查表是否存在
        cursor = conn.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='operation_logs'
        ''')

        if not cursor.fetchone():
            # 创建操作日志表
            conn.execute('''
                CREATE TABLE operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_number TEXT,
                    operation_type TEXT NOT NULL,
                    operation_detail TEXT,
                    step_number INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            ''')
            conn.commit()
    finally:
        conn.close()


def log_operation(student_number, operation_type, operation_detail=None, step_number=None, ip_address=None):
    """
    记录操作日志

    Args:
        student_number: 考生编号
        operation_type: 操作类型
        operation_detail: 操作详情
        step_number: 步骤编号
        ip_address: IP地址
    """
    try:
        # 确保表存在
        ensure_operation_logs_table()

        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO operation_logs (
                student_number, operation_type, operation_detail, step_number, created_at, ip_address
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            student_number,
            operation_type,
            operation_detail,
            step_number,
            datetime.now().isoformat(),
            ip_address
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # 日志记录失败不应影响主业务
        print(f"记录操作日志失败: {e}")
        return False


# 操作类型常量
OPERATION_START_EXAM = 'start_exam'           # 开始考试
OPERATION_NEXT_STEP = 'next_step'             # 进入下一步
OPERATION_PREV_STEP = 'prev_step'             # 进入上一步
OPERATION_DRAW_QUESTION = 'draw_question'      # 抽取题目
OPERATION_COMPLETE_EXAM = 'complete_exam'     # 完成考试
OPERATION_NEXT_STUDENT = 'next_student'       # 下一个考生
OPERATION_RESET_SYSTEM = 'reset_system'       # 重置系统
OPERATION_VIEW_QUESTION = 'view_question'      # 查看题目
