"""
系统设置模块 - 处理考试系统的配置和设置
"""

import logging
from flask import Blueprint, request
from ..common.database import get_db_connection
from ..common.utils import format_response, validate_request

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('', methods=['GET'])
def get_settings():
    """获取考试系统设置"""
    try:
        # 动态从数据库获取步骤信息，构建时间设置
        time_settings = {}
        total_steps = 0

        try:
            conn = get_db_connection()
            # 从 exam_steps 表读取所有步骤的时长配置
            cursor = conn.execute('''
                SELECT step_number, title, duration
                FROM exam_steps
                WHERE is_active = 1
                ORDER BY step_number
            ''')
            steps = cursor.fetchall()

            # 动态构建时间设置
            for step in steps:
                step_num = step['step_number']
                time_settings[f'step{step_num}Time'] = step['duration'] or 0

            # 获取总步骤数
            total_steps = len(steps)

            conn.close()

        except Exception as e:
            logger.warning(f"获取步骤设置失败，使用空配置: {e}")
            total_steps = 0
            # 如果 exam_steps 表不存在，使用默认步骤配置
            time_settings = {
                'step1Time': 120,
                'step2Time': 120,
                'step3Time': 300,
                'step4Time': 600,
                'step5Time': 480,
                'step6Time': 0
            }

        # 基础设置（这些不是从 exam_steps 读取的）
        default_settings = {
            'timeSettings': time_settings,
            'examSettings': {
                'totalSteps': total_steps,  # 动态从数据库获取
                'autoSave': True,
                'autoSaveInterval': 30,
                'allowPause': True,
                'allowSkip': False,
                'showProgress': True,
                'showTimer': True,
                'randomQuestions': True
            },
            'uiSettings': {
                'showLeftPanel': True,
                'showRightPanel': True,
                'leftPanelWidth': 20,
                'rightPanelWidth': 20,
                'fontSize': 'medium',
                'compactMode': False,
                'animations': True,
                'sounds': False
            },
            'systemSettings': {
                'debugMode': False,
                'logLevel': 'info',
                'maxStudents': 1000,
                'dataRetentionDays': 365,
                'backupEnabled': True,
                'backupInterval': 24
            }
        }

        # 从数据库获取其他自定义设置
        try:
            conn = get_db_connection()
            cursor = conn.execute('SELECT * FROM settings')
            db_settings = cursor.fetchall()
            conn.close()

            # 合并数据库设置到默认设置
            for setting in db_settings:
                category = setting.get('category', 'general')
                key = setting.get('key')
                value = setting.get('value')

                if category in default_settings:
                    try:
                        import json
                        parsed_value = json.loads(value) if isinstance(value, str) else value
                        default_settings[category][key] = parsed_value
                    except (json.JSONDecodeError, TypeError):
                        default_settings[category][key] = value

        except Exception as e:
            logger.warning(f"获取数据库设置失败: {e}")

        return format_response(
            success=True,
            data=default_settings,
            message="获取系统设置成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取系统设置失败: {str(e)}",
            status_code=500
        )

@settings_bp.route('', methods=['PUT'])
def update_settings():
    """更新考试系统设置"""
    try:
        data = request.get_json()
        
        if not data:
            return format_response(
                success=False,
                error="请求数据不能为空",
                status_code=400
            )
        
        conn = get_db_connection()
        
        # 更新设置到数据库
        updated_count = 0
        for category, settings in data.items():
            if isinstance(settings, dict):
                for key, value in settings.items():
                    try:
                        import json
                        value_str = json.dumps(value) if not isinstance(value, str) else value
                        
                        # 检查设置是否存在
                        cursor = conn.execute('''
                            SELECT id FROM settings 
                            WHERE category = ? AND key = ?
                        ''', (category, key))
                        
                        if cursor.fetchone():
                            # 更新现有设置
                            conn.execute('''
                                UPDATE settings 
                                SET value = ?, updated_at = datetime('now')
                                WHERE category = ? AND key = ?
                            ''', (value_str, category, key))
                        else:
                            # 插入新设置
                            conn.execute('''
                                INSERT INTO settings (category, key, value, created_at, updated_at)
                                VALUES (?, ?, ?, datetime('now'), datetime('now'))
                            ''', (category, key, value_str))
                        
                        updated_count += 1
                        
                    except Exception as e:
                        logger.warning(f"更新设置失败 {category}.{key}: {e}")
                        continue
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={'updatedCount': updated_count},
            message=f"成功更新了 {updated_count} 项设置"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新系统设置失败: {str(e)}",
            status_code=500
        )

@settings_bp.route('/<category>', methods=['GET'])
def get_category_settings(category):
    """获取指定分类的设置"""
    try:
        valid_categories = ['timeSettings', 'examSettings', 'uiSettings', 'systemSettings']
        if category not in valid_categories:
            return format_response(
                success=False,
                error=f'无效的设置分类，有效分类: {", ".join(valid_categories)}',
                status_code=400
            )
        
        conn = get_db_connection()
        cursor = conn.execute('''
            SELECT key, value FROM settings 
            WHERE category = ?
        ''', (category,))
        
        settings = cursor.fetchall()
        conn.close()
        
        result = {}
        for setting in settings:
            try:
                import json
                value = json.loads(setting['value']) if isinstance(setting['value'], str) else setting['value']
                result[setting['key']] = value
            except (json.JSONDecodeError, TypeError):
                result[setting['key']] = setting['value']
        
        return format_response(
            success=True,
            data=result,
            message=f"获取 {category} 设置成功"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"获取设置分类失败: {str(e)}",
            status_code=500
        )

@settings_bp.route('/<category>/<key>', methods=['PUT'])
def update_single_setting(category, key):
    """更新单个设置项"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        is_valid, error_msg = validate_request(data, ['value'])
        if not is_valid:
            return format_response(
                success=False,
                error=error_msg,
                status_code=400
            )
        
        value = data.get('value')
        
        conn = get_db_connection()
        
        try:
            import json
            value_str = json.dumps(value) if not isinstance(value, str) else value
            
            # 检查设置是否存在
            cursor = conn.execute('''
                SELECT id FROM settings 
                WHERE category = ? AND key = ?
            ''', (category, key))
            
            if cursor.fetchone():
                # 更新现有设置
                conn.execute('''
                    UPDATE settings 
                    SET value = ?, updated_at = datetime('now')
                    WHERE category = ? AND key = ?
                ''', (value_str, category, key))
            else:
                # 插入新设置
                conn.execute('''
                    INSERT INTO settings (category, key, value, created_at, updated_at)
                    VALUES (?, ?, ?, datetime('now'), datetime('now'))
                ''', (category, key, value_str))
            
            conn.commit()
            conn.close()
            
            return format_response(
                success=True,
                data={
                    'category': category,
                    'key': key,
                    'value': value
                },
                message=f"设置 {category}.{key} 更新成功"
            )
            
        except Exception as e:
            conn.close()
            return format_response(
                success=False,
                error=f"更新设置失败: {str(e)}",
                status_code=500
            )

    except Exception as e:
        return format_response(
            success=False,
            error=f"更新单个设置失败: {str(e)}",
            status_code=500
        )

@settings_bp.route('/reset', methods=['POST'])
def reset_settings():
    """重置所有设置为默认值"""
    try:
        conn = get_db_connection()
        
        # 删除所有自定义设置
        cursor = conn.execute('DELETE FROM settings')
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return format_response(
            success=True,
            data={'deletedCount': deleted_count},
            message=f"成功重置设置，删除了 {deleted_count} 项自定义设置"
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f"重置设置失败: {str(e)}",
            status_code=500
        )
