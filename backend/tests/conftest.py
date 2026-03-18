"""
测试配置文件
"""
import os
import sys
import tempfile
import sqlite3

# 添加项目路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 测试配置
TEST_DATABASE = os.path.join(tempfile.gettempdir(), 'test_interview_system.db')

# 测试配置类
class TestConfig:
    """测试环境配置"""
    SECRET_KEY = 'test-secret-key'
    DEBUG = True
    TESTING = True
    DATABASE = TEST_DATABASE
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = tempfile.gettempdir()

def setup_test_db():
    """创建测试数据库"""
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)
    
    conn = sqlite3.connect(TEST_DATABASE)
    cursor = conn.cursor()
    
    # 创建学生表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT UNIQUE NOT NULL,
            name TEXT,
            current_step INTEGER DEFAULT 1,
            exam_status TEXT DEFAULT 'ready',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 创建题目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_index INTEGER UNIQUE NOT NULL,
            question_data TEXT,
            is_used BOOLEAN DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professional_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_index INTEGER UNIQUE NOT NULL,
            question_data TEXT,
            difficulty TEXT,
            subject TEXT,
            is_used BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    return TEST_DATABASE

def teardown_test_db():
    """清理测试数据库"""
    if os.path.exists(TEST_DATABASE):
        try:
            os.remove(TEST_DATABASE)
        except:
            pass
