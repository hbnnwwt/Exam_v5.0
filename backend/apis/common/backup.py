"""
数据库自动备份模块 - 定时自动备份SQLite数据库
"""
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import json
from apis.common.logger import logger

# 备份配置
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backups')
BACKUP_CONFIG_FILE = os.path.join(BACKUP_DIR, 'backup_config.json')

# 默认配置
DEFAULT_CONFIG = {
    'enabled': True,
    'interval_hours': 24,  # 备份间隔（小时）
    'max_backups': 7,  # 最多保留的备份数量
    'auto_cleanup': True  # 自动清理旧备份
}

_config = DEFAULT_CONFIG.copy()

def ensure_backup_dir():
    """确保备份目录存在"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def load_config():
    """加载备份配置"""
    global _config
    ensure_backup_dir()
    if os.path.exists(BACKUP_CONFIG_FILE):
        try:
            with open(BACKUP_CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                _config.update(loaded)
        except Exception as e:
            logger.error(f"Failed to load backup config: {e}")
    return _config

def save_config():
    """保存备份配置"""
    ensure_backup_dir()
    try:
        with open(BACKUP_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(_config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save backup config: {e}")

def get_backup_config():
    """获取当前备份配置"""
    return _config.copy()

def update_backup_config(**kwargs):
    """更新备份配置"""
    global _config
    _config.update(kwargs)
    save_config()
    return _config

def get_database_path():
    """获取数据库文件路径"""
    from config import get_config
    config = get_config()
    return config.DATABASE

def create_backup():
    """
    创建数据库备份
    
    Returns:
        tuple: (success, backup_file_path, message)
    """
    ensure_backup_dir()
    
    db_path = get_database_path()
    if not os.path.exists(db_path):
        return False, None, f"数据库文件不存在: {db_path}"
    
    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.db")
    
    try:
        # 使用SQLite的backup API进行在线备份
        conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_file)
        
        conn.backup(backup_conn)
        
        conn.close()
        backup_conn.close()
        
        logger.info(f"Database backup created: {backup_file}")
        
        # 自动清理旧备份
        if _config.get('auto_cleanup', True):
            cleanup_old_backups()
        
        return True, backup_file, "备份成功"
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False, None, f"备份失败: {str(e)}"

def restore_backup(backup_file):
    """
    恢复数据库备份
    
    Args:
        backup_file (str): 备份文件路径
        
    Returns:
        tuple: (success, message)
    """
    db_path = get_database_path()
    
    if not os.path.exists(backup_file):
        return False, f"备份文件不存在: {backup_file}"
    
    if not os.path.exists(db_path):
        return False, f"数据库文件不存在: {db_path}"
    
    try:
        # 关闭所有连接后恢复
        # 首先创建一个临时副本
        temp_backup = backup_file + '.restoring'
        shutil.copy2(backup_file, temp_backup)
        
        # 替换原数据库
        shutil.copy2(temp_backup, db_path)
        os.remove(temp_backup)
        
        logger.info(f"Database restored from: {backup_file}")
        return True, "恢复成功"
        
    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False, f"恢复失败: {str(e)}"

def list_backups():
    """列出所有备份文件"""
    ensure_backup_dir()
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.startswith('backup_') and f.endswith('.db'):
            fpath = os.path.join(BACKUP_DIR, f)
            stat = os.stat(fpath)
            backups.append({
                'filename': f,
                'path': fpath,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
    
    # 按创建时间排序
    backups.sort(key=lambda x: x['created'], reverse=True)
    return backups

def cleanup_old_backups():
    """清理旧备份"""
    max_backups = _config.get('max_backups', 7)
    backups = list_backups()
    
    if len(backups) <= max_backups:
        return
    
    # 删除多余的备份
    for backup in backups[max_backups:]:
        try:
            os.remove(backup['path'])
            logger.info(f"Old backup removed: {backup['filename']}")
        except Exception as e:
            logger.error(f"Failed to remove old backup {backup['filename']}: {e}")

# 定时备份任务
_backup_thread = None
_stop_event = None

def start_scheduled_backup(interval_hours=None):
    """启动定时备份"""
    global _backup_thread, _stop_event
    
    if interval_hours:
        _config['interval_hours'] = interval_hours
    
    if _backup_thread and _backup_thread.is_alive():
        logger.warning("Scheduled backup is already running")
        return False, "定时备份已在运行"
    
    _stop_event = threading.Event()
    _backup_thread = threading.Thread(target=_backup_loop, daemon=True)
    _backup_thread.start()
    
    logger.info(f"Scheduled backup started (interval: {_config['interval_hours']} hours)")
    return True, "定时备份已启动"

def stop_scheduled_backup():
    """停止定时备份"""
    global _backup_thread, _stop_event
    
    if _stop_event:
        _stop_event.set()
    
    if _backup_thread:
        _backup_thread.join(timeout=5)
    
    logger.info("Scheduled backup stopped")
    return True, "定时备份已停止"

def _backup_loop():
    """备份循环（后台线程）"""
    interval_seconds = _config['interval_hours'] * 3600
    
    while not _stop_event.is_set():
        try:
            if _config.get('enabled', True):
                success, path, msg = create_backup()
                if success:
                    logger.info(f"Scheduled backup completed: {path}")
                else:
                    logger.error(f"Scheduled backup failed: {msg}")
        except Exception as e:
            logger.error(f"Error in backup loop: {e}")
        
        # 等待下一次备份
        _stop_event.wait(interval_seconds)

def get_backup_blueprint():
    """创建备份管理蓝图"""
    from flask import Blueprint, jsonify, send_file
    from apis.common.utils import format_response
    
    backup_bp = Blueprint('backup', __name__, url_prefix='/backup-api')
    
    @backup_bp.route('/create', methods=['POST'])
    def create():
        """手动创建备份"""
        success, path, msg = create_backup()
        if success:
            return format_response(success=True, data={'path': path}, message=msg)
        return format_response(success=False, error=msg, status_code=500)
    
    @backup_bp.route('/list', methods=['GET'])
    def list():
        """列出所有备份"""
        backups = list_backups()
        return format_response(success=True, data={'backups': backups})
    
    @backup_bp.route('/restore', methods=['POST'])
    def restore():
        """恢复备份"""
        data = request.get_json()
        if not data or 'backup_file' not in data:
            return format_response(success=False, error='缺少backup_file参数', status_code=400)
        
        success, msg = restore_backup(data['backup_file'])
        if success:
            return format_response(success=True, message=msg)
        return format_response(success=False, error=msg, status_code=500)
    
    @backup_bp.route('/config', methods=['GET'])
    def get_config():
        """获取备份配置"""
        return format_response(success=True, data=get_backup_config())
    
    @backup_bp.route('/config', methods=['POST'])
    def set_config():
        """更新备份配置"""
        data = request.get_json()
        if data:
            config = update_backup_config(**data)
            return format_response(success=True, data=config, message='配置已更新')
        return format_response(success=False, error='请求数据不能为空', status_code=400)
    
    @backup_bp.route('/schedule/start', methods=['POST'])
    def start_schedule():
        """启动定时备份"""
        interval = request.json.get('interval_hours') if request.json else None
        success, msg = start_scheduled_backup(interval)
        if success:
            return format_response(success=True, message=msg)
        return format_response(success=False, error=msg, status_code=400)
    
    @backup_bp.route('/schedule/stop', methods=['POST'])
    def stop_schedule():
        """停止定时备份"""
        success, msg = stop_scheduled_backup()
        return format_response(success=success, message=msg)
    
    return backup_bp
