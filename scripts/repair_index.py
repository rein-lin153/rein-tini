#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复/重建音乐索引脚本
扫描 MUSIC_FOLDER 并修复/重建索引文件
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Music, db
from app.music.models_db import MusicManager
from app.music.utils import get_audio_duration


def repair_index():
    """修复/重建音乐索引"""
    app = create_app()
    
    with app.app_context():
        print("开始修复音乐索引...")
        
        music_folder = app.config['MUSIC_FOLDER']
        cover_folder = app.config['COVER_FOLDER']
        allowed_extensions = app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3'})
        
        if not os.path.exists(music_folder):
            print(f"错误: 音乐文件夹不存在: {music_folder}")
            return
        
        # 获取文件系统中的所有音乐文件
        files = [f for f in os.listdir(music_folder)
                if os.path.isfile(os.path.join(music_folder, f))
                and f.rsplit('.', 1)[-1].lower() in allowed_extensions]
        
        print(f"找到 {len(files)} 个音乐文件")
        
        manager = MusicManager()
        synced_count = 0
        created_count = 0
        updated_count = 0
        
        for filename in files:
            file_path = os.path.join(music_folder, filename)
            
            # 检查数据库中是否已存在
            music = Music.query.filter_by(filename=filename).first()
            
            if music:
                # 更新现有记录
                file_size = os.path.getsize(file_path)
                duration = get_audio_duration(file_path)
                
                updates = {}
                if music.file_size != file_size:
                    updates['file_size'] = file_size
                if duration and music.duration != duration:
                    updates['duration'] = duration
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"警告: 文件不存在但数据库中有记录: {filename}")
                    continue
                
                # 查找封面
                cover_url = None
                if cover_folder and os.path.exists(cover_folder):
                    base_name = filename.rsplit('.', 1)[0]
                    for ext in ['jpg', 'jpeg', 'png', 'webp']:
                        cover_path = os.path.join(cover_folder, f'{base_name}.{ext}')
                        if os.path.exists(cover_path):
                            cover_url = f'/static/music/covers/{base_name}.{ext}'
                            break
                
                if cover_url and music.cover != cover_url:
                    updates['cover'] = cover_url
                
                if updates:
                    manager.update_music(music.id, updates)
                    updated_count += 1
                    print(f"更新: {filename}")
                
                synced_count += 1
            else:
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
                
                file_size = os.path.getsize(file_path)
                duration = get_audio_duration(file_path)
                
                music_data = {
                    'filename': filename,
                    'title': song_title,
                    'artist': artist,
                    'url': f'/static/music/{filename}',
                    'cover': cover_url,
                    'file_size': file_size,
                    'duration': duration,
                    'enabled': True
                }
                
                manager.create_music(music_data)
                created_count += 1
                print(f"创建: {filename}")
        
        # 清理数据库中不存在的文件记录
        all_music = Music.query.all()
        deleted_count = 0
        for music in all_music:
            file_path = os.path.join(music_folder, music.filename)
            if not os.path.exists(file_path):
                print(f"删除不存在的记录: {music.filename}")
                manager.delete_music(music.id)
                deleted_count += 1
        
        print("\n修复完成！")
        print(f"  同步: {synced_count} 个文件")
        print(f"  创建: {created_count} 个新记录")
        print(f"  更新: {updated_count} 个记录")
        print(f"  删除: {deleted_count} 个不存在的记录")


if __name__ == '__main__':
    repair_index()

