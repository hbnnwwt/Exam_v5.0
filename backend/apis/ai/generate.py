import json
import os
import logging
import requests
from flask import jsonify, request
from . import ai_bp
from .api_keys import load_api_key

# 配置日志
logger = logging.getLogger(__name__)

def get_subject_name(subject_code):
    """根据科目代码获取科目名称"""
    if not subject_code:
        return ''
    try:
        from apis.common.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.execute('SELECT name FROM subjects WHERE code = ?', (subject_code,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row['name']
    except Exception as e:
        logger.warning(f"获取科目名称失败: {e}")
    return subject_code  # 如果查不到，返回原代码

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

    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result = response.json()
    # Find text content (skip thinking)
    for item in result.get('content', []):
        if item.get('type') == 'text':
            return item.get('text', '')
    return ''

def call_modelscope(provider_config, messages):
    """调用 ModelScope API (OpenAI 兼容格式)"""
    api_key = provider_config.get('apiKey')
    base_url = provider_config.get('baseUrl', 'https://api-inference.modelscope.cn')
    model = provider_config.get('defaultModel', 'qwen3.5-397b')

    # ModelScope 模型映射
    model_map = {
        'qwen-turbo': 'Qwen/Qwen3.5-397B-A17B',
        'qwen-plus': 'Qwen/Qwen3.5-397B-A17B',
        'qwen-max': 'Qwen/Qwen3.5-397B-A17B',
        'qwen3.5-397b': 'Qwen/Qwen3.5-397B-A17B',
        'qwen3.5-397b-instruct': 'Qwen/Qwen3.5-397B-A17B',
    }
    model_id = model_map.get(model, model)

    url = f"{base_url}/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 转换消息格式为 OpenAI 格式
    openai_messages = []
    for msg in messages:
        openai_messages.append({'role': msg['role'], 'content': msg['content']})

    data = {
        'model': model_id,
        'messages': openai_messages,
        'max_tokens': 1024,
        'temperature': 0.7
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result = response.json()
    # 提取生成的文本 (OpenAI 格式)
    if 'choices' in result and len(result['choices']) > 0:
        return result['choices'][0].get('message', {}).get('content', '')
    return ''

def call_openai_compatible(provider_config, messages):
    """调用 OpenAI 兼容格式 API"""
    api_key = provider_config.get('apiKey')
    base_url = provider_config.get('baseUrl', 'https://api.openai.com/v1')
    model = provider_config.get('defaultModel', 'gpt-4o')

    url = f"{base_url}/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 转换消息格式
    openai_messages = []
    for msg in messages:
        openai_messages.append({'role': msg['role'], 'content': msg['content']})

    data = {
        'model': model,
        'messages': openai_messages,
        'max_tokens': 1024,
        'temperature': 0.7
    }

    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result = response.json()
    # 提取生成的文本
    if 'choices' in result and len(result['choices']) > 0:
        return result['choices'][0].get('message', {}).get('content', '')
    return ''

def call_anthropic(provider_config, messages):
    """调用 Anthropic 兼容格式 API (Claude/MiniMax等)"""
    api_key = provider_config.get('apiKey')
    base_url = provider_config.get('baseUrl', 'https://api.anthropic.com')
    model = provider_config.get('defaultModel', 'claude-sonnet-4-20250514')

    url = f"{base_url}/v1/messages"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }

    # 转换消息格式
    claude_messages = []
    system_content = ''
    for msg in messages:
        if msg['role'] == 'system':
            system_content = msg['content']
        else:
            claude_messages.append({'role': msg['role'], 'content': msg['content']})

    data = {
        'model': model,
        'messages': claude_messages,
        'max_tokens': 1024
    }

    if system_content:
        data['system'] = system_content

    response = requests.post(url, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result = response.json()
    # Find text content
    for item in result.get('content', []):
        if item.get('type') == 'text':
            return item.get('text', '')
    return ''

@ai_bp.route('/generate', methods=['POST'])
def generate_question():
    """单题 AI 生成"""
    data = request.json
    provider_id = data.get('provider')
    question_type = data.get('type', 'professional')
    context = data.get('context', '')
    source_text = data.get('source_text', '')
    subject = data.get('subject', '')  # 获取科目代码
    subject_name = get_subject_name(subject)  # 转换为科目名称

    provider = load_api_key(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not configured'}), 400

    # 构建 messages（根据题型不同，优先使用 source_text 作为参考）
    if source_text:
        # 如果提供了参考内容，基于它生成变体
        # 检测是否包含多套题目（通过换行和题目编号判断）
        has_multiple_questions = '题目1' in source_text or '题目2' in source_text or source_text.count('\n') > 0
        
        if question_type == 'translation':
            if has_multiple_questions:
                prompt = f"""请基于以下参考内容，生成3组难度递进的英文段落：
参考内容：
{source_text}

要求：
1. 生成3组段落，难度递进：基础组 -> 进阶组 -> 挑战组
2. 每组包含与参考内容相同数量的段落
3. 组与组之间用"---"分隔
4. 直接输出段落内容，不要带标签

格式示例：
基础段落1
基础段落2
---
进阶段落1
进阶段落2
---
挑战段落1
挑战段落2

请生成3组难度递进的英文段落："""
            else:
                prompt = f"""请基于以下参考内容，生成3个难度递进的英文段落：
参考内容：{source_text}

要求：
1. 生成3个段落，难度递进：基础 -> 进阶 -> 挑战
2. 第1个段落使用简单词汇和句式
3. 第2个段落使用专业术语和复合句
4. 第3个段落使用复杂长句和深入表达
5. 直接输出3个段落，每行一个
6. 不要中文翻译

请生成3个难度递进的英文段落："""
        else:
            # 专业题，加入科目信息
            subject_info = f"【科目：{subject_name}】" if subject_name else ""
            
            if has_multiple_questions:
                prompt = f"""请基于以下参考内容，生成3组难度递进的专业题目：
{subject_info}
参考内容：
{source_text}

要求：
1. 生成3组题目，组间难度递进：基础组 -> 应用组 -> 综合组
2. 每组包含与参考内容相同数量的题目
3. 组与组之间用"---"分隔
4. 直接输出题目内容，不要带"基础组"等标签

格式示例：
基础概念题目1
基础概念题目2
---
应用分析题目1
应用分析题目2
---
深度综合题目1
深度综合题目2

请生成3组难度递进的专业题："""
            else:
                prompt = f"""请基于以下参考内容，生成3道差异明显的专业题目：
{subject_info}
参考内容：{source_text}
科目：{subject_name if subject_name else context}

【重要】必须生成3道差异显著的题目，难度递进：
- 第1道（基础）：考察基本概念和定义，难度较低
- 第2道（应用）：考察实际应用和分析能力，难度中等  
- 第3道（综合）：考察深入理解和综合运用，难度较高

要求：
1. 3道题目必须是不同难度层次，不能都是同一类型
2. 第1道侧重"是什么"，第2道侧重"为什么/怎么用"，第3道侧重"深入分析/综合运用"
3. 每道题目要清晰、有针对性，适合研究生复试
4. 直接输出3道题目，每行一个，不要带"题目1："等前缀
5. 必须生成3道真正差异显著的题目

请生成3道难度递进的专业题："""
    else:
        # 文本框为空，使用 context 作为主题
        if question_type == 'translation':
            prompt = f"""请生成3个关于{context}的英文段落，难度递进。

要求：
1. 第1个段落：基础难度，简单词汇和句式
2. 第2个段落：进阶难度，专业术语和复合句
3. 第3个段落：挑战难度，复杂长句和深入表达
4. 每个段落2-4句话，内容专业
5. 直接输出3个段落，每行一个
6. 不要中文翻译

请生成3个难度递进的英文段落："""
        else:
            # 专业题，加入科目信息
            subject_info = f"【科目：{subject_name}】" if subject_name else ""
            prompt = f"""请生成3道关于{context}的专业题目。
{subject_info}

要求生成3道难度递进的题目：
1. 基础题：考察基本概念（是什么）
2. 应用题：考察实际应用（怎么用）
3. 综合题：考察深入分析（为什么/如何优化）

要求：
1. 3道题目必须是不同难度，覆盖基础到深入
2. 每道题目清晰、有针对性，适合研究生复试
3. 直接输出3道题目，每行一个，不要带编号前缀

请生成3道难度递进的专业题："""

    messages = [{'role': 'user', 'content': prompt}]

    # 根据 provider 类型调用不同 API
    if provider_id == 'minimax' or 'minimax' in provider.get('baseUrl', ''):
        try:
            result = call_minimax(provider, messages)
            if result:
                candidates = [s.strip() for s in result.split('\n') if s.strip()]
                return jsonify({'candidates': candidates[:3]})
        except Exception as e:
            logger.warning(f"MiniMax API error: {e}")
            pass

    # ModelScope API
    if provider_id == 'modelscope' or 'modelscope' in provider.get('baseUrl', '') or 'modelscope.cn' in provider.get('baseUrl', ''):
        try:
            result = call_modelscope(provider, messages)
            if result:
                candidates = [s.strip() for s in result.split('\n') if s.strip()]
                return jsonify({'candidates': candidates[:3]})
        except Exception as e:
            logger.warning(f"ModelScope API error: {e}")
            pass

    # 硅基流动 API (OpenAI 兼容格式)
    if provider_id == 'siliconflow' or 'siliconflow' in provider.get('baseUrl', ''):
        try:
            result = call_openai_compatible(provider, messages)
            if result:
                candidates = [s.strip() for s in result.split('\n') if s.strip()]
                return jsonify({'candidates': candidates[:3]})
        except Exception as e:
            logger.warning(f"SiliconFlow API error: {e}")
            pass

    # Anthropic/Claude API (内置 provider 或自定义 provider 明确指定 anthropic 格式)
    api_format = provider.get('apiFormat', 'openai')
    if provider_id in ['claude', 'anthropic'] or 'anthropic' in provider.get('baseUrl', '') or api_format == 'anthropic':
        try:
            result = call_anthropic(provider, messages)
            if result:
                candidates = [s.strip() for s in result.split('\n') if s.strip()]
                return jsonify({'candidates': candidates[:3]})
        except Exception as e:
            logger.warning(f"Anthropic API error: {e}")
            pass

    # OpenAI 兼容 API (默认)
    try:
        result = call_openai_compatible(provider, messages)
        if result:
            candidates = [s.strip() for s in result.split('\n') if s.strip()]
            return jsonify({'candidates': candidates[:3]})
    except Exception as e:
        logger.warning(f"OpenAI API error: {e}")

    # 失败时返回模拟候选（确保3个）
    if question_type == 'translation':
        candidates = [
            f"The rapid development of artificial intelligence has brought unprecedented changes to various industries.",
            f"Machine learning algorithms are transforming the way we process and analyze large-scale data.",
            f"Cloud computing technology enables enterprises to deploy applications more flexibly and efficiently."
        ]
    else:
        subject_info = f"【{subject_name}】" if subject_name else ""
        candidates = [
            f"{subject_info}请简述 {context} 的基本概念及核心特点。",
            f"{subject_info}解释 {context} 的工作原理，并说明其在实际应用中的优势。",
            f"{subject_info}分析 {context} 的应用场景，并举例说明其在行业中的具体应用。"
        ]

    return jsonify({'candidates': candidates[:3]})

@ai_bp.route('/batch-generate', methods=['POST'])
def batch_generate():
    """批量 AI 生成"""
    data = request.json
    provider_id = data.get('provider')
    question_type = data.get('type', 'professional')
    knowledge = data.get('knowledge', '')
    count = data.get('count', 5)
    questions_per_set = data.get('questionsPerSet', 1)

    provider = load_api_key(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not configured'}), 400

    # 解析知识点
    topics = [k.strip() for k in knowledge.split(',') if k.strip()]
    if not topics:
        topics = ['计算机基础']

    # 构建 AI 提示词（根据题型不同）
    if questions_per_set > 1:
        # 套题模式
        if question_type == 'translation':
            prompt = f"""请生成 {count} 套翻译题，每套包含 {questions_per_set} 个英文段落。

要求：
1. 内容涉及以下主题：{', '.join(topics)}
2. 每个段落应该是完整的英文，长度适中（2-4句话）
3. 内容要有专业性，适合研究生水平的翻译练习
4. 直接输出英文内容，不要包含中文翻译

重要：使用 "---" 分隔不同的套题，每套内的 {questions_per_set} 个段落各占一行。

格式示例（每套{questions_per_set}个段落）：
The first paragraph content here...
The second paragraph content here...
---
The first paragraph of next set...
The second paragraph of next set...
---
...

请生成 {count} 套英文段落（每套{questions_per_set}个）："""
        else:
            prompt = f"""请生成 {count} 套专业题目，每套包含 {questions_per_set} 道小题。

要求：
1. 题目涉及以下知识点：{', '.join(topics)}
2. 每道题目都要有具体的题目内容，不能是占位符
3. 题目要清晰、有针对性，适合研究生复试
4. 每套题目围绕相同或相关知识点展开

重要：使用 "---" 分隔不同的套题，每套内的 {questions_per_set} 道小题各占一行。

格式示例（每套{questions_per_set}道题）：
请解释TCP协议的三次握手过程及其作用。
TCP和UDP协议的主要区别是什么？
---
什么是操作系统的进程调度？
进程和线程有什么区别？
---
...

请生成 {count} 套专业题目（每套{questions_per_set}道）："""
    else:
        # 单题模式
        if question_type == 'translation':
            prompt = f"""请生成 {count} 个英文段落或句子用于翻译练习，要求：
1. 内容涉及以下主题：{', '.join(topics)}
2. 每个段落或句子应该是完整的英文内容，长度适中（2-4句话）
3. 内容要有专业性，适合研究生水平的翻译练习
4. 直接输出英文内容，每行一个段落/句子，不要有编号或其他格式
5. 不要包含中文翻译，只输出英文原文

请生成英文段落："""
        else:
            prompt = f"""请生成 {count} 道专业题目，要求：
1. 题目涉及以下知识点：{', '.join(topics)}
2. 每道题目都要有具体的题目内容，不能是占位符
3. 题目要清晰、有针对性，适合研究生复试
4. 直接输出题目列表，每行一个题目，不要有编号或其他格式

请生成具体的题目内容："""

    # 调用 AI API
    messages = [{'role': 'user', 'content': prompt}]

    try:
        # 根据 provider 类型调用不同 API
        api_format = provider.get('apiFormat', 'openai')
        if provider_id == 'minimax' or 'minimax' in provider.get('baseUrl', ''):
            result = call_minimax(provider, messages)
        elif provider_id == 'modelscope' or 'modelscope' in provider.get('baseUrl', '') or 'modelscope.cn' in provider.get('baseUrl', ''):
            result = call_modelscope(provider, messages)
        elif provider_id == 'siliconflow' or 'siliconflow' in provider.get('baseUrl', ''):
            # 硅基流动使用 OpenAI 兼容格式
            result = call_openai_compatible(provider, messages)
        elif provider_id in ['claude', 'anthropic'] or 'anthropic' in provider.get('baseUrl', '') or api_format == 'anthropic':
            result = call_anthropic(provider, messages)
        else:
            # 默认使用 OpenAI 格式
            result = call_openai_compatible(provider, messages)

        # 解析返回的题目
        questions = []
        if result:
            if questions_per_set > 1:
                # 套题模式：按 --- 分隔多套题目
                # 先清理结果，移除常见的 Markdown 代码块标记
                cleaned_result = result.replace('```', '').strip()
                sets = cleaned_result.split('---')
                logger.debug(f"解析套题：找到 {len(sets)} 个分隔段，需要 {count} 套")
                
                for i, set_content in enumerate(sets[:count]):
                    set_content = set_content.strip()
                    if not set_content:
                        logger.debug(f"套题 {i+1} 内容为空，跳过")
                        continue
                    
                    logger.debug(f"解析套题 {i+1}，内容长度: {len(set_content)}")
                    
                    # 解析每套题的子题
                    sub_questions = []
                    lines = [line.strip() for line in set_content.split('\n') if line.strip()]
                    logger.debug(f"套题 {i+1} 找到 {len(lines)} 行内容")
                    
                    for line in lines:
                        # 跳过空行和分隔线
                        if not line or line == '---' or set(line) <= {'-', '=', '*'}:
                            continue
                            
                        # 移除行号 (1. 1、 1) 等
                        question_text = line
                        for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.',
                                       '1、', '2、', '3、', '4、', '5、', '6、', '7、', '8、', '9、', '0、',
                                       '(1)', '(2)', '(3)', '(4)', '(5)', '(6)', '(7)', '(8)', '(9)', '(0)',
                                       '题目1', '题目2', '题目3', '题目4', '题目5',
                                       '-', '*', '•']:
                            if question_text.startswith(prefix):
                                question_text = question_text[len(prefix):].strip()
                                break
                        
                        # 移除 "题目：" 等前缀
                        for prefix in ['题目：', '题目:', '题：', '题:', 'Q:', 'Q：']:
                            if question_text.startswith(prefix):
                                question_text = question_text[len(prefix):].strip()
                                break
                                
                        if question_text and len(question_text) > 5:  # 至少5个字符才算有效题目
                            sub_questions.append(question_text)
                            logger.debug(f"  添加子题: {question_text[:30]}...")
                            if len(sub_questions) >= questions_per_set:
                                break
                    
                    # 补充子题到指定数量
                    while len(sub_questions) < questions_per_set:
                        topic = topics[len(questions) % len(topics)]
                        sub_questions.append(f"请简述 {topic} 的基本概念。")
                        logger.debug(f"  补充默认子题")
                    
                    # 只取前 questions_per_set 个子题
                    sub_questions = sub_questions[:questions_per_set]
                    
                    # 构建套题格式
                    questions.append({
                        'id': i + 1,
                        'question': sub_questions,  # 数组格式表示套题
                        'answer': f"{topics[i % len(topics)]} 的参考答案",
                        'difficulty': 'medium',
                        'subject': topics[i % len(topics)],
                        'is_set': True
                    })
                    logger.debug(f"套题 {i+1} 解析完成，共 {len(sub_questions)} 道子题")
            else:
                # 单题模式：每行一题
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                for i, line in enumerate(lines[:count]):
                    # 移除行号
                    question_text = line
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.',
                                   '1、', '2、', '3、', '4、', '5、', '6、', '7、', '8、', '9、', '0、',
                                   '-', '*', '•']:
                        if question_text.startswith(prefix):
                            question_text = question_text[len(prefix):].strip()
                            break

                    questions.append({
                        'id': i + 1,
                        'question': question_text,
                        'answer': f"{topics[i % len(topics)]} 的参考答案",
                        'difficulty': 'medium',
                        'subject': topics[i % len(topics)]
                    })

        # 如果 AI 没有返回足够题目，补充一些
        while len(questions) < count:
            i = len(questions)
            topic = topics[i % len(topics)]
            if questions_per_set > 1:
                # 补充套题
                sub_questions = [f"请简述 {topic} 的基本概念和应用场景。" for _ in range(questions_per_set)]
                questions.append({
                    'id': i + 1,
                    'question': sub_questions,
                    'answer': f"{topic} 的参考答案",
                    'difficulty': 'medium',
                    'subject': topic,
                    'is_set': True
                })
            else:
                questions.append({
                    'id': i + 1,
                    'question': f"请简述 {topic} 的基本概念和应用场景。",
                    'answer': f"{topic} 的参考答案",
                    'difficulty': 'medium',
                    'subject': topic
                })

        return jsonify({'questions': questions})

    except Exception as e:
        logger.error(f"AI 批量生成失败: {e}", exc_info=True)
        # 失败时返回模拟数据
        questions = []
        for i in range(count):
            topic = topics[i % len(topics)]
            if questions_per_set > 1:
                # 失败时返回套题格式的模拟数据
                sub_questions = [f"关于 {topic} 的问题 {i+1}-{j+1}" for j in range(questions_per_set)]
                questions.append({
                    'id': i + 1,
                    'question': sub_questions,
                    'answer': f"{topic} 的参考答案",
                    'difficulty': 'medium',
                    'subject': topic,
                    'is_set': True
                })
            else:
                questions.append({
                    'id': i + 1,
                    'question': f"关于 {topic} 的问题 {i+1}",
                    'answer': f"{topic} 的参考答案",
                    'difficulty': 'medium',
                    'subject': topic
                })
        return jsonify({'questions': questions})