import json
import os
import requests
from flask import jsonify, request
from . import ai_bp

CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'ai_providers.json')

def load_providers():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_provider_config(provider_id):
    providers = load_providers()
    for p in providers:
        if p.get('id') == provider_id:
            return p
    return None

def call_minimax(provider_config, messages):
    """调用 MiniMax API"""
    api_key = provider_config.get('apiKey')
    base_url = provider_config.get('baseUrl', 'https://api.minimaxi.com/anthropic')
    model = provider_config.get('defaultModel', 'MiniMax-M2.7')

    url = f"{base_url}/v1/messages"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }

    # 转换 messages 格式
    claude_messages = []
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'assistant'
        claude_messages.append({'role': role, 'content': msg['content']})

    data = {
        'model': model,
        'messages': claude_messages,
        'max_tokens': 1024
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()

    result = response.json()
    return result['content'][0]['text']

@ai_bp.route('/generate', methods=['POST'])
def generate_question():
    """单题 AI 生成"""
    data = request.json
    provider_id = data.get('provider')
    question_type = data.get('type', 'professional')
    context = data.get('context', '')
    source_text = data.get('source_text', '')

    provider = get_provider_config(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not configured'}), 400

    # 构建 messages
    messages = [
        {'role': 'user', 'content': f'请生成一道关于{context}的题目，题型：{question_type}'}
    ]

    # 根据 provider 类型调用不同 API
    if provider_id == 'minimax' or 'minimax' in provider.get('baseUrl', ''):
        try:
            result = call_minimax(provider, messages)
            candidates = [s.strip() for s in result.split('\n') if s.strip()]
            return jsonify({'candidates': candidates[:3]})
        except Exception as e:
            return jsonify({'error': f'MiniMax API 调用失败: {str(e)}'}), 500

    # 简化实现：根据类型返回模拟候选
    if question_type == 'translation':
        candidates = [
            f"人工智能的快速发展给各行各业带来了前所未有的变革。",
            f"人工智能的飞速发展已经为各行业带来了空前的改变。"
        ]
    else:
        candidates = [
            f"请简述 {context} 的基本概念。",
            f"解释 {context} 的工作原理。",
            f"分析 {context} 的应用场景。"
        ]

    return jsonify({'candidates': candidates})

@ai_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    """批量 AI 生成"""
    data = request.json
    provider_id = data.get('provider')
    question_type = data.get('type', 'professional')
    knowledge = data.get('knowledge', '')
    count = data.get('count', 10)

    provider = get_provider_config(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not configured'}), 400

    # 解析知识点
    topics = [k.strip() for k in knowledge.split(',') if k.strip()]
    if not topics:
        topics = ['计算机基础']

    # 生成模拟题目
    questions = []
    for i in range(count):
        topic = topics[i % len(topics)]
        q_type = '翻译题' if question_type == 'translation' else '专业题'
        questions.append({
            'id': i + 1,
            'question': f"{q_type} {i+1}: 关于 {topic} 的问题",
            'answer': f"{topic} 的参考答案",
            'difficulty': 'medium',
            'subject': topic
        })

    return jsonify({'questions': questions})