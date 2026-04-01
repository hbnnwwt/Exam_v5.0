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

def save_providers(providers):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(providers, f, ensure_ascii=False, indent=2)

@ai_bp.route('/config', methods=['GET'])
def get_providers():
    return jsonify(load_providers())

@ai_bp.route('/config', methods=['POST'])
def add_provider():
    providers = load_providers()
    data = request.json
    data['id'] = data.get('id') or f"custom_{len(providers)}"
    data['enabled'] = False
    providers.append(data)
    save_providers(providers)
    return jsonify(data)

@ai_bp.route('/config/<provider_id>', methods=['PUT'])
def update_provider(provider_id):
    providers = load_providers()
    for i, p in enumerate(providers):
        if p.get('id') == provider_id:
            providers[i].update(request.json)
            save_providers(providers)
            return jsonify(providers[i])
    return jsonify({'error': 'Provider not found'}), 404

@ai_bp.route('/config/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    providers = load_providers()
    providers = [p for p in providers if p.get('id') != provider_id]
    save_providers(providers)
    return jsonify({'success': True})