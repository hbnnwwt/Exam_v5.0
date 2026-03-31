"""
基础单元测试 - 测试核心功能
"""
import os
import sys
import unittest
import tempfile
import sqlite3
import json
from datetime import datetime

# 添加项目路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 测试用的临时数据库
TEST_DB = os.path.join(tempfile.gettempdir(), 'test_core.db')

def setup_module(module):
    """测试模块初始化"""
    # 创建测试数据库
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    
    # 学生表
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT UNIQUE NOT NULL,
            name TEXT,
            current_step INTEGER DEFAULT 1,
            exam_status TEXT DEFAULT 'ready',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 翻译题表
    cursor.execute('''
        CREATE TABLE translation_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_index INTEGER UNIQUE NOT NULL,
            question_data TEXT,
            is_used BOOLEAN DEFAULT 0
        )
    ''')
    
    # 专业题表
    cursor.execute('''
        CREATE TABLE professional_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_index INTEGER UNIQUE NOT NULL,
            question_data TEXT,
            difficulty TEXT,
            subject TEXT,
            is_used BOOLEAN DEFAULT 0
        )
    ''')
    
    # 插入测试数据
    cursor.execute('''
        INSERT INTO students (student_number, name, current_step, exam_status, created_at, updated_at)
        VALUES ('01', '张三', 1, 'ready', datetime('now'), datetime('now'))
    ''')
    
    cursor.execute('''
        INSERT INTO translation_questions (question_index, question_data, is_used)
        VALUES (1, '[{"content":"Test translation question"}]', 0)
    ''')
    
    cursor.execute('''
        INSERT INTO professional_questions (question_index, question_data, difficulty, subject, is_used)
        VALUES (1, '[{"content":"Test professional question"}]', 'medium', 'computer_science', 0)
    ''')
    
    conn.commit()
    conn.close()

def teardown_module(module):
    """测试模块清理"""
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except:
            pass


class TestDatabaseConnection(unittest.TestCase):
    """测试数据库连接"""
    
    def test_database_exists(self):
        """测试数据库文件存在"""
        self.assertTrue(os.path.exists(TEST_DB))
    
    def test_database_connection(self):
        """测试数据库连接"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        self.assertEqual(result[0], 1)


class TestStudentOperations(unittest.TestCase):
    """测试学生操作"""
    
    def test_get_all_students(self):
        """测试获取所有学生"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute('SELECT * FROM students')
        students = cursor.fetchall()
        conn.close()
        self.assertGreater(len(students), 0)
    
    def test_student_number_unique(self):
        """测试学生编号唯一性约束"""
        conn = sqlite3.connect(TEST_DB)
        try:
            cursor = conn.execute('''
                INSERT INTO students (student_number, name, created_at, updated_at)
                VALUES ('01', '重复', datetime('now'), datetime('now'))
            ''')
            conn.commit()
            self.fail("应该抛出唯一性约束错误")
        except sqlite3.IntegrityError:
            pass  # 预期错误
        finally:
            conn.close()


class TestQuestionOperations(unittest.TestCase):
    """测试题目操作"""
    
    def test_get_translation_questions(self):
        """测试获取翻译题"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute('SELECT * FROM translation_questions')
        questions = cursor.fetchall()
        conn.close()
        self.assertGreater(len(questions), 0)
    
    def test_get_professional_questions(self):
        """测试获取专业题"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute('SELECT * FROM professional_questions')
        questions = cursor.fetchall()
        conn.close()
        self.assertGreater(len(questions), 0)
    
    def test_professional_question_subject(self):
        """测试专业题科目筛选"""
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute(
            'SELECT * FROM professional_questions WHERE subject = ?',
            ('computer_science',)
        )
        questions = cursor.fetchall()
        conn.close()
        self.assertGreater(len(questions), 0)


class TestUtilsModule(unittest.TestCase):
    """测试工具模块"""
    
    def test_format_response(self):
        """测试响应格式化"""
        from flask import Flask
        app = Flask(__name__)
        
        with app.app_context():
            from apis.common.utils import format_response
            
            response = format_response(success=True, data={'test': 'value'})
            self.assertEqual(response[1], 200)
            
            response = format_response(success=False, error='Error', status_code=400)
            self.assertEqual(response[1], 400)
    
    def test_validate_request(self):
        """测试请求验证"""
        from apis.common.utils import validate_request
        
        # 有效请求
        is_valid, error = validate_request({'name': 'test'}, ['name'])
        self.assertTrue(is_valid)
        
        # 缺少字段
        is_valid, error = validate_request({}, ['name'])
        self.assertFalse(is_valid)
    
    def test_parse_json_field(self):
        """测试JSON字段解析"""
        from apis.common.utils import parse_json_field
        
        # 有效JSON
        result = parse_json_field('{"key": "value"}')
        self.assertEqual(result, {'key': 'value'})
        
        # 空值
        result = parse_json_field(None, default={})
        self.assertEqual(result, {})
        
        # 无效JSON
        result = parse_json_field('invalid json', default={})
        self.assertEqual(result, {})


class TestAuthModule(unittest.TestCase):
    """测试认证模块"""
    
    def test_generate_token(self):
        """测试Token生成"""
        from apis.common.auth import generate_token
        
        token1 = generate_token()
        token2 = generate_token()
        
        self.assertIsNotNone(token1)
        self.assertIsNotNone(token2)
        self.assertNotEqual(token1, token2)
        self.assertEqual(len(token1), 64)  # 32字节hex = 64字符
    
    def test_hash_password(self):
        """测试密码哈希"""
        from apis.common.auth import hash_password
        
        pwd_hash = hash_password('test123')
        self.assertIsNotNone(pwd_hash)
        self.assertEqual(len(pwd_hash), 64)
        
        # 相同密码产生相同哈希
        self.assertEqual(hash_password('test123'), pwd_hash)
    
    def test_verify_password(self):
        """测试密码验证"""
        from apis.common.auth import hash_password, verify_password
        
        pwd_hash = hash_password('test123')
        self.assertTrue(verify_password('test123', pwd_hash))
        self.assertFalse(verify_password('wrong', pwd_hash))
    
    def test_create_and_verify_token(self):
        """测试Token创建和验证"""
        from apis.common.auth import create_token, verify_token
        
        token = create_token('test_user')
        user_id = verify_token(token)
        
        self.assertEqual(user_id, 'test_user')
    
    def test_verify_invalid_token(self):
        """测试无效Token验证"""
        from apis.common.auth import verify_token
        
        result = verify_token('invalid_token')
        self.assertIsNone(result)


class TestBackupModule(unittest.TestCase):
    """测试备份模块"""
    
    def test_backup_config(self):
        """测试备份配置"""
        from apis.common.backup import get_backup_config, update_backup_config
        
        config = get_backup_config()
        self.assertIn('enabled', config)
        self.assertIn('interval_hours', config)
        
        # 更新配置
        new_config = update_backup_config(interval_hours=12)
        self.assertEqual(new_config['interval_hours'], 12)


class TestLoggerModule(unittest.TestCase):
    """测试日志模块"""
    
    def test_logger_exists(self):
        """测试日志记录器创建"""
        from apis.common.logger import get_logger
        
        logger = get_logger('test')
        self.assertIsNotNone(logger)
    
    def test_logger_output(self):
        """测试日志输出"""
        import io
        import logging
        from apis.common.logger import setup_logger
        
        # 创建一个带内存处理的logger
        logger = logging.getLogger('test_output')
        logger.setLevel(logging.INFO)
        
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        
        logger.info('Test log message')
        
        output = stream.getvalue()
        self.assertIn('Test log message', output)


if __name__ == '__main__':
    unittest.main()
