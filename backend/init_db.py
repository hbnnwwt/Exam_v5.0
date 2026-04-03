#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""
import os
import sys
import sqlite3

# 默认考试步骤
DEFAULT_EXAM_STEPS = [
    (1, '中文自我介绍', '', 60, 'introduction'),
    (2, '英文自我介绍', '进行简短的英文自我介绍', 60, 'introduction'),
    (3, '英文翻译', '阅读并翻译一段英文材料', 240, 'translation'),
    (4, '专业问题', '回答专业相关问题', 300, 'professional'),
    (5, '综合问答', '考官将针对考生的个人陈述、研究计划、专业能力等方面进行提问。\n⏰本环节无时间限制，由考官自由掌握时间', 540, 'introduction'),
    (6, '考试结束', '面试结束', 0, 'completion'),
]

def init_database():
    # 确保目录存在
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'data')
    os.makedirs(db_dir, exist_ok=True)

    db_path = os.path.join(db_dir, 'interview_system.db')

    conn = sqlite3.connect(db_path)

    # 创建所有表
    conn.execute('CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, attribute TEXT UNIQUE, value TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS exam_steps (id INTEGER PRIMARY KEY AUTOINCREMENT, step_number INTEGER NOT NULL UNIQUE, title TEXT NOT NULL, description TEXT NOT NULL, duration INTEGER NOT NULL, step_type TEXT NOT NULL, is_active BOOLEAN DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS step_contents (id INTEGER PRIMARY KEY AUTOINCREMENT, step_id INTEGER NOT NULL, content TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, student_number TEXT UNIQUE, name TEXT NOT NULL, current_step INTEGER DEFAULT 1, exam_status TEXT DEFAULT "ready", step_data TEXT, start_time TEXT, end_time TEXT, total_duration INTEGER, translation_question_id INTEGER, professional_question_id INTEGER, translation_question TEXT, professional_question TEXT, professional_subject TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS exam_records (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, student_number TEXT, current_step INTEGER DEFAULT 1, current_step_remaining_time INTEGER DEFAULT 0, translation_question_id INTEGER, professional_question_id INTEGER, used_question_ids TEXT, exam_status TEXT DEFAULT "pending", created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, exam_date TEXT, total_score REAL, status TEXT DEFAULT "pending")')
    conn.execute('CREATE TABLE IF NOT EXISTS translation_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question_index INTEGER, question_data TEXT, difficulty TEXT DEFAULT "medium", is_used BOOLEAN DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS professional_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, question_index INTEGER, question_data TEXT, difficulty TEXT DEFAULT "medium", subject TEXT, is_used BOOLEAN DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE, name TEXT NOT NULL, description TEXT, is_active BOOLEAN DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS operation_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, operation_type TEXT, operator TEXT, operation_details TEXT, ip_address TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS api_keys (id TEXT PRIMARY KEY, api_key TEXT, base_url TEXT, default_model TEXT, is_default INTEGER DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')

    # 插入默认考试步骤（如果不存在）
    for step in DEFAULT_EXAM_STEPS:
        conn.execute('''
            INSERT OR IGNORE INTO exam_steps
            (step_number, title, description, duration, step_type)
            VALUES (?, ?, ?, ?, ?)
        ''', step)

    # 插入默认系统设置
    DEFAULT_SETTINGS = [
        ('header_title', '北京石油化工学院研究生复试'),
        ('footer_copyright', '版权所有 © 2026 北京石油化工学院'),
    ]
    for attr, value in DEFAULT_SETTINGS:
        conn.execute('''
            INSERT OR IGNORE INTO settings (attribute, value)
            VALUES (?, ?)
        ''', (attr, value))

    conn.commit()
    conn.close()

    print(f'Database initialized: {db_path}')
    return True

if __name__ == '__main__':
    init_database()
