"""
考试导出API模块
提供考试数据导出功能
"""

import logging
from flask import Blueprint, jsonify, request, make_response
from datetime import datetime
import json
import csv
import io
import sys
import os

logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apis.common.database import get_db_connection
from apis.common.utils import format_response

export_bp = Blueprint('export', __name__)

def get_subject_map():
    """从数据库动态获取科目映射"""
    subject_map = {}
    try:
        conn = get_db_connection()
        cursor = conn.execute('SELECT code, name FROM subjects')
        for row in cursor.fetchall():
            subject_map[row['code']] = row['name']
        conn.close()
    except Exception as e:
        logger.warning(f"获取科目映射失败: {e}")
    return subject_map

def get_image_source(item_content, prefer_thumbnail=False):
    if isinstance(item_content, dict):
        if prefer_thumbnail:
            thumb = item_content.get('thumb')
            if isinstance(thumb, str) and thumb:
                return thumb
        src = item_content.get('src')
        if isinstance(src, str) and src:
            return src
        thumb = item_content.get('thumb')
        if isinstance(thumb, str) and thumb:
            return thumb
        return ''
    if isinstance(item_content, str):
        return item_content
    return ''

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def format_question_content_for_html(content):
    """格式化题目内容为HTML格式"""
    if not content:
        return '暂无内容'

    html_content = ''
    question_data = None

    # 检查数据格式并转换
    if isinstance(content, str):
        # 如果是逗号分隔的字符串格式，转换为数组
        if ',' in content and not content.startswith('['):
            parts = content.split(',')
            question_data = []

            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    question_data.append([parts[i].strip(), parts[i + 1].strip()])
        else:
            # 尝试作为JSON解析
            try:
                question_data = json.loads(content)
            except:
                # JSON解析失败，当作纯文本处理
                question_data = [["txt", content]]
    elif isinstance(content, list):
        # 如果已经是数组格式
        question_data = content
    else:
        question_data = content

    # 处理 {"content": [...]} 格式
    if isinstance(question_data, list) and len(question_data) > 0:
        if isinstance(question_data[0], dict) and 'content' in question_data[0]:
            question_data = question_data[0]['content']

    if isinstance(question_data, list) and len(question_data) > 0:
        # 处理多内容格式
        for index, item in enumerate(question_data):
            if isinstance(item, list) and len(item) >= 2:
                item_type = item[0]
                item_content = item[1]

                if item_type == 'txt':
                    # 文本内容
                    html_content += f'<div class="question-text-part">{item_content}</div>'
                elif item_type == 'img':
                    # 图片内容
                    image_path = get_image_source(item_content)
                    if image_path.startswith('data:image/'):
                        # Base64图片数据 - 直接使用
                        html_content += f'''<div class="question-image-part">
                            <img src="{image_path}" alt="题目图片 {index + 1}" style="max-width: 100%; height: auto; border-radius: 4px;">
                        </div>'''
                    else:
                        # 图片文件路径 - 尝试读取并转换为Base64
                        img_src = ''
                        file_to_check = None

                        if image_path.startswith('/uploads/'):
                            file_to_check = 'static' + image_path
                        elif image_path.startswith('static/uploads/'):
                            file_to_check = image_path
                        elif image_path.startswith('assets/'):
                            file_to_check = image_path
                        elif not image_path.startswith('./') and not image_path.startswith('http'):
                            file_to_check = 'assets/' + image_path
                        else:
                            file_to_check = image_path.lstrip('./')

                        # 尝试读取文件
                        if file_to_check and os.path.exists(file_to_check):
                            try:
                                import base64
                                with open(file_to_check, 'rb') as f:
                                    img_data = base64.b64encode(f.read()).decode()
                                    # 根据文件扩展名确定MIME类型
                                    ext = os.path.splitext(file_to_check)[1].lower()
                                    mime_type = 'image/png'
                                    if ext in ['.jpg', '.jpeg']:
                                        mime_type = 'image/jpeg'
                                    elif ext == '.gif':
                                        mime_type = 'image/gif'
                                    elif ext == '.webp':
                                        mime_type = 'image/webp'
                                    img_src = f'data:{mime_type};base64,{img_data}'
                            except Exception as e:
                                logger.warning(f'读取图片文件失败: {file_to_check}, 错误: {e}')

                        if img_src:
                            html_content += f'''<div class="question-image-part">
                                <img src="{img_src}" alt="题目图片 {index + 1}" style="max-width: 100%; height: auto; border-radius: 4px;">
                            </div>'''
                        else:
                            # 文件不存在，显示占位符
                            html_content += f'''<div class="question-image-part">
                                <div style="padding: 20px; background: #f8d9da; border: 1px solid #f5c6cb; text-align: center; color: #721c24;">
                                    图片文件不存在: {image_path}
                                </div>
                            </div>'''
            elif isinstance(item, str):
                html_content += f'<div class="question-text-part">{item}</div>'
    elif isinstance(question_data, str):
        html_content = f'<div class="question-text-part">{question_data}</div>'
    elif question_data and hasattr(question_data, 'get') and question_data.get('content'):
        html_content = f'<div class="question-text-part">{question_data["content"]}</div>'

    return html_content or str(content)

def generate_subject_stats_html(students):
    """生成专业科目统计的HTML"""
    # 统计不同专业科目的学生数
    subject_counts = {}
    subject_map = get_subject_map()

    for student in students:
        if student.get('professionalSubject'):
            subject = student['professionalSubject']
            subject_counts[subject] = subject_counts.get(subject, 0) + 1

    if not subject_counts:
        return '<p>暂无专业科目数据</p>'

    stats_html = '<div class="subject-grid">'
    for subject, count in subject_counts.items():
        stats_html += f'''
            <div class="subject-item">
                <span class="subject-name">{subject}</span>
                <span class="subject-count">{count}人</span>
            </div>
        '''
    stats_html += '</div>'

    return stats_html

def format_question_content_for_pdf(content):
    """格式化题目内容为PDF格式，处理图片为base64"""
    if not content:
        return '暂无内容'

    import base64
    import os

    html_content = ''
    question_data = None

    # 检查数据格式并转换
    if isinstance(content, str):
        # 如果是逗号分隔的字符串格式，转换为数组
        if ',' in content and not content.startswith('['):
            parts = content.split(',')
            question_data = []

            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    question_data.append([parts[i].strip(), parts[i + 1].strip()])
        else:
            # 尝试作为JSON解析
            try:
                question_data = json.loads(content)
            except:
                # JSON解析失败，当作纯文本处理
                question_data = [["txt", content]]
    elif isinstance(content, list):
        # 如果已经是数组格式
        question_data = content
    else:
        question_data = content

    if isinstance(question_data, list) and len(question_data) > 0:
        # 处理多内容格式
        for index, item in enumerate(question_data):
            if isinstance(item, list) and len(item) >= 2:
                item_type = item[0]
                item_content = item[1]

                if item_type == 'txt':
                    # 文本内容
                    html_content += f'<div class="question-text-part">{item_content}</div>'
                elif item_type == 'img':
                    # 图片内容
                    image_path = get_image_source(item_content)
                    if image_path.startswith('data:image/'):
                        # Base64图片数据，直接使用
                        html_content += f'''<div class="question-image-part">
                            <img src="{image_path}" alt="题目图片 {index + 1}" style="max-width: 100%; height: auto; border-radius: 4px;">
                        </div>'''
                    else:
                        # 图片路径，尝试转换为base64
                        try:
                            # 构建完整的文件路径
                            if image_path.startswith('assets/images/'):
                                file_path = image_path
                            elif image_path.startswith('/assets/'):
                                file_path = image_path[1:]
                            elif not image_path.startswith('./') and not image_path.startswith('http'):
                                file_path = f'assets/images/{image_path}'
                            else:
                                file_path = image_path

                            # 读取图片文件并转换为base64
                            if os.path.exists(file_path):
                                with open(file_path, 'rb') as img_file:
                                    img_data = img_file.read()
                                    img_base64 = base64.b64encode(img_data).decode('utf-8')

                                    # 根据文件扩展名确定MIME类型
                                    if file_path.lower().endswith('.png'):
                                        mime_type = 'image/png'
                                    elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                                        mime_type = 'image/jpeg'
                                    elif file_path.lower().endswith('.gif'):
                                        mime_type = 'image/gif'
                                    else:
                                        mime_type = 'image/png'  # 默认

                                    data_url = f'data:{mime_type};base64,{img_base64}'
                                    html_content += f'''<div class="question-image-part">
                                        <img src="{data_url}" alt="题目图片 {index + 1}" style="max-width: 100%; height: auto; border-radius: 4px;">
                                    </div>'''
                            else:
                                # 文件不存在，显示占位符
                                html_content += f'''<div class="question-image-part">
                                    <div style="padding: 20px; background: #f8f9fa; border: 1px dashed #ccc; text-align: center; color: #666;">
                                        图片文件不存在: {file_path}
                                    </div>
                                </div>'''
                        except Exception as e:
                            # 处理图片失败，显示错误信息
                            html_content += f'''<div class="question-image-part">
                                <div style="padding: 20px; background: #f8d7da; border: 1px solid #f5c6cb; text-align: center; color: #721c24;">
                                    图片处理失败: {str(e)}
                                </div>
                            </div>'''
            elif isinstance(item, str):
                html_content += f'<div class="question-text-part">{item}</div>'
    elif isinstance(question_data, str):
        html_content = f'<div class="question-text-part">{question_data}</div>'
    elif question_data and hasattr(question_data, 'get') and question_data.get('content'):
        html_content = f'<div class="question-text-part">{question_data["content"]}</div>'

    return html_content or str(content)

def format_question_content_for_pdf_text(content):
    """格式化题目内容为PDF纯文本格式"""
    if not content:
        return '暂无内容'

    text_content = ''
    question_data = None

    # 检查数据格式并转换
    if isinstance(content, str):
        # 如果是逗号分隔的字符串格式，转换为数组
        if ',' in content and not content.startswith('['):
            parts = content.split(',')
            question_data = []

            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    question_data.append([parts[i].strip(), parts[i + 1].strip()])
        else:
            # 尝试作为JSON解析
            try:
                question_data = json.loads(content)
            except:
                # JSON解析失败，当作纯文本处理
                question_data = [["txt", content]]
    elif isinstance(content, list):
        # 如果已经是数组格式
        question_data = content
    else:
        question_data = content

    # 处理 {"content": [...]} 格式
    if isinstance(question_data, list) and len(question_data) > 0:
        if isinstance(question_data[0], dict) and 'content' in question_data[0]:
            question_data = question_data[0]['content']

    if isinstance(question_data, list) and len(question_data) > 0:
        # 处理多内容格式
        text_parts = []
        for index, item in enumerate(question_data):
            if isinstance(item, list) and len(item) >= 2:
                item_type = item[0]
                item_content = item[1]

                if item_type == 'txt':
                    # 文本内容
                    text_parts.append(item_content)
                elif item_type == 'img':
                    # 图片内容，显示为文本描述
                    image_path = get_image_source(item_content)
                    if image_path.startswith('data:image/'):
                        text_parts.append(f"[图片 {index + 1}: Base64编码图片]")
                    else:
                        text_parts.append(f"[图片 {index + 1}: {image_path}]")
            elif isinstance(item, str):
                text_parts.append(item)

        text_content = '\n'.join(text_parts)
    elif isinstance(question_data, str):
        text_content = question_data
    elif question_data and hasattr(question_data, 'get') and question_data.get('content'):
        text_content = question_data['content']

    return text_content or str(content)

def format_question_content_for_pdf_elements(content, normal_style, question_style=None):
    """格式化题目内容为PDF元素列表，包含文本和图片"""
    if not content:
        return [Paragraph('暂无内容', normal_style)]

    from reportlab.platypus import Paragraph, Image, Spacer
    from reportlab.lib.units import inch
    import base64
    import os
    import tempfile

    elements = []
    question_data = None

    # 检查数据格式并转换
    if isinstance(content, str):
        # 如果是逗号分隔的字符串格式，转换为数组
        if ',' in content and not content.startswith('['):
            parts = content.split(',')
            question_data = []

            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    question_data.append([parts[i].strip(), parts[i + 1].strip()])
        else:
            # 尝试作为JSON解析
            try:
                question_data = json.loads(content)
            except:
                # JSON解析失败，当作纯文本处理
                question_data = [["txt", content]]
    elif isinstance(content, list):
        # 如果已经是数组格式
        question_data = content
    else:
        question_data = content

    # 处理 {"content": [...]} 格式
    if isinstance(question_data, list) and len(question_data) > 0:
        if isinstance(question_data[0], dict) and 'content' in question_data[0]:
            question_data = question_data[0]['content']

    if isinstance(question_data, list) and len(question_data) > 0:
        # 处理多内容格式
        for index, item in enumerate(question_data):
            if isinstance(item, list) and len(item) >= 2:
                item_type = item[0]
                item_content = item[1]

                if item_type == 'txt':
                    # 文本内容
                    if item_content.strip():
                        text_style = question_style if question_style else normal_style
                        elements.append(Paragraph(item_content, text_style))
                        elements.append(Spacer(1, 6))

                elif item_type == 'img':
                    # 图片内容
                    try:
                        img_element = None
                        image_path = get_image_source(item_content)

                        if image_path.startswith('data:image/'):
                            # Base64图片数据
                            # 解析base64数据
                            header, data = image_path.split(',', 1)
                            img_data = base64.b64decode(data)

                            # 创建临时文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                                temp_file.write(img_data)
                                temp_path = temp_file.name

                            try:
                                img_element = Image(temp_path, width=4*inch, height=3*inch)
                                img_element.hAlign = 'CENTER'
                            except:
                                elements.append(Paragraph(f'[图片 {index + 1}: Base64编码图片 - 无法显示]', normal_style))
                            finally:
                                # 清理临时文件
                                try:
                                    os.unlink(temp_path)
                                except:
                                    pass
                        else:
                            # 图片路径
                            file_path = None
                            if image_path.startswith('/uploads/'):
                                # 处理 /uploads/xxx.png 格式
                                file_path = 'static' + image_path
                            elif image_path.startswith('static/uploads/'):
                                file_path = image_path
                            elif image_path.startswith('assets/images/'):
                                file_path = image_path
                            elif image_path.startswith('/assets/'):
                                file_path = image_path[1:]
                            elif not image_path.startswith('./') and not image_path.startswith('http'):
                                file_path = f'assets/images/{image_path}'
                            else:
                                file_path = image_path.replace('./', '')

                            # 读取图片文件
                            if file_path and os.path.exists(file_path):
                                try:
                                    img_element = Image(file_path)
                                    # 设置图片大小，保持比例
                                    img_width, img_height = img_element.imageWidth, img_element.imageHeight
                                    max_width = 4.5 * inch
                                    max_height = 3 * inch

                                    # 计算缩放比例
                                    width_ratio = max_width / img_width
                                    height_ratio = max_height / img_height
                                    scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大

                                    img_element.drawWidth = img_width * scale_ratio
                                    img_element.drawHeight = img_height * scale_ratio
                                    img_element.hAlign = 'CENTER'
                                except Exception as e:
                                    elements.append(Paragraph(f'[图片 {index + 1}: {file_path} - 加载失败: {str(e)}]', normal_style))
                            else:
                                elements.append(Paragraph(f'[图片 {index + 1}: {file_path} - 文件不存在]', normal_style))

                        if img_element:
                            elements.append(img_element)
                            elements.append(Spacer(1, 12))

                    except Exception as e:
                        elements.append(Paragraph(f'[图片 {index + 1}: 处理失败 - {str(e)}]', normal_style))
                        elements.append(Spacer(1, 6))

            elif isinstance(item, str):
                if item.strip():
                    elements.append(Paragraph(item, normal_style))
                    elements.append(Spacer(1, 6))

    elif isinstance(question_data, str):
        if question_data.strip():
            elements.append(Paragraph(question_data, normal_style))
    elif question_data and hasattr(question_data, 'get') and question_data.get('content'):
        if question_data['content'].strip():
            elements.append(Paragraph(question_data['content'], normal_style))

    # 如果没有任何元素，添加默认文本
    if not elements:
        elements.append(Paragraph('暂无内容', normal_style))

    return elements

@export_bp.route('/students', methods=['GET'])
def export_students():
    """导出所有学生的考试信息"""
    try:
        conn = get_db_connection()
        
        # 获取所有学生的详细信息
        cursor = conn.execute('''
            SELECT 
                s.student_number,
                s.name,
                s.current_step,
                s.exam_status,
                s.translation_question_id,
                s.professional_question_id,
                s.professional_subject,
                s.start_time,
                s.end_time,
                s.total_duration,
                s.created_at,
                er.exam_status as record_status,
                er.created_at as record_created_at
            FROM students s
            LEFT JOIN exam_records er ON s.student_number = er.student_number
            ORDER BY CAST(s.student_number AS INTEGER)
        ''')
        
        students = cursor.fetchall()
        
        # 获取翻译题目信息
        translation_questions = {}
        cursor = conn.execute('SELECT id, question_index FROM translation_questions')
        for row in cursor.fetchall():
            translation_questions[row['id']] = row['question_index']
        
        # 获取专业题目信息
        professional_questions = {}
        cursor = conn.execute('SELECT id, question_index, subject FROM professional_questions')
        for row in cursor.fetchall():
            professional_questions[row['id']] = {
                'question_index': row['question_index'],
                'subject': row['subject']
            }
        
        conn.close()
        
        # 构建导出数据
        export_data = []
        for student in students:
            # 获取翻译题目编号
            translation_question_number = None
            if student['translation_question_id']:
                translation_question_number = translation_questions.get(student['translation_question_id'])
            
            # 获取专业题目编号
            professional_question_number = None
            professional_question_subject = None
            if student['professional_question_id']:
                prof_info = professional_questions.get(student['professional_question_id'])
                if prof_info:
                    professional_question_number = prof_info['question_index']
                    professional_question_subject = prof_info['subject']
            
            # 计算考试时长（分钟）
            duration_minutes = None
            if student['total_duration']:
                duration_minutes = round(student['total_duration'] / 60, 1)
            
            # 格式化时间
            start_time_formatted = None
            end_time_formatted = None
            if student['start_time']:
                try:
                    start_dt = datetime.fromisoformat(student['start_time'])
                    start_time_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_time_formatted = student['start_time']
            
            if student['end_time']:
                try:
                    end_dt = datetime.fromisoformat(student['end_time'])
                    end_time_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    end_time_formatted = student['end_time']
            
            # 考试状态映射
            status_map = {
                'ready': '准备中',
                'in_progress': '进行中',
                'completed': '已完成',
                'paused': '暂停'
            }
            
            # 步骤名称映射
            step_map = {
                1: '中文自我介绍',
                2: '英文自我介绍',
                3: '英文翻译',
                4: '专业问题',
                5: '综合问答',
                6: '考试结束'
            }
            
            # 专业科目映射
            subject_map = get_subject_map()

            export_data.append({
                'studentNumber': student['student_number'],
                'name': student['name'] or '',
                'currentStep': step_map.get(student['current_step'], f'步骤{student["current_step"]}'),
                'examStatus': status_map.get(student['exam_status'], student['exam_status']),
                'translationQuestionNumber': translation_question_number,
                'professionalQuestionNumber': professional_question_number,
                'professionalSubject': subject_map.get(professional_question_subject, professional_question_subject) if professional_question_subject else None,
                'startTime': start_time_formatted,
                'endTime': end_time_formatted,
                'durationMinutes': duration_minutes,
                'createdAt': student['created_at'],
                'recordStatus': '已完成' if student['record_status'] == 'completed' else '未完成' if student['record_status'] in (0, 'ready') else '无记录'
            })
        
        return format_response(
            success=True,
            data=export_data,
            message=f"成功导出{len(export_data)}条学生记录"
        )
        
    except Exception as e:
        return format_response(
            success=False,
            error=f"导出学生数据失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/students/csv', methods=['GET'])
def export_students_csv():
    """导出学生数据为CSV文件"""
    try:
        response = export_students()
        response_obj = response[0] if isinstance(response, tuple) else response
        data = json.loads(response_obj.get_data(as_text=True))

        if not data['success']:
            return response_obj

        students = data['data']
        
        # 创建CSV内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = [
            '学生编号', '姓名', '当前步骤', '考试状态',
            '翻译题目编号', '专业题目编号', '专业科目',
            '开始时间', '结束时间', '考试时长(分钟)',
            '创建时间', '记录状态'
        ]
        writer.writerow(headers)
        
        # 写入数据
        for student in students:
            row = [
                student['studentNumber'],
                student['name'],
                student['currentStep'],
                student['examStatus'],
                student['translationQuestionNumber'] or '',
                student['professionalQuestionNumber'] or '',
                student['professionalSubject'] or '',
                student['startTime'] or '',
                student['endTime'] or '',
                student['durationMinutes'] or '',
                student['createdAt'] or '',
                student['recordStatus']
            ]
            writer.writerow(row)
        
        # 创建响应
        csv_content = output.getvalue()
        output.close()
        
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=exam_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return format_response(
            success=False,
            error=f"导出CSV文件失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/preview', methods=['GET'])
def export_preview():
    """获取导出预览数据"""
    try:
        conn = get_db_connection()

        # 获取所有学生的详细信息
        # 使用子查询获取每个学生最早考试记录的创建时间作为备用开始时间
        cursor = conn.execute('''
            SELECT
                s.student_number,
                s.name,
                s.current_step,
                s.exam_status,
                s.translation_question,
                s.translation_question_id,
                s.professional_question,
                s.professional_question_id,
                s.professional_subject,
                s.start_time,
                s.end_time,
                s.total_duration,
                s.created_at,
                (
                    SELECT exam_status FROM exam_records
                    WHERE student_number = s.student_number
                    ORDER BY created_at DESC LIMIT 1
                ) as record_status,
                (
                    SELECT created_at FROM exam_records
                    WHERE student_number = s.student_number
                    ORDER BY created_at ASC LIMIT 1
                ) as record_created_at
            FROM students s
            ORDER BY CAST(s.student_number AS INTEGER)
        ''')

        students = cursor.fetchall()

        # 获取翻译题目信息
        translation_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data FROM translation_questions')
        for row in cursor.fetchall():
            translation_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data']
            }

        # 获取专业题目信息
        professional_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data, subject FROM professional_questions')
        for row in cursor.fetchall():
            professional_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data'],
                'subject': row['subject']
            }

        conn.close()

        # 构建预览数据
        preview_data = []
        for student in students:
            # 获取翻译题目详情
            translation_info = None
            if student['translation_question_id']:
                trans_info = translation_questions.get(student['translation_question_id'])
                if trans_info:
                    translation_info = {
                        'questionNumber': trans_info['question_index'],
                        'questionContent': student['translation_question'] or trans_info['question_data']
                    }

            # 获取专业题目详情
            professional_info = None
            if student['professional_question_id']:
                prof_info = professional_questions.get(student['professional_question_id'])
                if prof_info:
                    # 科目映射
                    subject_map = get_subject_map()
                    subject_code = prof_info['subject']
                    professional_info = {
                        'questionNumber': prof_info['question_index'],
                        'questionContent': student['professional_question'] or prof_info['question_data'],
                        'subject': subject_map.get(subject_code, subject_code) if subject_code else None
                    }

            # 计算考试时长
            duration_minutes = None
            if student['total_duration']:
                duration_minutes = round(student['total_duration'] / 60, 1)

            # 格式化时间
            start_time_formatted = None
            end_time_formatted = None

            # 优先使用 students.start_time，如果没有则使用 exam_records 的创建时间作为备用
            effective_start_time = student['start_time'] or student['record_created_at']
            if effective_start_time:
                try:
                    start_dt = datetime.fromisoformat(effective_start_time)
                    start_time_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_time_formatted = effective_start_time

            if student['end_time']:
                try:
                    end_dt = datetime.fromisoformat(student['end_time'])
                    end_time_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    end_time_formatted = student['end_time']

            # 步骤名称映射
            step_map = {
                1: '中文自我介绍',
                2: '英文自我介绍',
                3: '英文翻译',
                4: '专业问题',
                5: '综合问答',
                6: '考试结束'
            }

            # 专业科目映射
            subject_map = get_subject_map()

            # 直接传递原始题目内容，让前端处理格式化
            # 不在后端进行格式化，保持原始数据结构

            preview_data.append({
                'studentNumber': student['student_number'],
                'name': student['name'] or '',
                'currentStep': step_map.get(student['current_step'], f'步骤{student["current_step"]}'),
                'examStatus': student['exam_status'],
                'translationInfo': translation_info,
                'professionalInfo': professional_info,
                'professionalSubject': subject_map.get(student['professional_subject'], student['professional_subject']) if student['professional_subject'] else None,
                'startTime': start_time_formatted,
                'endTime': end_time_formatted,
                'durationMinutes': duration_minutes,
                'createdAt': student['created_at'],
                'isCompleted': student['record_status'] == 'completed'
            })

        return format_response(
            success=True,
            data=preview_data,
            message=f"成功获取{len(preview_data)}条学生记录预览"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取预览数据失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/statistics', methods=['GET'])
def export_statistics():
    """导出考试统计信息"""
    try:
        conn = get_db_connection()

        # 基本统计
        cursor = conn.execute('SELECT COUNT(*) as total FROM students')
        total_students = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) as completed FROM exam_records WHERE exam_status = 'completed'")
        completed_exams = cursor.fetchone()[0]

        # 专业科目统计
        cursor = conn.execute('''
            SELECT professional_subject, COUNT(*) as count
            FROM students
            WHERE professional_subject IS NOT NULL AND professional_subject != ''
            GROUP BY professional_subject
            ORDER BY count DESC
        ''')
        subject_stats = cursor.fetchall()
        
        # 各步骤统计
        cursor = conn.execute('''
            SELECT current_step, COUNT(*) as count 
            FROM students 
            GROUP BY current_step 
            ORDER BY current_step
        ''')
        step_stats = cursor.fetchall()
        
        # 专业科目统计
        cursor = conn.execute('''
            SELECT professional_subject, COUNT(*) as count 
            FROM students 
            WHERE professional_subject IS NOT NULL AND professional_subject != ''
            GROUP BY professional_subject
        ''')
        subject_stats = cursor.fetchall()
        
        # 考试时长统计
        cursor = conn.execute('''
            SELECT 
                AVG(total_duration) as avg_duration,
                MIN(total_duration) as min_duration,
                MAX(total_duration) as max_duration
            FROM students 
            WHERE total_duration IS NOT NULL AND total_duration > 0
        ''')
        duration_stats = cursor.fetchone()
        
        conn.close()
        
        # 构建统计数据
        statistics = {
            'summary': {
                'totalStudents': total_students,
                'completedExams': completed_exams,
                'subjectStats': [
                    {
                        'subject': row['professional_subject'],
                        'subjectName': get_subject_map().get(row['professional_subject'], row['professional_subject']),
                        'count': row['count']
                    }
                    for row in subject_stats
                ]
            },
            'stepDistribution': [
                {
                    'step': row['current_step'],
                    'stepName': {
                        1: '中文自我介绍',
                        2: '英文自我介绍', 
                        3: '英文翻译',
                        4: '专业问题',
                        5: '综合问答',
                        6: '考试结束'
                    }.get(row['current_step'], f'步骤{row["current_step"]}'),
                    'count': row['count']
                }
                for row in step_stats
            ],
            'durationStats': {
                'averageMinutes': round(duration_stats['avg_duration'] / 60, 1) if duration_stats['avg_duration'] else 0,
                'minMinutes': round(duration_stats['min_duration'] / 60, 1) if duration_stats['min_duration'] else 0,
                'maxMinutes': round(duration_stats['max_duration'] / 60, 1) if duration_stats['max_duration'] else 0
            },
            'exportTime': datetime.now().isoformat()
        }
        
        return format_response(
            success=True,
            data=statistics,
            message="统计信息导出成功"
        )
        
    except Exception as e:
        return format_response(
            success=False,
            error=f"导出统计信息失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/bundle', methods=['GET'])
def export_bundle():
    try:
        conn = get_db_connection()

        students_cursor = conn.execute('''
            SELECT
                s.id,
                s.student_number,
                s.name,
                s.current_step,
                s.exam_status,
                s.translation_question,
                s.translation_question_id,
                s.professional_question,
                s.professional_question_id,
                s.professional_subject,
                s.start_time,
                s.end_time,
                s.total_duration,
                s.created_at,
                er.exam_status as record_status,
                er.created_at as record_created_at
            FROM students s
            LEFT JOIN exam_records er ON s.student_number = er.student_number
            ORDER BY CAST(s.student_number AS INTEGER)
        ''')
        students = [row_to_dict(row) for row in students_cursor.fetchall()]

        translation_cursor = conn.execute('''
            SELECT id, question_index, question_data, created_at
            FROM translation_questions
            ORDER BY question_index
        ''')
        translation_questions = [row_to_dict(row) for row in translation_cursor.fetchall()]

        professional_cursor = conn.execute('''
            SELECT id, question_index, question_data, difficulty, subject, created_at
            FROM professional_questions
            ORDER BY subject, question_index
        ''')
        professional_questions = [row_to_dict(row) for row in professional_cursor.fetchall()]

        subjects_cursor = conn.execute('''
            SELECT id, code, name, description, is_active, created_at
            FROM subjects
            ORDER BY code
        ''')
        subjects = [row_to_dict(row) for row in subjects_cursor.fetchall()]

        records_cursor = conn.execute('''
            SELECT id, student_number, exam_status, created_at
            FROM exam_records
            ORDER BY created_at DESC
        ''')
        exam_records = [row_to_dict(row) for row in records_cursor.fetchall()]

        conn.close()

        completed_exams = len([row for row in exam_records if row and row.get('exam_status') == 'completed'])

        return format_response(
            success=True,
            data={
                'exportTime': datetime.now().isoformat(),
                'summary': {
                    'totalStudents': len(students),
                    'completedExams': completed_exams,
                    'translationQuestions': len(translation_questions),
                    'professionalQuestions': len(professional_questions),
                    'subjects': len(subjects),
                    'examRecords': len(exam_records)
                },
                'students': students,
                'translationQuestions': translation_questions,
                'professionalQuestions': professional_questions,
                'subjects': subjects,
                'examRecords': exam_records
            },
            message='完整数据导出成功'
        )
    except Exception as e:
        return format_response(
            success=False,
            error=f"导出完整数据失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/html', methods=['GET'])
def export_html():
    """导出HTML格式的考试记录"""
    try:
        # 直接获取预览数据，不通过API调用
        conn = get_db_connection()

        # 获取所有学生的详细信息
        cursor = conn.execute('''
            SELECT
                s.student_number,
                s.name,
                s.current_step,
                s.exam_status,
                s.translation_question,
                s.translation_question_id,
                s.professional_question,
                s.professional_question_id,
                s.professional_subject,
                s.start_time,
                s.end_time,
                s.total_duration,
                s.created_at,
                er.exam_status as record_status,
                er.created_at as record_created_at
            FROM students s
            LEFT JOIN exam_records er ON s.student_number = er.student_number
            ORDER BY CAST(s.student_number AS INTEGER)
        ''')

        students_raw = cursor.fetchall()

        # 获取翻译题目信息
        translation_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data FROM translation_questions')
        for row in cursor.fetchall():
            translation_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data']
            }

        # 获取专业题目信息
        professional_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data, subject FROM professional_questions')
        for row in cursor.fetchall():
            professional_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data'],
                'subject': row['subject']
            }

        conn.close()

        # 构建学生数据
        students = []
        for student in students_raw:
            # 获取翻译题目详情
            translation_info = None
            if student['translation_question_id']:
                trans_info = translation_questions.get(student['translation_question_id'])
                if trans_info:
                    translation_info = {
                        'questionNumber': trans_info['question_index'],
                        'questionContent': student['translation_question'] or trans_info['question_data']
                    }

            # 获取专业题目详情
            professional_info = None
            if student['professional_question_id']:
                prof_info = professional_questions.get(student['professional_question_id'])
                if prof_info:
                    # 科目映射
                    subject_map = get_subject_map()
                    subject_code = prof_info['subject']
                    professional_info = {
                        'questionNumber': prof_info['question_index'],
                        'questionContent': student['professional_question'] or prof_info['question_data'],
                        'subject': subject_map.get(subject_code, subject_code) if subject_code else None
                    }

            # 计算考试时长
            duration_minutes = None
            if student['total_duration']:
                duration_minutes = round(student['total_duration'] / 60, 1)

            # 格式化时间
            start_time_formatted = None
            end_time_formatted = None

            # 优先使用 students.start_time，如果没有则使用 exam_records 的创建时间作为备用
            effective_start_time = student['start_time'] or student['record_created_at']
            if effective_start_time:
                try:
                    start_dt = datetime.fromisoformat(effective_start_time)
                    start_time_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_time_formatted = effective_start_time

            if student['end_time']:
                try:
                    end_dt = datetime.fromisoformat(student['end_time'])
                    end_time_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    end_time_formatted = student['end_time']

            # 步骤名称映射
            step_map = {
                1: '中文自我介绍',
                2: '英文自我介绍',
                3: '英文翻译',
                4: '专业问题',
                5: '综合问答',
                6: '考试结束'
            }

            # 专业科目映射
            subject_map = get_subject_map()

            students.append({
                'studentNumber': student['student_number'],
                'name': student['name'] or '',
                'currentStep': step_map.get(student['current_step'], f'步骤{student["current_step"]}'),
                'examStatus': student['exam_status'],
                'translationInfo': translation_info,
                'professionalInfo': professional_info,
                'professionalSubject': subject_map.get(student['professional_subject'], student['professional_subject']) if student['professional_subject'] else None,
                'startTime': start_time_formatted,
                'endTime': end_time_formatted,
                'durationMinutes': duration_minutes,
                'createdAt': student['created_at'],
                'isCompleted': student['record_status'] == 'completed'
            })

        # 生成HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>研究生复试考试记录 - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 28px;
        }}
        .header .subtitle {{
            color: #666;
            margin-top: 10px;
            font-size: 16px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary h3 {{
            margin: 0 0 10px 0;
            color: #007bff;
        }}
        .student-record {{
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .student-header {{
            background: #007bff;
            color: white;
            padding: 15px;
            font-weight: bold;
            font-size: 18px;
        }}
        .student-content {{
            padding: 20px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .info-item {{
            display: flex;
            flex-direction: column;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #333;
        }}
        .question-section {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .question-title {{
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        .question-content {{
            background: white;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #007bff;
            margin-top: 10px;
        }}
        .question-text-part {{
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .question-image-part {{
            margin-bottom: 10px;
            text-align: center;
        }}
        .question-image-part img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .subject-stats {{
            margin-top: 15px;
        }}
        .subject-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .subject-item {{
            background: white;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #28a745;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .subject-name {{
            font-weight: 500;
            color: #333;
        }}
        .subject-count {{
            font-weight: bold;
            color: #28a745;
        }}
        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .status-completed {{
            background: #d4edda;
            color: #155724;
        }}
        .status-progress {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        .status-ready {{
            background: #fff3cd;
            color: #856404;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #666;
            font-size: 14px;
        }}
        @media print {{
            body {{ margin: 0; }}
            .student-record {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>研究生复试考试记录</h1>
        <div class="subtitle">导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</div>
    </div>

    <div class="summary">
        <h3>考试概况</h3>
        <p>总计学生数: {len(students)} 人 | 已完成考试: {len([s for s in students if s['isCompleted']])} 人 | 完成率: {round(len([s for s in students if s['isCompleted']]) / len(students) * 100, 1) if students else 0}%</p>

        <h4>专业科目分布</h4>
        <div class="subject-stats">
            {generate_subject_stats_html(students)}
        </div>
    </div>
"""

        # 为每个学生生成记录
        for student in students:
            status_class = 'status-completed' if student['isCompleted'] else 'status-ready'
            status_text = '已完成' if student['isCompleted'] else '未完成'

            html_content += f"""
    <div class="student-record">
        <div class="student-header">
            学生编号: {student['studentNumber']} {f"- {student['name']}" if student['name'] else ""}
            <span class="status-badge {status_class}" style="float: right;">{status_text}</span>
        </div>
        <div class="student-content">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">当前步骤</div>
                    <div class="info-value">{student['currentStep']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">考试状态</div>
                    <div class="info-value">{student['examStatus']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">开始时间</div>
                    <div class="info-value">{student['startTime'] or '未开始'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">结束时间</div>
                    <div class="info-value">{student['endTime'] or '未结束'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">考试时长</div>
                    <div class="info-value">{f"{student['durationMinutes']}分钟" if student['durationMinutes'] else '未计时'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">专业科目</div>
                    <div class="info-value">{student['professionalSubject'] or '未选择'}</div>
                </div>
            </div>
"""

            # 添加翻译题目信息
            if student['translationInfo']:
                formatted_content = format_question_content_for_html(student['translationInfo']['questionContent'])
                html_content += f"""
            <div class="question-section">
                <div class="question-title">英文翻译题目 (题目编号: {student['translationInfo']['questionNumber']})</div>
                <div class="question-content">{formatted_content}</div>
            </div>
"""

            # 添加专业题目信息
            if student['professionalInfo']:
                formatted_content = format_question_content_for_html(student['professionalInfo']['questionContent'])
                html_content += f"""
            <div class="question-section">
                <div class="question-title">专业问题 (题目编号: {student['professionalInfo']['questionNumber']})</div>
                <div class="question-content">{formatted_content}</div>
            </div>
"""

            html_content += """
        </div>
    </div>
"""

        html_content += f"""
    <div class="footer">
        <p>北京石油化工学院研究生复试系统 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""

        # 创建响应
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=exam_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

        return response

    except Exception as e:
        return format_response(
            success=False,
            error=f"导出HTML失败: {str(e)}",
            status_code=500
        )

@export_bp.route('/pdf', methods=['GET'])
def export_pdf():
    """导出PDF格式的考试记录（使用reportlab库）"""
    try:
        # 尝试导入reportlab
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import io
            import os
        except ImportError:
            return format_response(
                success=False,
                error="PDF导出功能需要安装reportlab库。请运行: pip install reportlab",
                status_code=500
            )

        # 获取学生数据（复用现有逻辑）
        conn = get_db_connection()

        # 获取所有学生的详细信息
        cursor = conn.execute('''
            SELECT
                s.student_number,
                s.name,
                s.current_step,
                s.exam_status,
                s.translation_question,
                s.translation_question_id,
                s.professional_question,
                s.professional_question_id,
                s.professional_subject,
                s.start_time,
                s.end_time,
                s.total_duration,
                s.created_at,
                er.exam_status as record_status,
                er.created_at as record_created_at
            FROM students s
            LEFT JOIN exam_records er ON s.student_number = er.student_number
            ORDER BY CAST(s.student_number AS INTEGER)
        ''')

        students_raw = cursor.fetchall()

        # 获取翻译题目信息
        translation_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data FROM translation_questions')
        for row in cursor.fetchall():
            translation_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data']
            }

        # 获取专业题目信息
        professional_questions = {}
        cursor = conn.execute('SELECT id, question_index, question_data, subject FROM professional_questions')
        for row in cursor.fetchall():
            professional_questions[row['id']] = {
                'question_index': row['question_index'],
                'question_data': row['question_data'],
                'subject': row['subject']
            }

        conn.close()

        # 构建学生数据
        students = []
        for student in students_raw:
            # 获取翻译题目详情
            translation_info = None
            if student['translation_question_id']:
                trans_info = translation_questions.get(student['translation_question_id'])
                if trans_info:
                    translation_info = {
                        'questionNumber': trans_info['question_index'],
                        'questionContent': student['translation_question'] or trans_info['question_data']
                    }

            # 获取专业题目详情
            professional_info = None
            if student['professional_question_id']:
                prof_info = professional_questions.get(student['professional_question_id'])
                if prof_info:
                    # 科目映射
                    subject_map = get_subject_map()
                    subject_code = prof_info['subject']
                    professional_info = {
                        'questionNumber': prof_info['question_index'],
                        'questionContent': student['professional_question'] or prof_info['question_data'],
                        'subject': subject_map.get(subject_code, subject_code) if subject_code else None
                    }

            # 计算考试时长
            duration_minutes = None
            if student['total_duration']:
                duration_minutes = round(student['total_duration'] / 60, 1)

            # 格式化时间
            start_time_formatted = None
            end_time_formatted = None

            # 优先使用 students.start_time，如果没有则使用 exam_records 的创建时间作为备用
            effective_start_time = student['start_time'] or student['record_created_at']
            if effective_start_time:
                try:
                    start_dt = datetime.fromisoformat(effective_start_time)
                    start_time_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_time_formatted = effective_start_time

            if student['end_time']:
                try:
                    end_dt = datetime.fromisoformat(student['end_time'])
                    end_time_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    end_time_formatted = student['end_time']

            # 步骤名称映射
            step_map = {
                1: '中文自我介绍',
                2: '英文自我介绍',
                3: '英文翻译',
                4: '专业问题',
                5: '综合问答',
                6: '考试结束'
            }

            # 专业科目映射
            subject_map = get_subject_map()

            students.append({
                'studentNumber': student['student_number'],
                'name': student['name'] or '',
                'currentStep': step_map.get(student['current_step'], f'步骤{student["current_step"]}'),
                'examStatus': student['exam_status'],
                'translationInfo': translation_info,
                'professionalInfo': professional_info,
                'professionalSubject': subject_map.get(student['professional_subject'], student['professional_subject']) if student['professional_subject'] else None,
                'startTime': start_time_formatted,
                'endTime': end_time_formatted,
                'durationMinutes': duration_minutes,
                'createdAt': student['created_at'],
                'isCompleted': student['record_status'] == 'completed'
            })

        # 创建PDF文档
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)

        # 获取样式
        styles = getSampleStyleSheet()

        # 尝试注册中文字体（如果可用）
        chinese_font_available = False
        try:
            # 尝试使用系统中文字体
            font_paths = [
                'C:/Windows/Fonts/msyh.ttf',  # 微软雅黑
                'C:/Windows/Fonts/simsun.ttf',  # 宋体
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        chinese_font_available = True
                        break
                    except:
                        continue
        except:
            pass  # 如果注册字体失败，使用默认字体

        # 创建自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            spaceBefore=0,
            alignment=1,  # 居中
            fontName='ChineseFont' if chinese_font_available else 'Helvetica-Bold',
            textColor=colors.HexColor('#2c3e50')
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            fontName='ChineseFont' if chinese_font_available else 'Helvetica-Bold',
            textColor=colors.HexColor('#34495e'),
            leftIndent=0
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=0,
            fontName='ChineseFont' if chinese_font_available else 'Helvetica',
            textColor=colors.HexColor('#2c3e50'),
            leftIndent=0,
            rightIndent=0,
            leading=14
        )

        # 题目内容样式
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=normal_style,
            fontSize=10,
            leftIndent=12,
            rightIndent=12,
            spaceAfter=8,
            leading=13,
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#dee2e6'),
            borderWidth=1,
            borderPadding=8
        )

        # 构建PDF内容
        story = []

        # 添加标题
        title = Paragraph("研究生复试考试记录", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # 添加导出时间
        export_time = Paragraph(f"导出时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}", normal_style)
        story.append(export_time)
        story.append(Spacer(1, 20))

        # 添加统计概况
        completed_count = len([s for s in students if s['isCompleted']])
        completion_rate = round((completed_count / len(students) * 100), 1) if students else 0

        summary_text = f"总计学生数: {len(students)} 人 | 已完成考试: {completed_count} 人 | 完成率: {completion_rate}%"
        summary = Paragraph(summary_text, normal_style)
        story.append(summary)
        story.append(Spacer(1, 20))

        # 添加专业科目分布
        subject_counts = {}
        subject_map = get_subject_map()

        for student in students:
            if student.get('professionalSubject'):
                subject = student['professionalSubject']
                subject_counts[subject] = subject_counts.get(subject, 0) + 1

        if subject_counts:
            story.append(Paragraph("专业科目分布:", heading_style))
            subject_data = [['专业科目', '学生数量']]
            for subject, count in subject_counts.items():
                subject_data.append([subject, f"{count}人"])

            subject_table = Table(subject_data, colWidths=[8*cm, 4*cm])
            subject_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if chinese_font_available else 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'ChineseFont' if chinese_font_available else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(subject_table)
            story.append(Spacer(1, 30))

        # 为每个学生添加记录
        for i, student in enumerate(students):
            if i > 0:
                story.append(Spacer(1, 20))

            # 学生标题
            student_title = f"学生编号: {student['studentNumber']}"
            if student['name']:
                student_title += f" - {student['name']}"

            status_text = " (已完成)" if student['isCompleted'] else " (未完成)"
            student_title += status_text

            story.append(Paragraph(student_title, heading_style))
            story.append(Spacer(1, 10))

            # 学生基本信息表格
            info_data = [
                ['当前步骤', student['currentStep']],
                ['考试状态', student['examStatus']],
                ['开始时间', student['startTime'] or '未开始'],
                ['结束时间', student['endTime'] or '未结束'],
                ['考试时长', f"{student['durationMinutes']}分钟" if student['durationMinutes'] else '未计时'],
                ['专业科目', student['professionalSubject'] or '未选择']
            ]

            info_table = Table(info_data, colWidths=[4*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'ChineseFont' if chinese_font_available else 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'ChineseFont' if chinese_font_available else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 15))

            # 添加题目信息
            if student['translationInfo']:
                story.append(Paragraph(f"英文翻译题目 (题目编号: {student['translationInfo']['questionNumber']})", heading_style))
                story.append(Spacer(1, 6))
                # 添加题目内容元素（包含图片）
                question_elements = format_question_content_for_pdf_elements(
                    student['translationInfo']['questionContent'],
                    normal_style,
                    question_style
                )
                story.extend(question_elements)
                story.append(Spacer(1, 15))

            if student['professionalInfo']:
                story.append(Paragraph(f"专业问题 (题目编号: {student['professionalInfo']['questionNumber']})", heading_style))
                story.append(Spacer(1, 6))
                # 添加题目内容元素（包含图片）
                question_elements = format_question_content_for_pdf_elements(
                    student['professionalInfo']['questionContent'],
                    normal_style,
                    question_style
                )
                story.extend(question_elements)
                story.append(Spacer(1, 15))

        # 添加页脚
        story.append(Spacer(1, 30))
        footer_text = f"北京石油化工学院研究生复试系统 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer = Paragraph(footer_text, normal_style)
        story.append(footer)

        # 生成PDF
        doc.build(story)

        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()

        # 创建响应
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=exam_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

        return response

    except Exception as e:
        import traceback
        logger.error(f"[PDF Export Error] {str(e)}", exc_info=True)
        return format_response(
            success=False,
            error=f"导出PDF失败: {str(e)}",
            status_code=500
        )
