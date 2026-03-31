"""
API 测试 - 测试Flask API端点
"""
import os
import sys
import unittest
import tempfile
import sqlite3
import json

# 添加项目路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 测试数据库
TEST_DB = os.path.join(tempfile.gettempdir(), 'test_api.db')


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
    
    # 题目表
    cursor.execute('''
        CREATE TABLE translation_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_index INTEGER UNIQUE NOT NULL,
            question_data TEXT,
            is_used BOOLEAN DEFAULT 0
        )
    ''')
    
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


class TestFlaskApp(unittest.TestCase):
    """测试Flask应用"""
    
    @classmethod
    def setUpClass(cls):
        """创建Flask测试客户端"""
        # 临时修改数据库配置
        import config
        config.Config.DATABASE = TEST_DB
        
        from app import app
        cls.app = app
        cls.client = app.test_client()
    
    def test_app_created(self):
        """测试应用创建"""
        self.assertIsNotNone(self.app)
    
    def test_test_route(self):
        """测试路由"""
        response = self.client.get('/exam-api/test')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])


class TestAuthAPI(unittest.TestCase):
    """测试认证API"""
    
    @classmethod
    def setUpClass(cls):
        """创建Flask测试客户端"""
        import config
        config.Config.DATABASE = TEST_DB
        
        from app import app
        cls.app = app
        cls.client = app.test_client()
    
    def test_login_success(self):
        """测试登录成功"""
        response = self.client.post('/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])
    
    def test_login_failure(self):
        """测试登录失败"""
        response = self.client.post('/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'wrong'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_logout_without_auth(self):
        """测试未授权登出"""
        response = self.client.post('/auth/logout')
        self.assertEqual(response.status_code, 401)
    
    def test_verify_without_auth(self):
        """测试未授权验证"""
        response = self.client.get('/auth/verify')
        self.assertEqual(response.status_code, 401)


class TestProtectedAPI(unittest.TestCase):
    """测试受保护的API"""
    
    @classmethod
    def setUpClass(cls):
        """创建Flask测试客户端并获取Token"""
        import config
        config.Config.DATABASE = TEST_DB
        
        from app import app
        cls.app = app
        cls.client = app.test_client()
        
        # 获取Token
        response = cls.client.post('/auth/login',
            data=json.dumps({'username': 'admin', 'password': 'admin123'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        cls.token = data['data']['token']
    
    def test_access_with_token(self):
        """测试带Token访问"""
        response = self.client.get('/auth/verify',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()
