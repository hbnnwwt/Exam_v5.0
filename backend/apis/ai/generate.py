import json
import os
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