#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
研究生复试系统 - Flask 后端入口
"""

import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, request
from flask_cors import CORS

# 添加项目路径
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
current_dir = str(backend_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 初始化日志（在导入其他模块之前）
from apis.common.logger import logger
from config import get_config

# 创建 Flask 应用
app = Flask(__name__, static_folder=str(backend_dir / 'assets'), static_url_path='/backend-assets')
app.config.from_object(get_config())

# 启用 CORS（开发环境）
if app.config['DEBUG']:
    CORS(app)

# 注册错误处理器
from apis.common.errors import register_error_handlers
register_error_handlers(app)

# 添加全局错误处理器来记录系统错误
@app.errorhandler(Exception)
def handle_global_exception(e):
    """全局异常处理器，记录错误到日志"""
    import traceback
    print(f"[GLOBAL ERROR] {str(e)}")
    print(traceback.format_exc())
    logger.error(
        f"Unhandled Exception: {str(e)} - "
        f"Path: {request.path} - "
        f"Method: {request.method} - "
        f"IP: {request.remote_addr}",
        exc_info=True
    )
    return {'success': False, 'error': '服务器内部错误'}, 500

@app.before_request
def log_request_info():
    """记录每个请求到日志"""
    logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")

# 数据库路径
DATABASE = app.config['DATABASE']

def get_db_connection():
    """获取数据库连接"""
    import sqlite3
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 导入子模块以注册路由（必须在蓝图注册前导入！）
try:
    from apis.exam import students
    print("OK - students module loaded")
except Exception as e:
    print(f"FAIL - students module load failed: {e}")

try:
    from apis.exam import questions
    print("OK - questions module loaded")
except Exception as e:
    print(f"FAIL - questions module load failed: {e}")

try:
    from apis.exam import exam_flow
    print("OK - exam_flow module loaded")
except Exception as e:
    print(f"FAIL - exam_flow module load failed: {e}")

# 注册 API 蓝图
try:
    from apis.exam import exam_bp
    app.register_blueprint(exam_bp, url_prefix='/exam-api')
    print("OK - exam API registered")
except ImportError as e:
    print(f"FAIL - exam API registration failed: {e}")

try:
    from apis.editor import editor_bp
    app.register_blueprint(editor_bp, url_prefix='/api')
    print("OK - editor API registered")
except ImportError as e:
    print(f"FAIL - editor API registration failed: {e}")

try:
    from apis.exam.export import export_bp
    app.register_blueprint(export_bp, url_prefix='/export-api')
    print("OK - export API registered")
except ImportError as e:
    print(f"FAIL - export API registration failed: {e}")

# 注册认证蓝图
try:
    from apis.common.auth import get_authBlueprint
    auth_bp = get_authBlueprint()
    app.register_blueprint(auth_bp)
    print("OK - auth API registered")
except ImportError as e:
    print(f"FAIL - auth API registration failed: {e}")

# 注册 AI 蓝图
try:
    from apis.ai import ai_bp
    app.register_blueprint(ai_bp)
    print("OK - AI API registered")
except ImportError as e:
    print(f"FAIL - AI API registration failed: {e}")

# 注册备份管理蓝图
try:
    from apis.common.backup import get_backup_blueprint
    backup_bp = get_backup_blueprint()
    app.register_blueprint(backup_bp)
    print("OK - backup API registered")
except ImportError as e:
    print(f"FAIL - backup API registration failed: {e}")

# 图片上传目录静态文件服务
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    """服务上传的图片"""
    from pathlib import Path
    uploads_path = str(Path(current_dir) / 'static' / 'uploads')
    return send_from_directory(uploads_path, filename)

# 帮助文档截图
@app.route('/docs/<path:filename>')
def serve_docs(filename):
    """服务帮助文档截图"""
    from pathlib import Path
    docs_path = str(Path(current_dir).parent / 'docs')
    return send_from_directory(docs_path, filename)

# 后端静态资源（图片、Logo、数据等）
@app.route('/backend-assets/<path:filename>')
def serve_backend_assets(filename):
    """服务后端静态资源"""
    import os
    import glob

    # Get backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    # Split the path and search in the last directory
    parts = filename.replace('\\', '/').split('/')
    if len(parts) >= 2:
        dir_part = os.path.join(backend_dir, 'assets', *parts[:-1])
        file_part = parts[-1]
    else:
        dir_part = os.path.join(backend_dir, 'assets')
        file_part = filename

    # Use glob to find file (works around Git Bash path issues)
    search_pattern = os.path.join(dir_part, file_part + '*')
    matches = glob.glob(search_pattern)

    if not matches:
        return {'error': 'File not found'}, 404

    file_path = matches[0]

    # Determine content type
    import mimetypes
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    # Read and return file content directly
    with open(file_path, 'rb') as f:
        content = f.read()

    from flask import Response
    return Response(content, mimetype=content_type)

# 前端构建的静态资源（CSS、JS等）
@app.route('/assets/<path:filename>')
def serve_frontend_assets(filename):
    """服务前端构建的静态资源"""
    from pathlib import Path
    frontend_assets_path = str(Path(current_dir) / 'assets' / 'frontend' / 'assets')
    if (Path(frontend_assets_path) / filename).exists():
        return send_from_directory(frontend_assets_path, filename)
    # 如果前端资源不存在，返回后端资源
    backend_assets_path = str(Path(current_dir) / 'assets')
    return send_from_directory(backend_assets_path, filename)

# 前端页面服务（生产环境）
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """服务前端页面"""
    from pathlib import Path
    # 如果是 API 请求或docs，跳过
    if path.startswith(('exam-api', 'api', 'export-api', 'docs')):
        return {'error': 'Not found'}, 404

    # 生产环境：返回前端构建文件
    frontend_path = Path(current_dir) / 'assets' / 'frontend'
    if frontend_path.exists():
        if path and (frontend_path / path).exists():
            return send_from_directory(str(frontend_path), path)
        return send_from_directory(str(frontend_path), 'index.html')

    return {'message': 'Frontend not built. Run: cd frontend && npm run build'}, 404

if __name__ == '__main__':
    print("=" * 40)
    print("Backend for Graduate Interview System")
    print(f"Environment: {'Development' if app.config['DEBUG'] else 'Production'}")
    print(f"URL: http://localhost:5000")
    print("=" * 40)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
