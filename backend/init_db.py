#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""
import os
import sys
import sqlite3

def init_database():
    # 确保目录存在
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'data')
    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(db_dir, 'interview_system.db')

    conn = sqlite3.connect(db_path)

    # 创建所有表
    conn.execute('CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, attribute TEXT UNIQUE, value TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS exam_steps (id INTEGER PRIMARY KEY AUTOINCREMENT, step_number INTEGER NOT NULL UNIQUE, title TEXT NOT NULL, description TEXT NOT NULL, duration INTEGER NOT NULL, step_type TEXT NOT NULL, is_active BOOLEAN DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS step_contents (id INTEGER PRIMARY KEY AUTOINCREMENT, step_id INTEGER NOT NULL, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, student_number TEXT UNIQUE, name TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS exam_records (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, exam_date TEXT, total_score REAL, status TEXT DEFAULT "pending", created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS translation_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, difficulty TEXT DEFAULT "medium", created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS professional_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER, content TEXT NOT NULL, difficulty TEXT DEFAULT "medium", created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')

    conn.commit()
    conn.close()

    print(f'Database initialized: {db_path}')
    return True

if __name__ == '__main__':
    init_database()
