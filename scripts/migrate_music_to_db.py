#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将JSON索引迁移到数据库
从 music_index.json 迁移数据到数据库
"""

import os
import sys
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Music, db
from app.music.models_db import MusicManager


def migrate_to_db():
    """从JSON索引迁移到数据库"""
    app = create_app()
    
    with app.app_context():
        print("开始迁移音乐索引到数据库...")
        
        # 读取JSON索引
        index_file = os.path.join(
            app.config['BASE_DIR'],
            'instance',
            'music_index.json'
        )
        
        if not os.path.exists(index_file):
            print(f"JSON索引文件不存在: {index_file}")
            print("将扫描文件系统并创建数据库记录...")
            from scripts.repair_index import repair_index
            repair_index()
            return
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        songs = index_data.get('songs', [])
        print(f"找到 {len(songs)} 条记录")
        
        manager = MusicManager()
        migrated_count = 0
        skipped_count = 0
        
        for song in songs:
            # 检查是否已存在
            existing = Music.query.filter_by(filename=song.get('filename')).first()
            if existing:
                print(f"跳过已存在的记录: {song.get('filename')}")
                skipped_count += 1
                continue
            
            # 创建新记录
            music_data = {
                'filename': song.get('filename'),
                'title': song.get('title', '未知歌曲'),
                'artist': song.get('artist', '未知艺术家'),
                'url': song.get('url', f"/static/music/{song.get('filename')}"),
                'cover': song.get('cover'),
                'file_size': song.get('file_size'),
                'duration': song.get('duration'),
                'order': song.get('order', 0),
                'enabled': song.get('enabled', True)
            }
            
            try:
                manager.create_music(music_data)
                migrated_count += 1
                print(f"迁移: {song.get('filename')}")
            except Exception as e:
                print(f"迁移失败: {song.get('filename')}, 错误: {str(e)}")
        
        print("\n迁移完成！")
        print(f"  迁移: {migrated_count} 条记录")
        print(f"  跳过: {skipped_count} 条记录")
        print("\n注意: JSON索引文件已保留作为备份，可以手动删除")


if __name__ == '__main__':
    migrate_to_db()

