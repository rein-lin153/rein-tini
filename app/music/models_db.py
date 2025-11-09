# -*- coding: utf-8 -*-
"""
音乐模块 - 数据库模型辅助函数
提供数据库和JSON文件索引的兼容层
"""

import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional
from flask import current_app
from app.models import Music
from app.extensions import db


class MusicManager:
    """音乐管理器（数据库优先，JSON文件作为备份）"""
    
    def __init__(self):
        self.lock = threading.Lock()
    
    def get_all_music(self, enabled_only: bool = True) -> List[Music]:
        """获取所有音乐（数据库）"""
        query = Music.query
        if enabled_only:
            query = query.filter_by(enabled=True)
        return query.order_by(Music.order.asc(), Music.uploaded_at.desc()).all()
    
    def get_music_by_id(self, music_id: int) -> Optional[Music]:
        """根据ID获取音乐"""
        return Music.query.get(music_id)
    
    def get_music_by_filename(self, filename: str) -> Optional[Music]:
        """根据文件名获取音乐"""
        return Music.query.filter_by(filename=filename).first()
    
    def search_music(self, query: str, enabled_only: bool = True, 
                     page: int = 1, per_page: int = 20) -> Dict:
        """搜索音乐（分页）"""
        q = Music.query
        if enabled_only:
            q = q.filter_by(enabled=True)
        
        if query:
            search_term = f'%{query}%'
            q = q.filter(
                db.or_(
                    Music.title.like(search_term),
                    Music.artist.like(search_term)
                )
            )
        
        pagination = q.order_by(Music.order.asc(), Music.uploaded_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'items': [music.to_dict() for music in pagination.items]
        }
    
    def create_music(self, music_data: Dict) -> Music:
        """创建音乐记录"""
        music = Music(
            title=music_data.get('title', '未知歌曲'),
            artist=music_data.get('artist', '未知艺术家'),
            filename=music_data['filename'],
            cover=music_data.get('cover'),
            url=music_data['url'],
            duration=music_data.get('duration'),
            file_size=music_data.get('file_size'),
            order=music_data.get('order', 0),
            enabled=music_data.get('enabled', True)
        )
        db.session.add(music)
        db.session.commit()
        return music
    
    def update_music(self, music_id: int, updates: Dict) -> Optional[Music]:
        """更新音乐记录"""
        music = Music.query.get(music_id)
        if not music:
            return None
        
        for key, value in updates.items():
            if hasattr(music, key):
                setattr(music, key, value)
        
        music.updated_at = datetime.utcnow()
        db.session.commit()
        return music
    
    def delete_music(self, music_id: int) -> bool:
        """删除音乐记录"""
        music = Music.query.get(music_id)
        if not music:
            return False
        
        db.session.delete(music)
        db.session.commit()
        return True
    
    def batch_delete_music(self, music_ids: List[int]) -> Dict:
        """批量删除音乐"""
        deleted = []
        failed = []
        
        for music_id in music_ids:
            music = Music.query.get(music_id)
            if music:
                try:
                    db.session.delete(music)
                    deleted.append(music_id)
                except Exception as e:
                    failed.append({'id': music_id, 'error': str(e)})
        
        db.session.commit()
        
        return {
            'deleted': deleted,
            'failed': failed,
            'total_deleted': len(deleted),
            'total_failed': len(failed)
        }
    
    def get_cover_usage_count(self, cover_path: str) -> int:
        """获取封面使用次数（用于判断是否可以删除）"""
        if not cover_path:
            return 0
        return Music.query.filter_by(cover=cover_path).count()
    
    def sync_with_filesystem(self, music_folder: str, cover_folder: str,
                            allowed_extensions: set) -> List[Music]:
        """同步数据库与文件系统"""
        if not os.path.exists(music_folder):
            return []
        
        # 获取文件系统中的所有音乐文件
        files = [f for f in os.listdir(music_folder)
                if os.path.isfile(os.path.join(music_folder, f))
                and f.rsplit('.', 1)[-1].lower() in allowed_extensions]
        
        synced_music = []
        
        for filename in files:
            # 检查数据库中是否已存在
            music = Music.query.filter_by(filename=filename).first()
            
            if not music:
                # 创建新记录
                title = filename.rsplit('.', 1)[0]
                if ' - ' in title:
                    parts = title.split(' - ', 1)
                    artist = parts[0].strip()
                    song_title = parts[1].strip()
                else:
                    artist = '未知艺术家'
                    song_title = title
                
                # 查找封面
                cover_url = None
                if cover_folder and os.path.exists(cover_folder):
                    base_name = filename.rsplit('.', 1)[0]
                    for ext in ['jpg', 'jpeg', 'png', 'webp']:
                        cover_path = os.path.join(cover_folder, f'{base_name}.{ext}')
                        if os.path.exists(cover_path):
                            cover_url = f'/static/music/covers/{base_name}.{ext}'
                            break
                
                file_path = os.path.join(music_folder, filename)
                file_size = os.path.getsize(file_path)
                
                music_data = {
                    'filename': filename,
                    'title': song_title,
                    'artist': artist,
                    'url': f'/static/music/{filename}',
                    'cover': cover_url,
                    'file_size': file_size,
                    'enabled': True
                }
                music = self.create_music(music_data)
            
            synced_music.append(music)
        
        return synced_music
    
    def get_playlist_format(self, enabled_only: bool = True) -> List[Dict]:
        """获取播放器格式的列表（兼容现有播放器）"""
        music_list = self.get_all_music(enabled_only=enabled_only)
        return [
            {
                'id': m.id,
                'title': m.title,
                'artist': m.artist,
                'filename': m.filename,
                'cover': m.cover,
                'url': m.url
            }
            for m in music_list
        ]

