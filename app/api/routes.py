# -*- coding: utf-8 -*-
"""
API 路由（RESTful JSON 接口）
"""

from datetime import datetime
import os
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import bp
from app.models import Post, Photo, Comment, Anniversary, User, Background
from app.main.utils import get_days_together, get_next_anniversary
from app.extensions import db, csrf


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


# ========== 背景管理 API ==========

def check_admin_auth():
    """检查管理员权限（token 或 session）"""
    auth_header = request.headers.get('Authorization', '')
    token = None
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
    
    if token:
        admin_token = current_app.config.get('ADMIN_UPLOAD_TOKEN')
        if token == admin_token:
            return True, None
        return False, '无效的上传令牌'
    
    # 尝试从 session 验证
    try:
        if current_user.is_authenticated and current_user.is_admin:
            return True, None
    except:
        pass
    
    return False, '无权访问，需要管理员权限或有效的上传令牌'


def ensure_backgrounds_table():
    """确保背景表存在，如果不存在则尝试创建"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'backgrounds' not in inspector.get_table_names():
            current_app.logger.warning('Backgrounds table does not exist, attempting to create...')
            try:
                db.create_all()
                current_app.logger.info('Backgrounds table created successfully')
                return True
            except Exception as create_error:
                current_app.logger.error(f'Failed to create backgrounds table: {str(create_error)}')
                return False
        return True
    except Exception as e:
        current_app.logger.error(f'Error checking backgrounds table: {str(e)}')
        return False


@bp.route('/backgrounds', methods=['GET'])
def list_backgrounds():
    """
    获取背景列表
    
    GET /api/backgrounds
    Response: {
        "backgrounds": [
            {
                "id": 1,
                "filename": "bg1.jpg",
                "url": "/uploads/backgrounds/bg1.jpg",
                "is_default": true,
                ...
            }
        ]
    }
    """
    try:
        # 确保表存在
        if not ensure_backgrounds_table():
            return jsonify({
                'error': '数据库表不存在，请运行: python scripts/init_db.py',
                'backgrounds': []
            }), 503
        
        backgrounds = Background.query.order_by(Background.is_default.desc(), Background.uploaded_at.desc()).all()
        return jsonify({
            'backgrounds': [bg.to_dict() for bg in backgrounds]
        })
    except Exception as e:
        current_app.logger.error(f'获取背景列表失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'backgrounds': []
        }), 500


@bp.route('/backgrounds', methods=['POST'])
@csrf.exempt
@login_required
def upload_background():
    """
    上传背景图片（管理员）
    
    POST /api/backgrounds
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    Form Data:
        - file: 背景图片文件（JPG/PNG，必需）
    
    Response: {
        "id": 1,
        "filename": "bg1.jpg",
        "url": "/uploads/backgrounds/bg1.jpg",
        ...
    }
    """
    try:
        # 确保表存在
        if not ensure_backgrounds_table():
            return jsonify({'error': '数据库表不存在，请运行: python scripts/init_db.py'}), 503
        
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件类型
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return jsonify({'error': '不支持的文件格式，仅支持 JPG/PNG'}), 400
        
        # 检查文件大小（最大 5MB）
        max_size = 5 * 1024 * 1024  # 5MB
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return jsonify({'error': '文件过大，最大 5MB'}), 400
        
        # 保存文件
        try:
            from PIL import Image
        except ImportError:
            return jsonify({'error': 'PIL/Pillow 库未安装，请安装: pip install Pillow'}), 500
        
        import uuid
        from werkzeug.utils import secure_filename
        
        backgrounds_folder = current_app.config['BACKGROUNDS_FOLDER']
        os.makedirs(backgrounds_folder, exist_ok=True)
        
        # 生成唯一文件名
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_ext}"
        filename = secure_filename(filename)
        file_path = os.path.join(backgrounds_folder, filename)
        
        # 打开并处理图片
        img = Image.open(file)
        
        # 获取图片尺寸
        width, height = img.size
        
        # 如果是 PNG，转换为 RGB（JPG 不支持透明度）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # 保存图片
        img.save(file_path, 'JPEG', quality=85, optimize=True)
        
        # 更新文件大小（保存后可能不同）
        file_size = os.path.getsize(file_path)
        
        # 创建数据库记录
        background = Background(
            filename=filename,
            url=f'/uploads/backgrounds/{filename}',
            file_size=file_size,
            width=width,
            height=height,
            is_default=False
        )
        
        db.session.add(background)
        db.session.commit()
        
        current_app.logger.info(f'背景上传成功: {filename} (ID: {background.id})')
        
        return jsonify(background.to_dict()), 201
    
    except Exception as e:
        current_app.logger.error(f'上传背景失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@bp.route('/backgrounds/<int:bg_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_background(bg_id):
    """
    删除背景（管理员）
    
    DELETE /api/backgrounds/<id>
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    
    Response: {
        "success": true
    }
    """
    try:
        # 确保表存在
        if not ensure_backgrounds_table():
            return jsonify({'error': '数据库表不存在，请运行: python scripts/init_db.py'}), 503
        
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        background = Background.query.get_or_404(bg_id)
        
        # 不能删除默认背景
        if background.is_default:
            return jsonify({'error': '不能删除默认背景，请先设置其他背景为默认'}), 400
        
        # 删除文件
        backgrounds_folder = current_app.config['BACKGROUNDS_FOLDER']
        file_path = os.path.join(backgrounds_folder, background.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f'删除背景文件失败: {str(e)}')
        
        # 从数据库删除
        db.session.delete(background)
        db.session.commit()
        
        current_app.logger.info(f'背景已删除: {background.filename} (ID: {bg_id})')
        
        return jsonify({'success': True})
    
    except Exception as e:
        current_app.logger.error(f'删除背景失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@bp.route('/backgrounds/<int:bg_id>/default', methods=['PUT'])
@csrf.exempt
@login_required
def set_default_background(bg_id):
    """
    设置默认背景（管理员）
    
    PUT /api/backgrounds/<id>/default
    Headers: Authorization: Bearer <ADMIN_UPLOAD_TOKEN>
    
    Response: {
        "id": 1,
        "is_default": true,
        ...
    }
    """
    try:
        # 确保表存在
        if not ensure_backgrounds_table():
            return jsonify({'error': '数据库表不存在，请运行: python scripts/init_db.py'}), 503
        
        # 检查管理员权限
        is_admin, error_msg = check_admin_auth()
        if not is_admin:
            return jsonify({'error': error_msg}), 403
        
        background = Background.query.get_or_404(bg_id)
        
        # 取消其他背景的默认状态
        Background.query.filter_by(is_default=True).update({'is_default': False})
        
        # 设置当前背景为默认
        background.is_default = True
        db.session.commit()
        
        current_app.logger.info(f'设置默认背景: {background.filename} (ID: {bg_id})')
        
        return jsonify(background.to_dict())
    
    except Exception as e:
        current_app.logger.error(f'设置默认背景失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': f'设置失败: {str(e)}'}), 500


@bp.route('/backgrounds/default', methods=['GET'])
def get_default_background():
    """
    获取默认背景
    
    GET /api/backgrounds/default
    Response: {
        "id": 1,
        "url": "/uploads/backgrounds/bg1.jpg",
        ...
    }
    """
    try:
        # 确保表存在
        if not ensure_backgrounds_table():
            return jsonify({'url': None, 'message': '未设置默认背景'}), 200
        
        background = Background.query.filter_by(is_default=True).first()
        if not background:
            return jsonify({'url': None, 'message': '未设置默认背景'})
        return jsonify(background.to_dict())
    except Exception as e:
        current_app.logger.error(f'获取默认背景失败: {str(e)}', exc_info=True)
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'url': None, 'message': '未设置默认背景', 'error': str(e)}), 200



