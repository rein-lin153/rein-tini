# -*- coding: utf-8 -*-
"""
API 路由（RESTful JSON 接口）
"""

from datetime import datetime
import os
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import bp
from app.models import Post, Photo, Comment, Anniversary, User
from app.main.utils import get_days_together, get_next_anniversary
from app.extensions import db


@bp.route('/status')
def status():
    """获取站点状态信息"""
    together_date = current_app.config['TOGETHER_DATE']
    days_together = get_days_together(together_date, current_app.config['TIMEZONE'])
    next_anniversary = get_next_anniversary(together_date, current_app.config['TIMEZONE'])
    
    return jsonify({
        'status': 'ok',
        'couple_names': [
            current_app.config['COUPLE_NAME_1'],
            current_app.config['COUPLE_NAME_2']
        ],
        'together_date': together_date,
        'days_together': days_together,
        'next_anniversary': {
            'name': next_anniversary['name'],
            'date': next_anniversary['date'].isoformat() if next_anniversary['date'] else None,
            'days_left': next_anniversary['days_left']
        }
    })


@bp.route('/posts')
def get_posts():
    """获取日记列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)  # 最多 50 条
    
    # 未登录只返回公开日记
    if not current_user.is_authenticated:
        query = Post.query.filter_by(is_private=False)
    else:
        query = Post.query
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [{
            'id': post.id,
            'title': post.title,
            'body': post.body[:200] + '...' if len(post.body) > 200 else post.body,
            'author': post.author.display_name,
            'mood': post.mood,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat()
        } for post in posts.items],
        'pagination': {
            'page': posts.page,
            'per_page': posts.per_page,
            'total': posts.total,
            'pages': posts.pages,
            'has_next': posts.has_next,
            'has_prev': posts.has_prev
        }
    })


@bp.route('/posts/<int:post_id>')
def get_post(post_id):
    """获取单篇日记"""
    post = Post.query.get_or_404(post_id)
    
    # 检查私密日记
    if post.is_private and not current_user.is_authenticated:
        return jsonify({'error': '无权访问'}), 403
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'body': post.body,
        'author': post.author.display_name,
        'mood': post.mood,
        'is_private': post.is_private,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
        'comments_count': post.comments.count()
    })


@bp.route('/photos')
def get_photos():
    """获取照片列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 50)
    
    photos = Photo.query.order_by(Photo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'photos': [{
            'id': photo.id,
            'filename': photo.filename,
            'thumb_filename': photo.thumb_filename,
            'caption': photo.caption,
            'location': photo.location,
            'uploader': photo.uploader.display_name,
            'width': photo.width,
            'height': photo.height,
            'created_at': photo.created_at.isoformat(),
            'url': f'/uploads/photos/{photo.filename}',
            'thumb_url': f'/uploads/thumbs/{photo.thumb_filename}'
        } for photo in photos.items],
        'pagination': {
            'page': photos.page,
            'per_page': photos.per_page,
            'total': photos.total,
            'pages': photos.pages
        }
    })


@bp.route('/photos/<int:photo_id>')
def get_photo(photo_id):
    """获取单张照片"""
    photo = Photo.query.get_or_404(photo_id)
    
    return jsonify({
        'id': photo.id,
        'filename': photo.filename,
        'thumb_filename': photo.thumb_filename,
        'caption': photo.caption,
        'location': photo.location,
        'uploader': photo.uploader.display_name,
        'width': photo.width,
        'height': photo.height,
        'file_size': photo.file_size,
        'created_at': photo.created_at.isoformat(),
        'url': f'/uploads/photos/{photo.filename}',
        'thumb_url': f'/uploads/thumbs/{photo.thumb_filename}',
        'comments_count': photo.comments.count()
    })


@bp.route('/anniversaries')
def get_anniversaries():
    """获取纪念日列表"""
    anniversaries = Anniversary.query.order_by(Anniversary.date).all()
    
    return jsonify({
        'anniversaries': [{
            'id': ann.id,
            'name': ann.name,
            'date': ann.date.isoformat(),
            'recurrence': ann.recurrence,
            'description': ann.description
        } for ann in anniversaries]
    })


@bp.route('/upload', methods=['POST'])
@login_required
def upload_photo():
    """API 图片上传（用于富文本编辑器）"""
    from app.album.image_handler import save_uploaded_photo
    
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400
    
    file = request.files['file']
    
    try:
        photo_info = save_uploaded_photo(file)
        
        # 创建数据库记录
        photo = Photo(
            filename=photo_info['filename'],
            thumb_filename=photo_info['thumb_filename'],
            uploader_id=current_user.id,
            width=photo_info['width'],
            height=photo_info['height'],
            file_size=photo_info['file_size']
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'photo_id': photo.id,
            'url': f'/uploads/photos/{photo_info["filename"]}',
            'thumb_url': f'/uploads/thumbs/{photo_info["thumb_filename"]}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/music/list')
def get_music_list():
    """获取音乐列表（包含封面信息）"""
    import os
    
    music_folder = current_app.config.get('MUSIC_FOLDER')
    cover_folder = current_app.config.get('COVER_FOLDER')
    
    if not music_folder:
        return jsonify({
            'success': False,
            'error': '音乐文件夹配置未找到',
            'music_list': []
        })
    
    if not os.path.exists(music_folder):
        return jsonify({
            'success': False,
            'error': '音乐文件夹不存在',
            'music_list': []
        })
    
    allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3', 'wav', 'ogg', 'm4a', 'flac'})
    music_list = []
    
    try:
        files = os.listdir(music_folder)
        
        for file in files:
            file_path = os.path.join(music_folder, file)
            if os.path.isfile(file_path):
                ext = file.rsplit('.', 1)[-1].lower() if '.' in file else ''
                
                if ext in allowed_extensions:
                    # 从文件名提取标题
                    title = file.rsplit('.', 1)[0]
                    if ' - ' in title:
                        parts = title.split(' - ', 1)
                        artist = parts[0].strip()
                        song_title = parts[1].strip()
                    else:
                        artist = '未知艺术家'
                        song_title = title
                    
                    # 查找封面图片
                    cover_url = None
                    if cover_folder and os.path.exists(cover_folder):
                        # 尝试多种封面文件名格式
                        base_name = file.rsplit('.', 1)[0]
                        cover_extensions = current_app.config.get('ALLOWED_COVER_EXTENSIONS', {'jpg', 'jpeg', 'png', 'webp'})
                        for cover_ext in cover_extensions:
                            cover_filename = '{}.{}'.format(base_name, cover_ext)
                            cover_path = os.path.join(cover_folder, cover_filename)
                            if os.path.exists(cover_path):
                                cover_url = '/static/music/covers/{}'.format(cover_filename)
                                break
                    
                    music_list.append({
                        'filename': file,
                        'title': song_title,
                        'artist': artist,
                        'url': '/static/music/{}'.format(file),
                        'cover': cover_url
                    })
        
        # 按标题排序
        music_list.sort(key=lambda x: x['title'])
        
    except Exception as e:
        current_app.logger.error('获取音乐列表失败: {}'.format(str(e)), exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'music_list': []
        })
    
    return jsonify({
        'success': True,
        'music_list': music_list,
        'count': len(music_list)
    })


@bp.route('/music/upload', methods=['POST'])
@login_required
def upload_music():
    """上传音乐文件（仅管理员）"""
    from werkzeug.utils import secure_filename
    import uuid
    
    # 检查管理员权限
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': '无权访问'}), 403
    
    # 检查文件是否存在
    if 'music_file' not in request.files:
        return jsonify({'success': False, 'error': '未选择音乐文件'}), 400
    
    music_file = request.files['music_file']
    cover_file = request.files.get('cover_file')
    
    if music_file.filename == '':
        return jsonify({'success': False, 'error': '未选择音乐文件'}), 400
    
    music_folder = current_app.config.get('MUSIC_FOLDER')
    cover_folder = current_app.config.get('COVER_FOLDER')
    allowed_music_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3', 'wav', 'ogg', 'm4a', 'flac'})
    allowed_cover_extensions = current_app.config.get('ALLOWED_COVER_EXTENSIONS', {'jpg', 'jpeg', 'png', 'webp'})
    max_music_size = current_app.config.get('MAX_MUSIC_SIZE', 50 * 1024 * 1024)
    max_cover_size = current_app.config.get('MAX_COVER_SIZE', 5 * 1024 * 1024)
    
    try:
        # 验证音乐文件
        music_ext = music_file.filename.rsplit('.', 1)[-1].lower() if '.' in music_file.filename else ''
        if music_ext not in allowed_music_extensions:
            return jsonify({'success': False, 'error': '不支持的音乐格式'}), 400
        
        # 保存音乐文件（先保存到临时位置检查大小）
        filename = secure_filename(music_file.filename)
        # 如果文件已存在，添加UUID前缀
        file_path = os.path.join(music_folder, filename)
        if os.path.exists(file_path):
            name, ext = os.path.splitext(filename)
            filename = '{}_{}{}'.format(name, uuid.uuid4().hex[:8], ext)
            file_path = os.path.join(music_folder, filename)
        
        # 保存文件
        music_file.save(file_path)
        
        # 检查文件大小
        music_size = os.path.getsize(file_path)
        if music_size > max_music_size:
            # 如果文件过大，删除它
            os.remove(file_path)
            return jsonify({'success': False, 'error': '音乐文件过大（最大{}MB）'.format(max_music_size // (1024 * 1024))}), 400
        
        current_app.logger.info('音乐文件已保存: {} ({} MB)'.format(filename, music_size / (1024 * 1024)))
        
        # 处理封面文件
        cover_url = None
        if cover_file and cover_file.filename:
            cover_ext = cover_file.filename.rsplit('.', 1)[-1].lower() if '.' in cover_file.filename else ''
            if cover_ext in allowed_cover_extensions:
                # 使用音乐文件名作为封面文件名（去掉音乐扩展名，添加封面扩展名）
                music_base_name = os.path.splitext(filename)[0]
                cover_filename = '{}.{}'.format(music_base_name, cover_ext)
                cover_path = os.path.join(cover_folder, cover_filename)
                cover_file.save(cover_path)
                
                # 检查封面文件大小
                cover_size = os.path.getsize(cover_path)
                if cover_size <= max_cover_size:
                    cover_url = '/static/music/covers/{}'.format(cover_filename)
                    current_app.logger.info('封面文件已保存: {}'.format(cover_filename))
                else:
                    # 如果封面文件过大，删除它
                    os.remove(cover_path)
                    current_app.logger.warning('封面文件过大，已删除: {}'.format(cover_filename))
        
        return jsonify({
            'success': True,
            'message': '上传成功',
            'filename': filename,
            'cover': cover_url,
            'url': '/static/music/{}'.format(filename)
        })
        
    except Exception as e:
        current_app.logger.error('上传音乐失败: {}'.format(str(e)), exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

