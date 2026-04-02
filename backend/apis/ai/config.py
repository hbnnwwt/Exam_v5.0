import json
import os
from flask import jsonify, request
from . import ai_bp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')

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
    """加载providers列表（兼容旧代码）"""
    config = load_config()
    return config.get('providers', [])

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
    """保存提供商配置（存在则更新，不存在则添加）"""
    providers = load_providers()
    data = request.json

    # 前端发送 {provider: 'minimax', apiKey: '...', ...}
    provider_id = data.get('provider') or data.get('id')

    # 查找是否已存在
    found = False
    for i, p in enumerate(providers):
        if p.get('id') == provider_id:
            # 更新已有提供商
            if 'apiKey' in data:
                providers[i]['apiKey'] = data['apiKey']
            if 'baseUrl' in data:
                providers[i]['baseUrl'] = data['baseUrl']
            if 'defaultModel' in data:
                providers[i]['defaultModel'] = data['defaultModel']
            if 'enabled' in data:
                providers[i]['enabled'] = data['enabled']
            if 'apiFormat' in data:
                providers[i]['apiFormat'] = data['apiFormat']
            found = True
            break

    if not found:
        # 添加新提供商
        new_provider = {
            'id': provider_id or f"custom_{len(providers)}",
            'name': data.get('name', provider_id),
            'apiKey': data.get('apiKey', ''),
            'baseUrl': data.get('baseUrl', ''),
            'defaultModel': data.get('defaultModel', ''),
            'enabled': data.get('enabled', False),
            'apiFormat': data.get('apiFormat', 'openai')
        }
        providers.append(new_provider)

    save_providers(providers)
    return jsonify({'success': True})

@ai_bp.route('/providers/<provider_id>', methods=['PUT'])
def update_provider(provider_id):
    providers = load_providers()
    for i, p in enumerate(providers):
        if p.get('id') == provider_id:
            providers[i].update(request.json)
            save_providers(providers)
            return jsonify(providers[i])
    return jsonify({'error': 'Provider not found'}), 404

@ai_bp.route('/providers/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    providers = load_providers()
    providers = [p for p in providers if p.get('id') != provider_id]
    save_providers(providers)
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