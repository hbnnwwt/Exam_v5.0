"""
API模块包 - 统一管理所有API接口
"""

from .exam import exam_bp
from .editor import editor_bp

__all__ = ['exam_bp', 'editor_bp']
