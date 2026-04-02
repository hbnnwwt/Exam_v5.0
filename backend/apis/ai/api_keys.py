import os
import json
import sqlite3
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'assets', 'data', 'interview_system.db')

# ENV key 前缀映射表
ENV_KEY_MAP = {
    'openai': 'OPENAI_API_KEY',
    'claude': 'ANTHROPIC_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'minimax': 'MINIMAX_API_KEY',
    'modelscope': 'MODELSCOPE_API_KEY',
    'siliconflow': 'SILICONFLOW_API_KEY',
}

def _get_db_path():
    return os.environ.get('DATABASE_PATH', DB_PATH)

def _get_conn():
    db_dir = os.path.dirname(_get_db_path())
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def _load_from_json():
    """从 JSON 模板加载默认配置（不含 key）"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_provider_from_json(provider_id):
    """从 JSON 模板获取 provider 的 base_url 和 default_model（不含 key）"""
    data = _load_from_json()
    providers = data.get('providers', []) if isinstance(data, dict) else data
    for p in providers:
        if p.get('id') == provider_id:
            return {
                'id': p.get('id'),
                'name': p.get('name'),
                'baseUrl': p.get('baseUrl', ''),
                'defaultModel': p.get('defaultModel', ''),
                'apiFormat': p.get('apiFormat', 'openai'),
            }
    return None

def load_from_db(provider_id):
    """从数据库读取 provider 配置"""
    conn = _get_conn()
    try:
        row = conn.execute(
            'SELECT id, api_key, base_url, default_model, is_default FROM api_keys WHERE id = ?',
            (provider_id,)
        ).fetchone()
        if row:
            return {
                'id': row['id'],
                'apiKey': row['api_key'],
                'baseUrl': row['base_url'],
                'defaultModel': row['default_model'],
                'is_default': row['is_default'],
            }
        return None
    finally:
        conn.close()

def save_to_db(provider_id, api_key='', base_url='', default_model='', is_default=0):
    """保存 provider 配置到数据库"""
    conn = _get_conn()
    try:
        conn.execute('''
            INSERT INTO api_keys (id, api_key, base_url, default_model, is_default, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                api_key = excluded.api_key,
                base_url = excluded.base_url,
                default_model = excluded.default_model,
                is_default = excluded.is_default,
                updated_at = excluded.updated_at
        ''', (provider_id, api_key, base_url, default_model, is_default, datetime.now().isoformat()))
        conn.commit()
    finally:
        conn.close()

def load_all_from_db():
    """从数据库读取所有 provider 配置"""
    conn = _get_conn()
    try:
        rows = conn.execute('SELECT * FROM api_keys').fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_default_provider_id():
    """获取默认 provider id（从 ENV → DB → JSON 依次查找）"""
    # 1. 优先 ENV
    default_env = os.environ.get('DEFAULT_PROVIDER', '').lower()
    if default_env and default_env in ENV_KEY_MAP:
        api_key = os.environ.get(ENV_KEY_MAP[default_env], '')
        if api_key:
            return default_env

    # 2. DB 中找 is_default=1 的
    conn = _get_conn()
    try:
        row = conn.execute('SELECT id FROM api_keys WHERE is_default = 1').fetchone()
        if row:
            return row['id']
    finally:
        conn.close()

    # 3. JSON 模板中的 defaultProvider
    data = _load_from_json()
    if isinstance(data, dict) and data.get('defaultProvider'):
        return data['defaultProvider']
    return None

def set_default_provider(provider_id):
    """设置默认 provider"""
    conn = _get_conn()
    try:
        conn.execute('UPDATE api_keys SET is_default = 0')
        if provider_id:
            conn.execute('UPDATE api_keys SET is_default = 1 WHERE id = ?', (provider_id,))
        conn.commit()
    finally:
        conn.close()

def load_api_key(provider_id):
    """
    核心读取函数：ENV → DB → JSON 模板
    返回完整的 provider 配置对象（含 apiKey）
    """
    # 1. 优先从 ENV 读
    env_key = ENV_KEY_MAP.get(provider_id)
    if env_key:
        api_key = os.environ.get(env_key, '')
        if api_key:
            json_fallback = load_provider_from_json(provider_id)
            return {
                'id': provider_id,
                'apiKey': api_key,
                'baseUrl': os.environ.get(f'{provider_id.upper()}_BASE_URL', json_fallback.get('baseUrl', '') if json_fallback else ''),
                'defaultModel': os.environ.get(f'{provider_id.upper()}_MODEL', json_fallback.get('defaultModel', '') if json_fallback else ''),
                'apiFormat': os.environ.get(f'{provider_id.upper()}_API_FORMAT', json_fallback.get('apiFormat', 'openai') if json_fallback else 'openai'),
            }

    # 2. 从 DB 读
    db_row = load_from_db(provider_id)
    if db_row and db_row.get('apiKey'):
        return db_row

    # 3. 从 JSON 模板读（仅 base_url 和 default_model，key 为空）
    return load_provider_from_json(provider_id)

def delete_from_db(provider_id):
    """从数据库删除 provider"""
    conn = _get_conn()
    try:
        conn.execute('DELETE FROM api_keys WHERE id = ?', (provider_id,))
        conn.commit()
    finally:
        conn.close()
