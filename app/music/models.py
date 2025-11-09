# -*- coding: utf-8 -*-
"""
音乐模块 - 数据模型（使用 JSON 文件索引）
"""

import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Optional


class MusicIndex:
    """音乐索引管理（线程安全的 JSON 文件存储）"""
    
    def __init__(self, index_file: str):
        """
        初始化音乐索引
        
        Args:
            index_file: JSON 索引文件路径
        """
        self.index_file = index_file
        self.lock = threading.Lock()
        self._ensure_index_file()
    
    def _ensure_index_file(self):
        """确保索引文件存在"""
        if not os.path.exists(self.index_file):
            with self.lock:
                if not os.path.exists(self.index_file):
                    os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
                    with open(self.index_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'songs': [],
                            'last_updated': datetime.utcnow().isoformat()
                        }, f, ensure_ascii=False, indent=2)
    
    def _read_index(self) -> Dict:
        """读取索引文件（线程安全）"""
        with self.lock:
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {'songs': [], 'last_updated': datetime.utcnow().isoformat()}
    
    def _write_index(self, data: Dict):
        """写入索引文件（线程安全，原子操作）"""
        with self.lock:
            # 原子写入：先写到临时文件，然后重命名
            temp_file = self.index_file + '.tmp'
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Windows 上需要先删除目标文件（如果存在）
                if os.path.exists(self.index_file):
                    os.remove(self.index_file)
                os.rename(temp_file, self.index_file)
            except Exception as e:
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
    
    def get_all_songs(self) -> List[Dict]:
        """获取所有歌曲"""
        index = self._read_index()
        return index.get('songs', [])
    
    def get_song_by_id(self, song_id: int) -> Optional[Dict]:
        """根据 ID 获取歌曲"""
        songs = self.get_all_songs()
        for song in songs:
            if song.get('id') == song_id:
                return song
        return None
    
    def get_song_by_filename(self, filename: str) -> Optional[Dict]:
        """根据文件名获取歌曲"""
        songs = self.get_all_songs()
        for song in songs:
            if song.get('filename') == filename:
                return song
        return None
    
    def add_song(self, song_data: Dict) -> Dict:
        """
        添加新歌曲
        
        Args:
            song_data: 歌曲数据字典，必须包含 filename, title, artist, url
        
        Returns:
            添加后的歌曲数据（包含 id）
        """
        index = self._read_index()
        songs = index.get('songs', [])
        
        # 生成新 ID
        max_id = max([s.get('id', 0) for s in songs], default=0)
        song_id = max_id + 1
        
        # 构建完整的歌曲数据
        song = {
            'id': song_id,
            'filename': song_data['filename'],
            'title': song_data.get('title', '未知歌曲'),
            'artist': song_data.get('artist', '未知艺术家'),
            'url': song_data['url'],
            'cover': song_data.get('cover'),
            'created_at': datetime.utcnow().isoformat(),
            'file_size': song_data.get('file_size'),
            'duration': song_data.get('duration')
        }
        
        songs.append(song)
        index['songs'] = songs
        index['last_updated'] = datetime.utcnow().isoformat()
        
        self._write_index(index)
        return song
    
    def update_song(self, song_id: int, updates: Dict) -> Optional[Dict]:
        """更新歌曲信息"""
        index = self._read_index()
        songs = index.get('songs', [])
        
        for i, song in enumerate(songs):
            if song.get('id') == song_id:
                songs[i].update(updates)
                songs[i]['updated_at'] = datetime.utcnow().isoformat()
                index['songs'] = songs
                index['last_updated'] = datetime.utcnow().isoformat()
                self._write_index(index)
                return songs[i]
        
        return None
    
    def delete_song(self, song_id: int) -> bool:
        """删除歌曲"""
        index = self._read_index()
        songs = index.get('songs', [])
        
        original_length = len(songs)
        songs = [s for s in songs if s.get('id') != song_id]
        
        if len(songs) < original_length:
            index['songs'] = songs
            index['last_updated'] = datetime.utcnow().isoformat()
            self._write_index(index)
            return True
        
        return False
    
    def sync_with_filesystem(self, music_folder: str, cover_folder: str, 
                            allowed_extensions: set) -> List[Dict]:
        """
        同步索引与文件系统
        
        Args:
            music_folder: 音乐文件夹路径
            cover_folder: 封面文件夹路径
            allowed_extensions: 允许的音乐文件扩展名
        
        Returns:
            同步后的歌曲列表
        """
        if not os.path.exists(music_folder):
            return []
        
        # 获取文件系统中的所有音乐文件
        files = [f for f in os.listdir(music_folder) 
                if os.path.isfile(os.path.join(music_folder, f)) 
                and f.rsplit('.', 1)[-1].lower() in allowed_extensions]
        
        # 获取现有索引
        indexed_songs = {s['filename']: s for s in self.get_all_songs()}
        synced_songs = []
        
        for filename in files:
            if filename in indexed_songs:
                # 使用现有索引数据
                song = indexed_songs[filename]
            else:
                # 创建新索引条目
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
                
                song_data = {
                    'filename': filename,
                    'title': song_title,
                    'artist': artist,
                    'url': f'/static/music/{filename}',
                    'cover': cover_url,
                    'file_size': file_size
                }
                song = self.add_song(song_data)
            
            synced_songs.append(song)
        
        # 移除已删除的文件对应的索引
        indexed_filenames = set(indexed_songs.keys())
        filesystem_filenames = set(files)
        deleted_filenames = indexed_filenames - filesystem_filenames
        
        for filename in deleted_filenames:
            song = indexed_songs[filename]
            self.delete_song(song['id'])
        
        return synced_songs

