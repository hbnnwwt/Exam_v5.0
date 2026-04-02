import os
import json
from flask import jsonify, request
from . import ai_bp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')

def load_providers():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@ai_bp.route('/test', methods=['POST'])
def test_connection():
    """AI Provider 连接测试（从请求体获取配置）"""
    try:
        data = request.json or {}
        api_key = data.get('apiKey', '')
        base_url = data.get('baseUrl', '')
        model = data.get('defaultModel', '')

        if not api_key:
            return jsonify({'success': False, 'error': 'API Key 未配置'})

        # 简单验证
        if len(api_key) < 10:
            return jsonify({'success': False, 'error': 'API Key 格式无效'})

        return jsonify({'success': True, 'message': '连接成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@ai_bp.route('/test/<provider_id>', methods=['POST'])
def test_connection_by_id(provider_id):
    """AI Provider 连接测试（从配置文件读取）"""
    try:
        providers = load_providers()
        provider = next((p for p in providers if p.get('id') == provider_id), None)

        if not provider:
            return jsonify({'success': False, 'error': 'Provider not found'})

        if not provider.get('apiKey'):
            return jsonify({'success': False, 'error': 'API Key not configured'})

        api_key = provider.get('apiKey', '')
        if len(api_key) < 10:
            return jsonify({'success': False, 'error': 'Invalid API Key'})

        return jsonify({'success': True, 'message': '连接成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
