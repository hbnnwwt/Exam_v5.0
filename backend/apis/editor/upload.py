"""
图片上传模块
"""

import os
import time
from flask import Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from ..common.utils import format_response

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads')
THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(source_path, target_path):
    image = Image.open(source_path)
    image.thumbnail((320, 320), Image.Resampling.LANCZOS)
    ext = os.path.splitext(target_path)[1].lower()
    save_format_map = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.gif': 'GIF',
        '.webp': 'WEBP',
        '.bmp': 'BMP'
    }
    save_format = save_format_map.get(ext, 'JPEG')
    if ext in ['.jpg', '.jpeg'] and image.mode in ['RGBA', 'LA', 'P']:
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode in ['RGBA', 'LA']:
            background.paste(image, mask=image.split()[-1])
        else:
            background.paste(image.convert('RGBA'), mask=image.convert('RGBA').split()[-1])
        image = background
    if save_format == 'JPEG' and image.mode in ['RGBA', 'LA', 'P']:
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode in ['RGBA', 'LA']:
            background.paste(image, mask=image.split()[-1])
        else:
            rgba = image.convert('RGBA')
            background.paste(rgba, mask=rgba.split()[-1])
        image = background
    image.save(target_path, format=save_format, optimize=True, quality=80)


@upload_bp.route('/image', methods=['POST'])
def upload_image():
    """上传图片"""
    try:
        if 'file' not in request.files:
            return format_response(
                success=False,
                error='请选择要上传的文件',
                status_code=400
            )

        file = request.files['file']

        if file.filename == '':
            return format_response(
                success=False,
                error='请选择要上传的文件',
                status_code=400
            )

        if not allowed_file(file.filename):
            return format_response(
                success=False,
                error=f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}',
                status_code=400
            )

        # 检查文件大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return format_response(
                success=False,
                error='文件大小超过限制（最大5MB）',
                status_code=400
            )

        filename = secure_filename(file.filename)
        origin_name, origin_ext = os.path.splitext(file.filename)
        timestamp = int(time.time() * 1000)
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = origin_ext.lower()
        if not name:
            name = 'image'
        filename = f"{name}_{timestamp}{ext}"

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        thumbnail_filepath = os.path.join(THUMBNAIL_FOLDER, filename)
        create_thumbnail(filepath, thumbnail_filepath)

        path = f"/uploads/{filename}"
        thumbnail_path = f"/uploads/thumbs/{filename}"

        return format_response(
            success=True,
            data={'path': path, 'thumbnail': thumbnail_path},
            message='图片上传成功'
        )

    except Exception as e:
        return format_response(
            success=False,
            error=f'图片上传失败: {str(e)}',
            status_code=500
        )


@upload_bp.route('/image', methods=['DELETE'])
def delete_image():
    """删除图片"""
    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return format_response(
                success=False,
                error='请提供图片路径',
                status_code=400
            )

        path = data['path']
        # 移除前导斜杠
        path = path.lstrip('/')

        # 安全检查：只允许删除 uploads 目录下的文件
        if not path.startswith('uploads/') or '..' in path or path.startswith('/'):
            return format_response(
                success=False,
                error='无效的文件路径',
                status_code=400
            )

        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', path)

        if os.path.exists(filepath):
            os.remove(filepath)
            if path.startswith('uploads/') and not path.startswith('uploads/thumbs/'):
                thumbnail_path = os.path.join(THUMBNAIL_FOLDER, os.path.basename(path))
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            return format_response(
                success=True,
                message='图片删除成功'
            )
        else:
            return format_response(
                success=False,
                error='文件不存在',
                status_code=404
            )

    except Exception as e:
        return format_response(
            success=False,
            error=f'图片删除失败: {str(e)}',
            status_code=500
        )


@upload_bp.route('/<path:filename>', methods=['GET'])
def get_image(filename):
    """获取图片"""
    return send_from_directory(UPLOAD_FOLDER, filename)
