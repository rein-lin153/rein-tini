# -*- coding: utf-8 -*-
"""
图片处理工具
包括图片上传、压缩、缩略图生成
"""

import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """
    检查文件扩展名是否允许
    
    Args:
        filename: 文件名
    
    Returns:
        bool
    """
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def generate_unique_filename(original_filename):
    """
    生成唯一的文件名
    
    Args:
        original_filename: 原始文件名
    
    Returns:
        新的唯一文件名
    """
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_name = '{}.{}'.format(uuid.uuid4().hex, ext)
    return unique_name


def validate_image(file_path):
    """
    验证是否为有效的图片文件（检查 magic bytes）
    
    Args:
        file_path: 文件路径
    
    Returns:
        bool
    """
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except Exception:
        return False


def compress_image(input_path, output_path, max_width=None, quality=75):
    """
    压缩图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        max_width: 最大宽度（None 表示不限制）
        quality: JPEG 质量（1-100）
    
    Returns:
        字典包含 width、height、file_size
    """
    try:
        img = Image.open(input_path)
        
        # 转换 RGBA 到 RGB（PNG 透明背景）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # 调整尺寸
        if max_width and img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        
        # 保存压缩后的图片
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        # 获取文件信息
        file_size = os.path.getsize(output_path)
        
        return {
            'width': img.width,
            'height': img.height,
            'file_size': file_size
        }
    
    except Exception as e:
        raise ValueError('图片处理失败: {}'.format(str(e)))


def create_thumbnail(input_path, output_path, thumb_width=300):
    """
    创建缩略图
    
    Args:
        input_path: 输入图片路径
        output_path: 输出缩略图路径
        thumb_width: 缩略图宽度
    
    Returns:
        bool
    """
    try:
        img = Image.open(input_path)
        
        # 转换模式
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # 计算缩略图尺寸
        ratio = thumb_width / float(img.width)
        thumb_height = int(img.height * ratio)
        
        # 生成缩略图
        img.thumbnail((thumb_width, thumb_height), Image.LANCZOS)
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        
        return True
    
    except Exception as e:
        raise ValueError('缩略图生成失败: {}'.format(str(e)))


def save_uploaded_photo(file):
    """
    保存上传的照片（包括原图和缩略图）
    
    Args:
        file: Werkzeug FileStorage 对象
    
    Returns:
        字典包含 filename、thumb_filename、width、height、file_size
    """
    if not file or file.filename == '':
        raise ValueError('未选择文件')
    
    if not allowed_file(file.filename):
        raise ValueError('不支持的文件格式')
    
    # 生成唯一文件名
    original_filename = secure_filename(file.filename)
    unique_filename = generate_unique_filename(original_filename)
    thumb_filename = 'thumb_' + unique_filename
    
    # 文件路径
    photos_folder = current_app.config['PHOTOS_FOLDER']
    thumbs_folder = current_app.config['THUMBS_FOLDER']
    
    temp_path = os.path.join(photos_folder, 'temp_' + unique_filename)
    photo_path = os.path.join(photos_folder, unique_filename)
    thumb_path = os.path.join(thumbs_folder, thumb_filename)
    
    try:
        # 保存临时文件
        file.save(temp_path)
        
        # 验证图片
        if not validate_image(temp_path):
            os.remove(temp_path)
            raise ValueError('无效的图片文件')
        
        # 压缩并保存原图
        max_width = current_app.config['MAX_IMAGE_WIDTH']
        quality = current_app.config['JPEG_QUALITY']
        image_info = compress_image(temp_path, photo_path, max_width=max_width, quality=quality)
        
        # 生成缩略图
        thumb_width = current_app.config['THUMBNAIL_WIDTH']
        create_thumbnail(photo_path, thumb_path, thumb_width=thumb_width)
        
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            'filename': unique_filename,
            'thumb_filename': thumb_filename,
            'width': image_info['width'],
            'height': image_info['height'],
            'file_size': image_info['file_size']
        }
    
    except Exception as e:
        # 清理文件
        for path in [temp_path, photo_path, thumb_path]:
            if os.path.exists(path):
                os.remove(path)
        raise e


def delete_photo_files(filename, thumb_filename):
    """
    删除照片文件（原图和缩略图）
    
    Args:
        filename: 原图文件名
        thumb_filename: 缩略图文件名
    """
    photos_folder = current_app.config['PHOTOS_FOLDER']
    thumbs_folder = current_app.config['THUMBS_FOLDER']
    
    photo_path = os.path.join(photos_folder, filename)
    thumb_path = os.path.join(thumbs_folder, thumb_filename)
    
    for path in [photo_path, thumb_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                current_app.logger.error('删除文件失败: {}'.format(str(e)))

