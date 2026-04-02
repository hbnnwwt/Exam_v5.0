import json
import os
from flask import jsonify, request
from . import ai_bp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')

def _load_json_config():
    """Load JSON config file, handling both list and dict formats."""
    if not os.path.exists(CONFIG_FILE):
        return {'providers': [], 'defaultProvider': None}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            return {'providers': data, 'defaultProvider': None}
        return data

def load_config():
    """加载完整配置（包含providers和defaultProvider）"""
    if not os.path.exists(CONFIG_FILE):
        return {'providers': [], 'defaultProvider': None}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # 兼容旧格式（直接是数组）
        if isinstance(data, list):
            return {'providers': data, 'defaultProvider': None}
        return data

def save_config(config):
    """保存完整配置"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_providers():
    """
    返回所有 provider 配置。
    key 优先从 api_keys.py 的 load_api_key() 获取（ENV→DB→JSON）。
    只返回 id、name、baseUrl、defaultModel、apiFormat，不返回 apiKey 明文。
    """
    from .api_keys import load_api_key, load_all_from_db

    json_config = _load_json_config()
    json_providers = json_config.get('providers', [])

    # 合并 JSON 中的 provider 定义
    all_ids = set()
    for p in json_providers:
        if p.get('id'):
            all_ids.add(p['id'])

    # 合并 DB 中的自定义 provider
    db_providers = load_all_from_db()
    for db_p in db_providers:
        if db_p.get('id'):
            all_ids.add(db_p['id'])

    result = []
    for pid in all_ids:
        full_config = load_api_key(pid)
        if full_config:
            result.append({
                'id': full_config.get('id'),
                'name': full_config.get('name', pid),
                'baseUrl': full_config.get('baseUrl', ''),
                'defaultModel': full_config.get('defaultModel', ''),
                'apiFormat': full_config.get('apiFormat', 'openai'),
                'hasApiKey': bool(full_config.get('apiKey')),
            })
    return result

def save_providers(providers):
    """保存providers列表（兼容旧代码）"""
    config = load_config()
    config['providers'] = providers
    save_config(config)

@ai_bp.route('/providers', methods=['GET'])
def get_providers():
    return jsonify(load_providers())

@ai_bp.route('/providers', methods=['POST'])
def save_provider():
    """保存提供商配置到数据库"""
    from .api_keys import save_to_db, load_from_db

    data = request.json
    provider_id = data.get('provider') or data.get('id')
    
    # 获取现有配置（如果存在）
    existing = load_from_db(provider_id) or {}
    
    # 如果 api_key 为空字符串，保留已有的 key
    api_key = data.get('apiKey', '')
    if api_key == '' and existing.get('apiKey'):
        api_key = existing['apiKey']

    save_to_db(
        provider_id,
        api_key=api_key,
        base_url=data.get('baseUrl', ''),
        default_model=data.get('defaultModel', ''),
        is_default=0
    )

    return jsonify({'success': True})

@ai_bp.route('/providers/<provider_id>', methods=['PUT'])
def update_provider(provider_id):
    from .api_keys import save_to_db, load_from_db

    existing = load_from_db(provider_id) or {}

    api_key = request.json.get('apiKey', '')
    if api_key == '' and existing.get('apiKey'):
        api_key = existing['apiKey']

    save_to_db(
        provider_id,
        api_key=api_key,
        base_url=request.json.get('baseUrl', ''),
        default_model=request.json.get('defaultModel', ''),
        is_default=0,
    )
    return jsonify({
        'id': provider_id,
        'name': request.json.get('name', provider_id),
        'baseUrl': request.json.get('baseUrl', ''),
        'defaultModel': request.json.get('defaultModel', ''),
        'apiFormat': request.json.get('apiFormat', 'openai'),
        'hasApiKey': bool(api_key),
    })

@ai_bp.route('/providers/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    from .api_keys import delete_from_db
    delete_from_db(provider_id)
    return jsonify({'success': True})

@ai_bp.route('/default-provider', methods=['GET'])
def get_default_provider():
    """获取默认provider"""
    from .api_keys import get_default_provider_id, load_from_db

    default_id = get_default_provider_id()
    if not default_id:
        return jsonify({'id': None})

    db_row = load_from_db(default_id)
    if db_row:
        return jsonify({'id': db_row.get('id'), 'name': db_row.get('name', default_id)})
    return jsonify({'id': None})

@ai_bp.route('/default-provider', methods=['POST'])
def set_default_provider():
    """设置默认provider"""
    from .api_keys import set_default_provider as db_set_default, load_from_db

    data = request.json
    provider_id = data.get('provider')

    # 验证provider是否存在
    if provider_id:
        db_row = load_from_db(provider_id)
        if not db_row:
            # provider 不在 DB 中，检查 JSON 模板
            json_config = _load_json_config()
            json_providers = json_config.get('providers', [])
            provider = next((p for p in json_providers if p.get('id') == provider_id), None)
            if not provider:
                return jsonify({'error': 'Provider not found'}), 404

    db_set_default(provider_id)
    return jsonify({'success': True, 'id': provider_id})