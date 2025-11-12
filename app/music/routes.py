# -*- coding: utf-8 -*-
"""
音乐模块 - 路由处理
"""

import os
import json
from flask import jsonify, request, render_template, send_from_directory, current_app
from flask_login import login_required, current_user
from app.music import bp
from app.music.models import MusicIndex
from app.music.utils import save_music_file, save_cover_file, validate_upload_token


def check_admin_auth():
    """
    检查管理员权限（token 或 session）
    返回: (is_admin: bool, error_message: str | None)
    """
    auth_header = request.headers.get('Authorization', '')
    token = None
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    elif current_user.is_authenticated and current_user.is_admin:
        # 也支持通过 session 验证（管理员登录）
        return True, None
    else:
        # 尝试从请求参数获取 token（用于表单提交）
        token = request.form.get('token') or request.headers.get('X-Upload-Token')
    
    # 如果提供了 token，验证它
    if token:
        admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
        if validate_upload_token(token, admin_token):
            return True, None
        return False, '无效的上传令牌'
    
    return False, '无权访问，需要管理员权限或有效的上传令牌'


def get_music_index() -> MusicIndex:
    """获取音乐索引实例"""
    index_file = os.path.join(
        current_app.config['BASE_DIR'],
        'instance',
        'music_index.json'
    )
    return MusicIndex(index_file)


@bp.route('/list')
def get_music_list():
    """
    获取音乐列表（兼容播放器接口）
    
    GET /music/list
    返回: JSON 列表 [{ id, title, artist, filename, cover, url }]
    
    注意：此接口用于播放器，只返回启用的音乐
    """
    try:
        # 使用数据库管理器（优先）或JSON索引（兼容）
        try:
            from app.music.models_db import MusicManager
            from app.models import Music
            from app.extensions import db
            
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'music' in inspector.get_table_names():
                manager = MusicManager()
                music_list = manager.get_playlist_format(enabled_only=True)
            else:
                # 表不存在，使用 JSON 索引
                raise Exception('Music table does not exist')
        except Exception as e:
            current_app.logger.warning(f'使用数据库失败，回退到JSON索引: {str(e)}')
            # 回退到JSON索引
            music_index = get_music_index()
            music_folder = current_app.config['MUSIC_FOLDER']
            cover_folder = current_app.config['COVER_FOLDER']
            allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3'})
            
            songs = music_index.sync_with_filesystem(
                music_folder, cover_folder, allowed_extensions
            )
            
            music_list = []
            for song in songs:
                music_list.append({
                    'id': song.get('id'),
                    'title': song.get('title', '未知歌曲'),
                    'artist': song.get('artist', '未知艺术家'),
                    'filename': song.get('filename'),
                    'cover': song.get('cover'),
                    'url': song.get('url', f"/static/music/{song.get('filename')}")
                })
        
        # 按标题排序
        music_list.sort(key=lambda x: x['title'])
        
        return jsonify(music_list)
    
    except Exception as e:
        current_app.logger.error(f'获取音乐列表失败: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/upload', methods=['POST'])
def upload_music():
    """
    上传音乐文件（管理员）
    
    POST /music/upload
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Form Data:
        - file: 音乐文件（MP3）
        - cover: 封面文件（可选，JPG/PNG/WEBP）
        - title: 歌曲标题（可选）
        - artist: 艺术家（可选）
    
    返回: JSON { id, title, artist, filename, cover, url }
    """
    try:
        # 验证管理员权限（使用公共函数）
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未选择音乐文件'}), 400
        
        music_file = request.files['file']
        cover_file = request.files.get('cover')
        title = request.form.get('title', '').strip()
        artist = request.form.get('artist', '').strip()
        
        if music_file.filename == '':
            return jsonify({'error': '未选择音乐文件'}), 400
        
        # 获取配置
        music_folder = current_app.config['MUSIC_FOLDER']
        cover_folder = current_app.config['COVER_FOLDER']
        max_music_size = current_app.config.get('MAX_MUSIC_SIZE', 25 * 1024 * 1024)
        max_cover_size = current_app.config.get('MAX_COVER_SIZE', 2 * 1024 * 1024)
        
        # 保存音乐文件
        filename, error, file_size = save_music_file(music_file, music_folder, max_music_size)
        if error:
            return jsonify({'error': error}), 400
        
        # 处理封面
        cover_url = None
        if cover_file and cover_file.filename:
            cover_url, cover_error = save_cover_file(
                cover_file, cover_folder, filename, max_cover_size
            )
            if cover_error:
                current_app.logger.warning(f'封面上传失败: {cover_error}')
                # 封面失败不影响音乐上传
        
        # 如果没有提供标题和艺术家，从文件名提取
        if not title or not artist:
            base_name = os.path.splitext(filename)[0]
            # 移除文件名前缀（格式：timestamp_uuid_name.ext）
            # 检查是否有时间戳和UUID前缀（时间戳是数字，UUID是8位十六进制）
            parts = base_name.split('_')
            if len(parts) >= 3:
                # 检查第一部分是否为时间戳（纯数字），第二部分是否为UUID（8位十六进制）
                try:
                    int(parts[0])  # 时间戳应该是数字
                    if len(parts[1]) == 8 and all(c in '0123456789abcdef' for c in parts[1].lower()):
                        # 移除时间戳和UUID前缀，保留原始文件名部分
                        base_name = '_'.join(parts[2:])
                except ValueError:
                    # 如果不是时间戳格式，保持原样
                    pass
            
            # 从文件名中提取艺术家和标题（格式：艺术家 - 标题）
            if ' - ' in base_name:
                parts = base_name.split(' - ', 1)
                artist = artist or parts[0].strip()
                title = title or parts[1].strip()
            else:
                title = title or base_name
                artist = artist or '未知艺术家'
        
        # 使用 save_music_file 返回的文件大小（避免重复读取文件）
        if file_size is None:
            # 如果返回值为 None，则从文件系统获取（兼容性处理）
            file_path = os.path.join(music_folder, filename)
            file_size = os.path.getsize(file_path)
        
        # 添加到索引
        music_index = get_music_index()
        song_data = {
            'filename': filename,
            'title': title,
            'artist': artist,
            'url': f'/static/music/{filename}',
            'cover': cover_url,
            'file_size': file_size
        }
        song = music_index.add_song(song_data)
        
        current_app.logger.info(f'音乐上传成功: {filename} (ID: {song["id"]})')
        
        return jsonify({
            'id': song['id'],
            'title': song['title'],
            'artist': song['artist'],
            'filename': song['filename'],
            'cover': song.get('cover'),
            'url': song['url']
        }), 200
    
    except Exception as e:
        current_app.logger.error(f'上传音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


# 注意：删除音乐功能已移至 routes_api.py
# 请使用新的 API: DELETE /music/api/music/<music_id>
# 旧的 DELETE /music/<song_id> 路由已移除，以避免端点冲突


@bp.route('/backgrounds')
def get_backgrounds():
    """
    获取背景图列表
    
    GET /music/backgrounds
    返回: JSON 列表 [url1, url2, ...]
    """
    try:
        backgrounds_folder = current_app.config.get('BACKGROUND_FOLDER')
        if not backgrounds_folder or not os.path.exists(backgrounds_folder):
            return jsonify([])
        
        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
        backgrounds = []
        
        for filename in os.listdir(backgrounds_folder):
            if os.path.isfile(os.path.join(backgrounds_folder, filename)):
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in allowed_extensions:
                    backgrounds.append(f'/static/backgrounds/{filename}')
        
        return jsonify(backgrounds)
    
    except Exception as e:
        current_app.logger.error(f'获取背景图列表失败: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/backgrounds/upload', methods=['POST'])
def upload_background():
    """
    上传背景图（管理员）
    
    POST /music/backgrounds/upload
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Form Data:
        - file: 背景图文件
    """
    try:
        # 验证权限（使用公共函数）
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 保存背景图（使用封面保存逻辑）
        backgrounds_folder = current_app.config.get('BACKGROUND_FOLDER')
        if not backgrounds_folder:
            return jsonify({'error': '背景图文件夹未配置'}), 500
        
        # 生成唯一文件名
        import uuid
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(backgrounds_folder, unique_filename)
        
        os.makedirs(backgrounds_folder, exist_ok=True)
        file.save(file_path)
        
        url = f'/static/backgrounds/{unique_filename}'
        
        return jsonify({'url': url}), 200
    
    except Exception as e:
        current_app.logger.error(f'上传背景图失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@bp.route('/player')
def player_page():
    """
    独立播放器页面
    
    GET /music/player
    返回: HTML 页面
    """
    return render_template('player.html')


@bp.route('/admin/upload')
@login_required
def admin_upload_page():
    """
    管理员上传页面（旧版，重定向到管理页面）
    
    GET /music/admin/upload
    返回: 重定向到管理页面
    """
    if not current_user.is_admin:
        from flask import flash, redirect, url_for
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    return redirect(url_for('music.admin_manager'))


@bp.route('/admin/manager')
@login_required
def admin_manager():
    """
    音乐管理页面
    
    GET /music/admin/manager
    返回: HTML 页面
    """
    if not current_user.is_admin:
        from flask import flash, redirect, url_for
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN', 'changeme123')
    max_music_size = current_app.config.get('MAX_MUSIC_SIZE', 30 * 1024 * 1024)
    max_content_length = current_app.config.get('MAX_CONTENT_LENGTH', 30 * 1024 * 1024)
    max_cover_size = current_app.config.get('MAX_COVER_SIZE', 2 * 1024 * 1024)
    return render_template('admin/music_manager.html', 
                         admin_token=admin_token,
                         max_music_size=max_music_size,
                         max_content_length=max_content_length,
                         max_cover_size=max_cover_size)

