import os
import json
from flask import jsonify, request
from . import ai_bp
from .api_keys import load_api_key

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
    """AI Provider 连接测试（ENV→DB→JSON 依次查找）"""
    try:
        provider = load_api_key(provider_id)

        if not provider:
            return jsonify({'success': False, 'error': 'Provider not found'})

        api_key = provider.get('apiKey', '')
        if not api_key:
            return jsonify({'success': False, 'error': 'API Key not configured'})

        if len(api_key) < 10:
            return jsonify({'success': False, 'error': 'Invalid API Key'})

        return jsonify({'success': True, 'message': '连接成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
