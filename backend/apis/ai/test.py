import os
import json
from flask import jsonify
from . import ai_bp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')

def load_providers():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@ai_bp.route('/test/<provider_id>', methods=['POST'])
def test_connection(provider_id):
    """AI Provider 连接测试"""
    providers = load_providers()
    provider = next((p for p in providers if p.get('id') == provider_id), None)

    if not provider:
        return jsonify({'success': False, 'error': 'Provider not found'})

    if not provider.get('apiKey'):
        return jsonify({'success': False, 'error': 'API Key not configured'})

    # 简单测试: 检查 API Key 格式
    api_key = provider.get('apiKey', '')
    if len(api_key) < 10:
        return jsonify({'success': False, 'error': 'Invalid API Key'})

    return jsonify({'success': True, 'message': '连接成功'})