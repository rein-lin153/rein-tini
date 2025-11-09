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
    获取音乐列表
    
    GET /music/list
    返回: JSON 列表 [{ id, title, artist, filename, cover, url }]
    """
    try:
        music_index = get_music_index()
        
        # 同步文件系统
        music_folder = current_app.config['MUSIC_FOLDER']
        cover_folder = current_app.config['COVER_FOLDER']
        allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3'})
        
        songs = music_index.sync_with_filesystem(
            music_folder, cover_folder, allowed_extensions
        )
        
        # 转换为 API 格式
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
        # 验证管理员权限（使用 token 或 session）
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        elif current_user.is_authenticated and current_user.is_admin:
            # 也支持通过 session 验证（管理员登录）
            pass
        else:
            # 尝试从请求参数获取 token（用于表单提交）
            token = request.form.get('token') or request.headers.get('X-Upload-Token')
        
        # 如果提供了 token，验证它
        if token:
            admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
            if not validate_upload_token(token, admin_token):
                return jsonify({'error': '无效的上传令牌'}), 403
        elif not (current_user.is_authenticated and current_user.is_admin):
            return jsonify({'error': '无权访问，需要管理员权限或有效的上传令牌'}), 403
        
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
        filename, error = save_music_file(music_file, music_folder, max_music_size)
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
            # 移除 UUID 前缀（如果有）
            if '_' in base_name and len(base_name.split('_')[0]) == 8:
                base_name = '_'.join(base_name.split('_')[1:])
            
            if ' - ' in base_name:
                parts = base_name.split(' - ', 1)
                artist = artist or parts[0].strip()
                title = title or parts[1].strip()
            else:
                title = title or base_name
                artist = artist or '未知艺术家'
        
        # 获取文件大小
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


@bp.route('/<int:song_id>', methods=['DELETE'])
def delete_music(song_id):
    """
    删除音乐（管理员）
    
    DELETE /music/<id>
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    """
    try:
        # 验证权限
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if token:
            admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
            if not validate_upload_token(token, admin_token):
                return jsonify({'error': '无效的上传令牌'}), 403
        elif not (current_user.is_authenticated and current_user.is_admin):
            return jsonify({'error': '无权访问'}), 403
        
        music_index = get_music_index()
        song = music_index.get_song_by_id(song_id)
        
        if not song:
            return jsonify({'error': '歌曲不存在'}), 404
        
        # 删除文件
        music_folder = current_app.config['MUSIC_FOLDER']
        file_path = os.path.join(music_folder, song['filename'])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f'删除音乐文件失败: {str(e)}')
        
        # 删除封面
        if song.get('cover'):
            cover_filename = os.path.basename(song['cover'])
            cover_folder = current_app.config['COVER_FOLDER']
            cover_path = os.path.join(cover_folder, cover_filename)
            if os.path.exists(cover_path):
                try:
                    os.remove(cover_path)
                except Exception as e:
                    current_app.logger.warning(f'删除封面文件失败: {str(e)}')
        
        # 从索引删除
        music_index.delete_song(song_id)
        
        current_app.logger.info(f'音乐已删除: {song["filename"]} (ID: {song_id})')
        
        return jsonify({'message': '删除成功'}), 200
    
    except Exception as e:
        current_app.logger.error(f'删除音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


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
        # 验证权限
        auth_header = request.headers.get('Authorization', '')
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        
        if token:
            admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
            if not validate_upload_token(token, admin_token):
                return jsonify({'error': '无效的上传令牌'}), 403
        elif not (current_user.is_authenticated and current_user.is_admin):
            return jsonify({'error': '无权访问'}), 403
        
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
    管理员上传页面
    
    GET /music/admin/upload
    返回: HTML 页面
    """
    if not current_user.is_admin:
        from flask import flash, redirect, url_for
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN', 'changeme123')
    return render_template('admin/music_upload.html', admin_token=admin_token)

