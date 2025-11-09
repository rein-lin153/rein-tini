# -*- coding: utf-8 -*-
"""
API 路由（RESTful JSON 接口）
"""

from datetime import datetime
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
    """获取音乐列表"""
    import os
    
    music_folder = current_app.config.get('MUSIC_FOLDER')
    current_app.logger.info('音乐文件夹路径: {}'.format(music_folder))
    
    if not music_folder:
        current_app.logger.warning('MUSIC_FOLDER 配置未找到')
        return jsonify({
            'success': False,
            'error': '音乐文件夹配置未找到',
            'music_list': []
        })
    
    if not os.path.exists(music_folder):
        current_app.logger.warning('音乐文件夹不存在: {}'.format(music_folder))
        return jsonify({
            'success': False,
            'error': '音乐文件夹不存在: {}'.format(music_folder),
            'music_list': []
        })
    
    allowed_extensions = current_app.config.get('ALLOWED_MUSIC_EXTENSIONS', {'mp3', 'wav', 'ogg', 'm4a', 'flac'})
    music_list = []
    
    try:
        files = os.listdir(music_folder)
        current_app.logger.info('音乐文件夹中的文件: {}'.format(files))
        
        for file in files:
            file_path = os.path.join(music_folder, file)
            if os.path.isfile(file_path):
                ext = file.rsplit('.', 1)[-1].lower() if '.' in file else ''
                current_app.logger.debug('检查文件: {}, 扩展名: {}'.format(file, ext))
                
                if ext in allowed_extensions:
                    # 从文件名提取标题（去掉扩展名）
                    title = file.rsplit('.', 1)[0]
                    # 可以尝试从文件名解析艺术家和标题（例如：艺术家 - 标题.mp3）
                    if ' - ' in title:
                        parts = title.split(' - ', 1)
                        artist = parts[0].strip()
                        song_title = parts[1].strip()
                    else:
                        artist = '未知艺术家'
                        song_title = title
                    
                    music_list.append({
                        'filename': file,
                        'title': song_title,
                        'artist': artist,
                        'url': '/static/music/{}'.format(file)
                    })
                    current_app.logger.info('添加音乐: {} - {}'.format(artist, song_title))
        
        # 按文件名排序
        music_list.sort(key=lambda x: x['title'])
        current_app.logger.info('找到 {} 首音乐'.format(len(music_list)))
        
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

