"""
数据库连接模块 - 统一的数据库连接管理
"""

import sqlite3
import os
import sys

# 获取项目根目录（backend目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# 数据库配置 - 使用绝对路径
DATABASE_PATH = os.path.join(backend_root, 'assets', 'data', 'interview_system.db')

def get_db_connection():
    """
    获取数据库连接
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"数据库文件不存在: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 启用字典工厂
    return conn

def execute_query(sql, params=None, fetch_one=False, fetch_all=True):
    """
    执行数据库查询
    
    Args:
        sql (str): SQL语句
        params (tuple): 参数
        fetch_one (bool): 是否只获取一条记录
        fetch_all (bool): 是否获取所有记录
        
    Returns:
        查询结果
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(sql, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor
            
        return result
    finally:
        conn.close()

def execute_update(sql, params=None, commit=True):
    """
    执行数据库更新操作
    
    Args:
        sql (str): SQL语句
        params (tuple): 参数
        commit (bool): 是否提交事务
        
    Returns:
        tuple: (lastrowid, rowcount)
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(sql, params or ())
        
        if commit:
            conn.commit()
            
        return cursor.lastrowid, cursor.rowcount
    finally:
        conn.close()

def execute_transaction(operations):
    """
    执行事务操作
    
    Args:
        operations (list): 操作列表，每个操作是(sql, params)元组
        
    Returns:
        bool: 是否成功
    """
    conn = get_db_connection()
    try:
        for sql, params in operations:
            conn.execute(sql, params or ())
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
