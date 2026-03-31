"""
题目管理模块 - 处理考试系统的题目获取、随机抽取等操作
"""

from flask import request
import random
from ..common.database import get_db_connection
from ..common.utils import format_response, format_question_data
from . import exam_bp

@exam_bp.route('/questions/<question_type>', methods=['GET'])
def get_questions(question_type):
    """获取题目列表"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()

        if question_type == 'translation':
            # 获取翻译题 - 直接从题目表检查 is_used 字段
            cursor = conn.execute('''
                SELECT id, question_index, question_data, is_used
                FROM translation_questions
                ORDER BY question_index
            ''')
            questions = cursor.fetchall()

        elif question_type == 'professional':
            # 获取专业题 - 直接从题目表检查 is_used 字段
            subject_filter = request.args.get('subject')

            sql = '''
                SELECT id, question_index, question_data, difficulty, subject, is_used
                FROM professional_questions
                WHERE 1=1
            '''
            params = []

            if subject_filter:
                sql += ' AND subject = ?'
                params.append(subject_filter)

            sql += ' ORDER BY question_index'

            cursor = conn.execute(sql, params)
            questions = cursor.fetchall()

        conn.close()

        # 格式化题目数据
        result = []
        for q in questions:
            try:
                # format_question_data 已经正确处理了 is_used 字段
                question_item = format_question_data(q, question_type)
                result.append(question_item)
            except Exception:
                continue

        return format_response(
            success=True,
            data=result,
            message=f"获取了 {len(result)} 道{question_type}题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取题目列表失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/<question_type>/<int:question_index>', methods=['GET'])
def get_question_by_index(question_type, question_index):
    """根据编号获取题目"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        
        if question_type == 'translation':
            cursor = conn.execute('''
                SELECT id, question_index, question_data 
                FROM translation_questions 
                WHERE question_index = ?
            ''', (question_index,))
        elif question_type == 'professional':
            cursor = conn.execute('''
                SELECT id, question_index, question_data, difficulty, subject 
                FROM professional_questions 
                WHERE question_index = ?
            ''', (question_index,))
            
        question = cursor.fetchone()
        conn.close()
        
        if not question:
            return format_response(
                success=False,
                error='题目不存在',
                status_code=404
            )
            
        try:
            result = format_question_data(question, question_type)
            
            return format_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            return format_response(
                success=False,
                error='题目数据格式错误',
                status_code=500
            )
            
    except Exception as e:
        return format_response(
            success=False,
            error=f"获取题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/<question_type>/id/<int:question_id>', methods=['GET'])
def get_question_by_id(question_type, question_id):
    """根据ID获取题目"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        
        if question_type == 'translation':
            cursor = conn.execute('''
                SELECT id, question_index, question_data 
                FROM translation_questions 
                WHERE id = ?
            ''', (question_id,))
        elif question_type == 'professional':
            cursor = conn.execute('''
                SELECT id, question_index, question_data, difficulty, subject 
                FROM professional_questions 
                WHERE id = ?
            ''', (question_id,))
            
        question = cursor.fetchone()
        conn.close()
        
        if not question:
            return format_response(
                success=False,
                error='题目不存在',
                status_code=404
            )
            
        try:
            result = format_question_data(question, question_type)
            
            return format_response(
                success=True,
                data=result
            )
            
        except Exception as e:
            return format_response(
                success=False,
                error='题目数据格式错误',
                status_code=500
            )
            
    except Exception as e:
        return format_response(
            success=False,
            error=f"获取题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/<question_type>/random', methods=['GET'])
def get_random_question(question_type):
    """随机获取题目"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        
        # 直接从题目表中查询未使用的题目
        if question_type == 'translation':
            subject_filter = request.args.get('subject')
            
            # 获取可用（未使用）的题目
            sql = '''
                SELECT id, question_index, question_data 
                FROM translation_questions 
                WHERE is_used = 0
            '''
            params = []
            sql += ' ORDER BY question_index'
            cursor = conn.execute(sql, params)
            
        elif question_type == 'professional':
            subject_filter = request.args.get('subject')

            # 获取可用（未使用）的题目
            sql = '''
                SELECT id, question_index, question_data, difficulty, subject 
                FROM professional_questions 
                WHERE is_used = 0
            '''
            params = []
            
            if subject_filter:
                sql += ' AND subject = ?'
                params.append(subject_filter)
                
            sql += ' ORDER BY question_index'
            cursor = conn.execute(sql, params)
            
        all_questions = cursor.fetchall()
        
        if not all_questions:
            conn.close()
            return format_response(
                success=False,
                error='没有可用的题目（已全部使用）',
                status_code=404
            )
            
        # 随机选择一个题目
        selected_question = random.choice(all_questions)
        
        # 将选中的题目标记为已使用
        table_name = f"{question_type}_questions"
        cursor = conn.execute(f'''
            UPDATE {table_name}
            SET is_used = 1
            WHERE id = ?
        ''', (selected_question['id'],))
        conn.commit()
        conn.close()
        
        try:
            result = format_question_data(selected_question, question_type)
            result['isUsed'] = True
            
            return format_response(
                success=True,
                data=result,
                message=f"随机抽取了1道{question_type}题目"
            )
            
        except Exception as e:
            return format_response(
                success=False,
                error='题目数据格式错误',
                status_code=500
            )
            
    except Exception as e:
        return format_response(
            success=False,
            error=f"随机获取题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/<question_type>/used', methods=['GET'])
def get_used_questions(question_type):
    """获取已使用的题目"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()
        
        if question_type == 'translation':
            cursor = conn.execute('''
                SELECT DISTINCT translation_question
                FROM exam_records
                WHERE translation_question IS NOT NULL
                AND translation_question != ''
            ''')
        elif question_type == 'professional':
            cursor = conn.execute('''
                SELECT DISTINCT professional_question
                FROM exam_records
                WHERE professional_question IS NOT NULL
                AND professional_question != ''
            ''')

        used_questions_raw = cursor.fetchall()
        conn.close()

        # 处理结果，提取题目编号
        used_questions = []
        for row in used_questions_raw:
            question_data = row[0]
            if question_data:
                try:
                    # 解析题目数据，提取编号
                    if question_data.startswith(f'{question_type}_'):
                        question_index = int(question_data.split('_')[1])
                        used_questions.append(question_index)
                except (ValueError, IndexError):
                    continue

        return format_response(
            success=True,
            data=used_questions,
            message=f"获取了 {len(used_questions)} 道已使用的{question_type}题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取已使用题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/<question_type>/available', methods=['GET'])
def get_available_questions(question_type):
    """获取可用题目列表（未使用的）"""
    try:
        if question_type not in ['translation', 'professional']:
            return format_response(
                success=False,
                error='无效的题目类型',
                status_code=400
            )

        conn = get_db_connection()

        # 获取已使用的题目ID
        used_ids = set()
        if question_type == 'translation':
            cursor = conn.execute('''
                SELECT translation_question_id FROM students
                WHERE translation_question_id IS NOT NULL
            ''')
            used_ids = {row[0] for row in cursor.fetchall() if row[0]}
        elif question_type == 'professional':
            cursor = conn.execute('''
                SELECT professional_question_id FROM students
                WHERE professional_question_id IS NOT NULL
            ''')
            used_ids = {row[0] for row in cursor.fetchall() if row[0]}

        # 获取所有题目并过滤
        if question_type == 'translation':
            cursor = conn.execute('''
                SELECT id, question_index, question_data
                FROM translation_questions
                ORDER BY question_index
            ''')
        else:
            cursor = conn.execute('''
                SELECT id, question_index, question_data, difficulty, subject
                FROM professional_questions
                ORDER BY question_index
            ''')

        all_questions = cursor.fetchall()
        conn.close()

        # 过滤出可用题目
        available = []
        for q in all_questions:
            if q['id'] not in used_ids:
                available.append({
                    'id': q['id'],
                    'questionIndex': q['question_index'],
                    'questionData': q['question_data']
                })
                if question_type == 'professional':
                    available[-1]['difficulty'] = q['difficulty']
                    available[-1]['subject'] = q['subject']

        return format_response(
            success=True,
            data=available,
            message=f"获取了 {len(available)} 道可用题目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取可用题目失败: {str(e)}",
            status_code=500
        )

@exam_bp.route('/questions/subjects', methods=['GET'])
def get_subjects():
    """获取专业课科目列表"""
    try:
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT DISTINCT subject 
            FROM professional_questions 
            WHERE subject IS NOT NULL
            ORDER BY subject
        ''')
        subjects = [row[0] for row in cursor.fetchall()]
        conn.close()

        # 科目映射
        subject_mapping = {
            'computer_science': '计算机科学',
            'data_structure': '数据结构',
            'ai_introduction': '人工智能导论',
            'accounting': '会计学'
        }

        result = []
        for subject in subjects:
            result.append({
                'value': subject,
                'label': subject_mapping.get(subject, subject),
                'count': 0  # 可以后续添加统计
            })

        return format_response(
            success=True,
            data=result,
            message=f"获取了 {len(result)} 个科目"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取科目列表失败: {str(e)}",
            status_code=500
        )
