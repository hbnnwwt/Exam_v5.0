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
    from .api_keys import save_to_db, get_default_provider_id

    data = request.json
    provider_id = data.get('provider') or data.get('id')

    save_to_db(
        provider_id,
        api_key=data.get('apiKey', ''),
        base_url=data.get('baseUrl', ''),
        default_model=data.get('defaultModel', ''),
        is_default=1 if get_default_provider_id() == provider_id else 0
    )

    return jsonify({'success': True})

@ai_bp.route('/providers/<provider_id>', methods=['PUT'])
def update_provider(provider_id):
    from .api_keys import save_to_db

    save_to_db(
        provider_id,
        api_key=request.json.get('apiKey', ''),
        base_url=request.json.get('baseUrl', ''),
        default_model=request.json.get('defaultModel', ''),
    )
    return jsonify(request.json)

@ai_bp.route('/providers/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    from .api_keys import delete_from_db
    delete_from_db(provider_id)
    return jsonify({'success': True})

@ai_bp.route('/default-provider', methods=['GET'])
def get_default_provider():
    """获取默认provider"""
    config = load_config()
    default_id = config.get('defaultProvider')
    if not default_id:
        return jsonify({'id': None})
    # 验证默认provider是否存在且已配置（有apiKey）
    providers = config.get('providers', [])
    provider = next((p for p in providers if p.get('id') == default_id and p.get('apiKey')), None)
    if provider:
        return jsonify({'id': provider.get('id'), 'name': provider.get('name', provider.get('id'))})
    return jsonify({'id': None})

@ai_bp.route('/default-provider', methods=['POST'])
def set_default_provider():
    """设置默认provider"""
    data = request.json
    provider_id = data.get('provider')

    config = load_config()

    if provider_id:
        # 验证provider是否存在且有apiKey
        providers = config.get('providers', [])
        provider = next((p for p in providers if p.get('id') == provider_id), None)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        if not provider.get('apiKey'):
            return jsonify({'error': 'Provider is not configured'}), 400

    config['defaultProvider'] = provider_id
    save_config(config)
    return jsonify({'success': True, 'id': provider_id})