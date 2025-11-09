# -*- coding: utf-8 -*-
"""
音乐模块 - 工具函数
"""

import os
import uuid
import logging
import time
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from PIL import Image


logger = logging.getLogger(__name__)

# 确保 logger 已配置
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def save_music_file(file, music_folder: str, max_size: int = 30 * 1024 * 1024) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    保存音乐文件（原子写入）
    
    Args:
        file: 上传的文件对象
        music_folder: 音乐文件夹路径
        max_size: 最大文件大小（字节）
    
    Returns:
        (filename, error_message, file_size) 元组
    """
    temp_file = None
    try:
        # 验证文件扩展名
        original_filename = file.filename
        if not original_filename:
            return None, '无效的文件名', None
        
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if ext not in ['mp3']:
            return None, f'不支持的音乐格式: {ext}（仅支持 MP3）', None
        
        # 验证 MIME 类型
        file.seek(0)
        header = file.read(3)
        file.seek(0)
        
        # MP3 文件通常以 ID3 标签开始（'ID3'）或 MP3 帧同步字开始（0xFF 0xFB 或 0xFF 0xF3）
        if not (header.startswith(b'ID3') or header[0] == 0xFF and header[1] in [0xFB, 0xF3, 0xF2, 0xFA]):
            # 允许通过，因为某些 MP3 文件可能没有 ID3 标签
            logger.warning(f'文件 {original_filename} 可能不是有效的 MP3 文件，但允许上传')
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return None, f'文件过大（最大 {max_size // (1024 * 1024)}MB）', None
        
        # 生成安全文件名（时间戳 + UUID + 原始文件名）
        timestamp = int(time.time())
        safe_name = secure_filename(original_filename)
        name, ext = os.path.splitext(safe_name)
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{name}{ext}"
        file_path = os.path.join(music_folder, unique_filename)
        
        # 确保目录存在
        os.makedirs(music_folder, exist_ok=True)
        
        # 原子写入：先写到临时文件
        temp_file = file_path + '.tmp'
        file.save(temp_file)
        
        # 再次验证文件大小
        actual_size = os.path.getsize(temp_file)
        if actual_size > max_size:
            os.remove(temp_file)
            return None, f'文件过大（最大 {max_size // (1024 * 1024)}MB）', None
        
        # 原子操作：重命名临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        os.replace(temp_file, file_path)
        temp_file = None  # 标记已成功，不需要清理
        
        logger.info(f'音乐文件已保存: {unique_filename} ({actual_size / (1024 * 1024):.2f} MB)')
        return unique_filename, None, actual_size
    
    except Exception as e:
        logger.error(f'保存音乐文件失败: {str(e)}', exc_info=True)
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None, f'保存文件失败: {str(e)}', None


def save_cover_file(file, cover_folder: str, music_filename: str = None,
                   max_size: int = 2 * 1024 * 1024) -> Tuple[Optional[str], Optional[str]]:
    """
    保存封面文件（原子写入）
    
    Args:
        file: 上传的封面文件对象
        cover_folder: 封面文件夹路径
        music_filename: 对应的音乐文件名（可选，用于生成封面文件名）
        max_size: 最大文件大小（字节）
    
    Returns:
        (cover_url, error_message) 元组
    """
    temp_file = None
    try:
        # 验证文件扩展名
        original_filename = file.filename
        if not original_filename:
            return None, '无效的文件名'
        
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            return None, f'不支持的封面格式: {ext}（支持 JPG, PNG, WEBP）'
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return None, f'封面文件过大（最大 {max_size // (1024 * 1024)}MB）'
        
        # 生成封面文件名
        if music_filename:
            # 使用音乐文件名作为封面文件名（去掉音乐扩展名）
            music_base_name = os.path.splitext(music_filename)[0]
            cover_filename = f'{music_base_name}.{ext}'
        else:
            # 生成唯一文件名
            timestamp = int(time.time())
            safe_name = secure_filename(original_filename)
            name, _ = os.path.splitext(safe_name)
            cover_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{name}.{ext}"
        
        file_path = os.path.join(cover_folder, cover_filename)
        
        # 确保目录存在
        os.makedirs(cover_folder, exist_ok=True)
        
        # 原子写入：先写到临时文件
        temp_file = file_path + '.tmp'
        file.save(temp_file)
        
        # 再次验证文件大小
        actual_size = os.path.getsize(temp_file)
        if actual_size > max_size:
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
                # 保存为 JPEG（统一格式，减少文件大小）
                if ext.lower() in ['jpg', 'jpeg']:
                    img.save(temp_file, 'JPEG', quality=85)
                else:
                    img.save(temp_file, 'PNG', optimize=True)
            
        except Exception as e:
            logger.warning(f'处理封面图片失败: {str(e)}，使用原始文件')
        
        # 原子操作：重命名临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        os.replace(temp_file, file_path)
        temp_file = None  # 标记已成功，不需要清理
        
        cover_url = f'/static/music/covers/{cover_filename}'
        logger.info(f'封面文件已保存: {cover_filename} ({actual_size / (1024 * 1024):.2f} MB)')
        return cover_url, None
    
    except Exception as e:
        logger.error(f'保存封面文件失败: {str(e)}', exc_info=True)
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return None, f'保存封面失败: {str(e)}'


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    获取音频文件时长（秒）
    
    Args:
        file_path: 音频文件路径
    
    Returns:
        时长（秒），如果无法获取则返回 None
    """
    try:
        # 尝试使用 mutagen 库（如果可用）
        try:
            from mutagen.mp3 import MP3
            from mutagen import File
            
            audio = File(file_path)
            if audio is not None and hasattr(audio, 'info'):
                return audio.info.length
        except ImportError:
            logger.debug('mutagen 未安装，跳过音频时长检测')
        except Exception as e:
            logger.warning(f'使用 mutagen 获取音频时长失败: {str(e)}')
        
        # 如果 mutagen 不可用，返回 None（播放器会自动检测）
        return None
    
    except Exception as e:
        logger.error(f'获取音频时长失败: {str(e)}', exc_info=True)
        return None


def delete_file_safely(file_path: str) -> bool:
    """
    安全删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否成功删除
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f'文件已删除: {file_path}')
            return True
        return False
    except Exception as e:
        logger.error(f'删除文件失败: {file_path}, 错误: {str(e)}', exc_info=True)
        return False


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

