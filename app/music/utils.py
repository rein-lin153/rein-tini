# -*- coding: utf-8 -*-
"""
音乐模块 - 工具函数
"""

import os
import uuid
import logging
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from PIL import Image


logger = logging.getLogger(__name__)


def save_music_file(file, music_folder: str, max_size: int = 25 * 1024 * 1024) -> Tuple[Optional[str], Optional[str]]:
    """
    保存音乐文件
    
    Args:
        file: 上传的文件对象
        music_folder: 音乐文件夹路径
        max_size: 最大文件大小（字节）
    
    Returns:
        (filename, error_message) 元组
    """
    try:
        # 验证文件扩展名
        filename = secure_filename(file.filename)
        if not filename:
            return None, '无效的文件名'
        
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in ['mp3']:
            return None, f'不支持的音乐格式: {ext}（仅支持 MP3）'
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return None, f'文件过大（最大 {max_size // (1024 * 1024)}MB）'
        
        # 生成唯一文件名（避免覆盖）
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
        file_path = os.path.join(music_folder, unique_filename)
        
        # 确保目录存在
        os.makedirs(music_folder, exist_ok=True)
        
        # 保存文件（原子写入）
        temp_file = file_path + '.tmp'
        file.save(temp_file)
        
        # 验证文件大小
        if os.path.getsize(temp_file) > max_size:
            os.remove(temp_file)
            return None, f'文件过大（最大 {max_size // (1024 * 1024)}MB）'
        
        # 重命名（原子操作）
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        logger.info(f'音乐文件已保存: {unique_filename} ({file_size / (1024 * 1024):.2f} MB)')
        return unique_filename, None
    
    except Exception as e:
        logger.error(f'保存音乐文件失败: {str(e)}', exc_info=True)
        # 清理临时文件
        if 'temp_file' in locals() and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None, f'保存文件失败: {str(e)}'


def save_cover_file(file, cover_folder: str, music_filename: str, 
                   max_size: int = 2 * 1024 * 1024) -> Tuple[Optional[str], Optional[str]]:
    """
    保存封面文件
    
    Args:
        file: 上传的封面文件对象
        cover_folder: 封面文件夹路径
        music_filename: 对应的音乐文件名（用于生成封面文件名）
        max_size: 最大文件大小（字节）
    
    Returns:
        (cover_url, error_message) 元组
    """
    try:
        # 验证文件扩展名
        filename = secure_filename(file.filename)
        if not filename:
            return None, '无效的文件名'
        
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            return None, f'不支持的封面格式: {ext}（支持 JPG, PNG, WEBP）'
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return None, f'封面文件过大（最大 {max_size // (1024 * 1024)}MB）'
        
        # 使用音乐文件名作为封面文件名（去掉音乐扩展名）
        music_base_name = os.path.splitext(music_filename)[0]
        cover_filename = f'{music_base_name}.{ext}'
        file_path = os.path.join(cover_folder, cover_filename)
        
        # 确保目录存在
        os.makedirs(cover_folder, exist_ok=True)
        
        # 保存文件（原子写入）
        temp_file = file_path + '.tmp'
        file.save(temp_file)
        
        # 验证文件大小
        if os.path.getsize(temp_file) > max_size:
            os.remove(temp_file)
            return None, f'封面文件过大（最大 {max_size // (1024 * 1024)}MB）'
        
        # 尝试处理图片（验证并可能压缩）
        try:
            img = Image.open(temp_file)
            # 转换为 RGB（如果是 RGBA）
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            
            # 如果图片过大，压缩（最大 800x800）
            max_dimension = 800
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                img.save(temp_file, 'JPEG' if ext in ['jpg', 'jpeg'] else 'PNG', quality=85)
            
        except Exception as e:
            logger.warning(f'处理封面图片失败: {str(e)}，使用原始文件')
        
        # 重命名（原子操作）
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        cover_url = f'/static/music/covers/{cover_filename}'
        logger.info(f'封面文件已保存: {cover_filename} ({file_size / (1024 * 1024):.2f} MB)')
        return cover_url, None
    
    except Exception as e:
        logger.error(f'保存封面文件失败: {str(e)}', exc_info=True)
        # 清理临时文件
        if 'temp_file' in locals() and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None, f'保存封面失败: {str(e)}'


def validate_upload_token(token: str, expected_token: str) -> bool:
    """
    验证上传令牌
    
    Args:
        token: 提供的令牌
        expected_token: 期望的令牌
    
    Returns:
        是否有效
    """
    if not expected_token or expected_token == 'changeme123':
        logger.warning('使用默认上传令牌，生产环境请更改！')
    
    return token == expected_token

