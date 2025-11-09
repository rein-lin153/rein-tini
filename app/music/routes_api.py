# -*- coding: utf-8 -*-
"""
音乐模块 - REST API 路由（新的管理 API）
"""

import os
from flask import jsonify, request, send_from_directory, current_app
from flask_login import login_required, current_user
from app.music import bp
from app.music.models_db import MusicManager
from app.music.utils import (
    save_music_file, save_cover_file, validate_upload_token,
    get_audio_duration, delete_file_safely
)
from app.extensions import db, csrf


def get_music_manager() -> MusicManager:
    """获取音乐管理器实例"""
    return MusicManager()


def check_admin_auth():
    """检查管理员权限（token 或 session）"""
    auth_header = request.headers.get('Authorization', '')
    token = None
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    
    if token:
        admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
        if not validate_upload_token(token, admin_token):
            return False, '无效的上传令牌'
        return True, None
    
    # 尝试从 session 验证
    try:
        if current_user.is_authenticated and current_user.is_admin:
            return True, None
    except:
        # 如果无法访问 current_user，返回 False
        pass
    
    return False, '无权访问，需要管理员权限或有效的上传令牌'


@bp.route('/api/music', methods=['GET'])
@bp.route('/api/music/', methods=['GET'])
def list_music():
    """
    获取音乐列表（分页、搜索）
    
    GET /music/api/music?page=1&per_page=20&q=search_term
    
    Query params:
        - page: 页码（默认 1）
        - per_page: 每页数量（默认 20）
        - q: 搜索关键词（可选，模糊搜索 title/artist）
    
    Response: {
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5,
        "items": [
            {
                "id": 1,
                "title": "歌曲名",
                "artist": "艺术家",
                "filename": "song.mp3",
                "cover": "/static/music/covers/song.jpg",
                "url": "/static/music/song.mp3",
                "duration": 180.5,
                "file_size": 5242880,
                "order": 0,
                "enabled": true,
                "uploaded_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
    }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        query = request.args.get('q', '').strip()
        
        # 限制每页数量
        per_page = min(per_page, 100)
        page = max(1, page)
        
        # 是否只返回启用的音乐（非管理员默认只返回启用的）
        enabled_only = True
        try:
            if current_user.is_authenticated and current_user.is_admin:
                # 管理员可以查看所有音乐
                enabled_only = False
        except:
            # 如果无法访问 current_user，默认只返回启用的
            pass
        
        # 尝试使用数据库（优先）
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'music' in inspector.get_table_names():
                manager = get_music_manager()
                result = manager.search_music(
                    query=query,
                    enabled_only=enabled_only,
                    page=page,
                    per_page=per_page
                )
                return jsonify(result)
        except Exception as db_error:
            current_app.logger.warning(f'使用数据库失败，回退到JSON索引: {str(db_error)}')
        
        # 回退到 JSON 索引
        try:
            from app.music.routes import get_music_index
            music_index = get_music_index()
            music_folder = current_app.config['MUSIC_FOLDER']
            cover_folder = current_app.config['COVER_FOLDER']
            allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3'})
            
            # 同步文件系统
            songs = music_index.sync_with_filesystem(
                music_folder, cover_folder, allowed_extensions
            )
            
            # 过滤启用的音乐
            if enabled_only:
                songs = [s for s in songs if s.get('enabled', True)]
            
            # 搜索过滤
            if query:
                query_lower = query.lower()
                songs = [s for s in songs 
                        if query_lower in s.get('title', '').lower() 
                        or query_lower in s.get('artist', '').lower()]
            
            # 分页
            total = len(songs)
            pages = (total + per_page - 1) // per_page if total > 0 else 0
            start = (page - 1) * per_page
            end = start + per_page
            items = songs[start:end]
            
            # 转换为 API 格式
            result_items = []
            for song in items:
                result_items.append({
                    'id': song.get('id'),
                    'title': song.get('title', '未知歌曲'),
                    'artist': song.get('artist', '未知艺术家'),
                    'filename': song.get('filename'),
                    'cover': song.get('cover'),
                    'url': song.get('url', f"/static/music/{song.get('filename')}"),
                    'duration': song.get('duration'),
                    'file_size': song.get('file_size'),
                    'order': song.get('order', 0),
                    'enabled': song.get('enabled', True),
                    'uploaded_at': song.get('created_at') or song.get('uploaded_at'),
                    'updated_at': song.get('updated_at')
                })
            
            return jsonify({
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': pages,
                'items': result_items
            })
        except Exception as json_error:
            current_app.logger.error(f'使用JSON索引失败: {str(json_error)}', exc_info=True)
            # 如果 JSON 索引也失败，返回空列表
            return jsonify({
                'total': 0,
                'page': page,
                'per_page': per_page,
                'pages': 0,
                'items': []
            })
    
    except Exception as e:
        current_app.logger.error(f'获取音乐列表失败: {str(e)}', exc_info=True)
        return jsonify({
            'error': str(e),
            'total': 0,
            'page': 1,
            'per_page': 20,
            'pages': 0,
            'items': []
        }), 500


@bp.route('/api/music/<int:music_id>', methods=['GET'])
def get_music(music_id):
    """
    获取单条音乐记录
    
    GET /api/music/<id>
    
    Response: {
        "id": 1,
        "title": "歌曲名",
        ...
    }
    """
    try:
        # 检查数据库表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'music' not in inspector.get_table_names():
            return jsonify({'error': 'Music table does not exist. Please run: python scripts/create_music_table.py'}), 503
        
        manager = get_music_manager()
        music = manager.get_music_by_id(music_id)
        
        if not music:
            return jsonify({'error': '音乐不存在'}), 404
        
        # 非管理员只能查看启用的音乐
        try:
            if not music.enabled and not (current_user.is_authenticated and current_user.is_admin):
                return jsonify({'error': '音乐不存在'}), 404
        except:
            # 如果无法访问 current_user，默认只返回启用的
            if not music.enabled:
                return jsonify({'error': '音乐不存在'}), 404
        
        return jsonify(music.to_dict())
    
    except Exception as e:
        current_app.logger.error(f'获取音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/api/music', methods=['POST'])
@csrf.exempt
def create_music():
    """
    上传音乐文件（管理员）
    
    POST /api/music
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Content-Type: multipart/form-data
    
    Form Data:
        - file: 音乐文件（MP3，必需）
        - cover: 封面文件（可选，JPG/PNG/WEBP）
        - title: 歌曲标题（可选）
        - artist: 艺术家（可选）
        - enabled: 是否启用（可选，默认 true）
        - order: 排序顺序（可选，默认 0）
    
    Response: {
        "id": 1,
        "title": "歌曲名",
        ...
    }
    """
    try:
        # 检查数据库表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'music' not in inspector.get_table_names():
            current_app.logger.warning('Music table does not exist, attempting to create...')
            try:
                db.create_all()
                current_app.logger.info('Music table created successfully')
            except Exception as create_error:
                current_app.logger.error(f'Failed to create music table: {str(create_error)}')
                import traceback
                current_app.logger.error(traceback.format_exc())
                return jsonify({'error': '数据库表不存在，请运行: python scripts/init_db.py'}), 503
        
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '未选择音乐文件'}), 400
        
        music_file = request.files['file']
        cover_file = request.files.get('cover')
        
        if music_file.filename == '':
            return jsonify({'error': '未选择音乐文件'}), 400
        
        # 获取配置
        music_folder = current_app.config['MUSIC_FOLDER']
        cover_folder = current_app.config['COVER_FOLDER']
        max_music_size = current_app.config.get('MAX_MUSIC_SIZE', 30 * 1024 * 1024)
        max_cover_size = current_app.config.get('MAX_COVER_SIZE', 2 * 1024 * 1024)
        
        # 确保目录存在
        os.makedirs(music_folder, exist_ok=True)
        os.makedirs(cover_folder, exist_ok=True)
        
        # 保存音乐文件
        filename, error, file_size = save_music_file(music_file, music_folder, max_music_size)
        if error:
            current_app.logger.error(f'保存音乐文件失败: {error}')
            return jsonify({'error': error}), 400
        
        # 获取音频时长
        file_path = os.path.join(music_folder, filename)
        duration = None
        try:
            duration = get_audio_duration(file_path)
        except Exception as e:
            current_app.logger.warning(f'获取音频时长失败: {str(e)}')
        
        # 处理封面
        cover_url = None
        if cover_file and cover_file.filename:
            try:
                cover_url, cover_error = save_cover_file(
                    cover_file, cover_folder, filename, max_cover_size
                )
                if cover_error:
                    current_app.logger.warning(f'封面上传失败: {cover_error}')
            except Exception as e:
                current_app.logger.warning(f'处理封面失败: {str(e)}')
        else:
            # 使用默认封面
            default_cover = current_app.config.get('DEFAULT_COVER', '/static/images/default_cover.jpg')
            default_cover_path = os.path.join(current_app.config['BASE_DIR'], 'app', 'static', 'images', 'default_cover.jpg')
            if os.path.exists(default_cover_path):
                cover_url = default_cover
        
        # 获取元数据
        title = request.form.get('title', '').strip()
        artist = request.form.get('artist', '').strip()
        enabled = request.form.get('enabled', 'true').lower() == 'true'
        try:
            order = int(request.form.get('order', 0))
        except (ValueError, TypeError):
            order = 0
        
        # 如果没有提供标题和艺术家，从文件名提取
        if not title or not artist:
            base_name = os.path.splitext(filename)[0]
            # 移除时间戳和UUID前缀（如果有）
            parts = base_name.split('_')
            if len(parts) >= 3:
                # 格式: timestamp_uuid_original_name
                base_name = '_'.join(parts[2:])
            
            if ' - ' in base_name:
                parts = base_name.split(' - ', 1)
                artist = artist or parts[0].strip()
                title = title or parts[1].strip()
            else:
                title = title or base_name
                artist = artist or '未知艺术家'
        
        # 创建音乐记录
        try:
            manager = get_music_manager()
            music_data = {
                'filename': filename,
                'title': title,
                'artist': artist,
                'url': f'/static/music/{filename}',
                'cover': cover_url,
                'file_size': file_size,
                'duration': duration,
                'order': order,
                'enabled': enabled
            }
            music = manager.create_music(music_data)
            
            current_app.logger.info(f'音乐上传成功: {filename} (ID: {music.id})')
            
            return jsonify(music.to_dict()), 201
        except Exception as db_error:
            current_app.logger.error(f'创建音乐记录失败: {str(db_error)}', exc_info=True)
            import traceback
            current_app.logger.error(traceback.format_exc())
            db.session.rollback()
            # 删除已上传的文件
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            return jsonify({'error': f'创建音乐记录失败: {str(db_error)}'}), 500
    
    except Exception as e:
        current_app.logger.error(f'上传音乐失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@bp.route('/api/music/<int:music_id>', methods=['PUT'])
@csrf.exempt
def update_music(music_id):
    """
    更新音乐元数据（管理员）
    
    PUT /api/music/<id>
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Content-Type: multipart/form-data 或 application/json
    
    Form Data / JSON:
        - title: 歌曲标题（可选）
        - artist: 艺术家（可选）
        - enabled: 是否启用（可选）
        - order: 排序顺序（可选）
        - cover: 封面文件（可选，替换封面）
    
    Response: {
        "id": 1,
        "title": "更新后的标题",
        ...
    }
    """
    try:
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        manager = get_music_manager()
        music = manager.get_music_by_id(music_id)
        
        if not music:
            return jsonify({'error': '音乐不存在'}), 404
        
        updates = {}
        
        # 处理 JSON 数据
        if request.is_json:
            data = request.get_json()
            if 'title' in data:
                updates['title'] = data['title']
            if 'artist' in data:
                updates['artist'] = data['artist']
            if 'enabled' in data:
                updates['enabled'] = bool(data['enabled'])
            if 'order' in data:
                updates['order'] = int(data['order'])
        
        # 处理表单数据
        if request.form:
            if 'title' in request.form:
                updates['title'] = request.form['title'].strip()
            if 'artist' in request.form:
                updates['artist'] = request.form['artist'].strip()
            if 'enabled' in request.form:
                updates['enabled'] = request.form['enabled'].lower() == 'true'
            if 'order' in request.form:
                updates['order'] = int(request.form['order'])
        
        # 处理封面替换
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            cover_folder = current_app.config['COVER_FOLDER']
            max_cover_size = current_app.config.get('MAX_COVER_SIZE', 2 * 1024 * 1024)
            
            # 删除旧封面（如果存在且不被其他记录使用）
            old_cover = music.cover
            if old_cover:
                old_cover_path = old_cover.replace('/static/music/covers/', '')
                old_cover_full_path = os.path.join(cover_folder, old_cover_path)
                
                # 检查是否有其他记录使用此封面
                usage_count = manager.get_cover_usage_count(old_cover)
                if usage_count <= 1:  # 只有当前记录使用
                    delete_file_safely(old_cover_full_path)
            
            # 保存新封面
            cover_url, cover_error = save_cover_file(
                cover_file, cover_folder, music.filename, max_cover_size
            )
            if cover_error:
                return jsonify({'error': f'封面上传失败: {cover_error}'}), 400
            
            updates['cover'] = cover_url
        
        # 更新记录
        if updates:
            music = manager.update_music(music_id, updates)
            if not music:
                return jsonify({'error': '更新失败'}), 500
        
        return jsonify(music.to_dict())
    
    except Exception as e:
        current_app.logger.error(f'更新音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'更新失败: {str(e)}'}), 500


@bp.route('/api/music/<int:music_id>', methods=['DELETE'])
@csrf.exempt
def delete_music(music_id):
    """
    删除音乐（管理员）
    
    DELETE /api/music/<id>
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    
    Response: {
        "success": true
    }
    """
    try:
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        manager = get_music_manager()
        music = manager.get_music_by_id(music_id)
        
        if not music:
            return jsonify({'error': '音乐不存在'}), 404
        
        # 删除音乐文件
        music_folder = current_app.config['MUSIC_FOLDER']
        file_path = os.path.join(music_folder, music.filename)
        delete_file_safely(file_path)
        
        # 删除封面（如果存在且不被其他记录使用）
        if music.cover:
            cover_usage_count = manager.get_cover_usage_count(music.cover)
            if cover_usage_count <= 1:  # 只有当前记录使用
                cover_path = music.cover.replace('/static/music/covers/', '')
                cover_folder = current_app.config['COVER_FOLDER']
                cover_full_path = os.path.join(cover_folder, cover_path)
                delete_file_safely(cover_full_path)
        
        # 从数据库删除
        manager.delete_music(music_id)
        
        current_app.logger.info(f'音乐已删除: {music.filename} (ID: {music_id})')
        
        return jsonify({'success': True})
    
    except Exception as e:
        current_app.logger.error(f'删除音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/api/music/batch-delete', methods=['POST'])
@csrf.exempt
def batch_delete_music():
    """
    批量删除音乐（管理员）
    
    POST /api/music/batch-delete
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Content-Type: application/json
    
    JSON Body: {
        "ids": [1, 2, 3]
    }
    
    Response: {
        "deleted": [1, 2, 3],
        "failed": [],
        "total_deleted": 3,
        "total_failed": 0
    }
    """
    try:
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        data = request.get_json()
        if not data or 'ids' not in data:
            return jsonify({'error': '缺少 ids 参数'}), 400
        
        music_ids = data['ids']
        if not isinstance(music_ids, list):
            return jsonify({'error': 'ids 必须是数组'}), 400
        
        manager = get_music_manager()
        
        # 批量删除
        deleted = []
        failed = []
        
        for music_id in music_ids:
            try:
                music = manager.get_music_by_id(music_id)
                if not music:
                    failed.append({'id': music_id, 'error': '音乐不存在'})
                    continue
                
                # 删除文件
                music_folder = current_app.config['MUSIC_FOLDER']
                file_path = os.path.join(music_folder, music.filename)
                delete_file_safely(file_path)
                
                # 删除封面
                if music.cover:
                    cover_usage_count = manager.get_cover_usage_count(music.cover)
                    if cover_usage_count <= 1:
                        cover_path = music.cover.replace('/static/music/covers/', '')
                        cover_folder = current_app.config['COVER_FOLDER']
                        cover_full_path = os.path.join(cover_folder, cover_path)
                        delete_file_safely(cover_full_path)
                
                # 从数据库删除
                manager.delete_music(music_id)
                deleted.append(music_id)
                
            except Exception as e:
                failed.append({'id': music_id, 'error': str(e)})
        
        return jsonify({
            'deleted': deleted,
            'failed': failed,
            'total_deleted': len(deleted),
            'total_failed': len(failed)
        })
    
    except Exception as e:
        current_app.logger.error(f'批量删除音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500


@bp.route('/api/music/download/<int:music_id>', methods=['GET'])
def download_music(music_id):
    """
    下载音乐文件
    
    GET /api/music/download/<id>
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN> (可选，管理员可以直接下载)
    
    Response: 文件流或重定向到静态URL
    """
    try:
        manager = get_music_manager()
        music = manager.get_music_by_id(music_id)
        
        if not music:
            return jsonify({'error': '音乐不存在'}), 404
        
        # 检查权限（非管理员只能下载启用的音乐）
        if not music.enabled:
            is_admin, _ = check_admin_auth()
            if not is_admin:
                return jsonify({'error': '无权下载'}), 403
        
        # 检查文件是否存在
        music_folder = current_app.config['MUSIC_FOLDER']
        file_path = os.path.join(music_folder, music.filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404
        
        # 返回文件（带下载头）
        as_attachment = request.args.get('attachment', 'false').lower() == 'true'
        return send_from_directory(
            music_folder,
            music.filename,
            as_attachment=as_attachment,
            download_name=music.filename
        )
    
    except Exception as e:
        current_app.logger.error(f'下载音乐失败: {str(e)}', exc_info=True)
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

