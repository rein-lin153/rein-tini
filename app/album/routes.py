# -*- coding: utf-8 -*-
"""
相册路由
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from app.album import bp
from app.album.forms import PhotoUploadForm, BatchPhotoUploadForm, PhotoEditForm
from app.album.image_handler import save_uploaded_photo, delete_photo_files
from app.models import Photo, Comment
from app.extensions import db
from flask import current_app


@bp.route('/')
def gallery():
    """相册展示页（瀑布流/网格）"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['PHOTOS_PER_PAGE']
    
    photos = Photo.query.order_by(Photo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('album/gallery.html', photos=photos)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """单张照片上传"""
    form = PhotoUploadForm()
    
    if form.validate_on_submit():
        try:
            # 保存照片文件
            photo_info = save_uploaded_photo(form.photo.data)
            
            # 创建数据库记录
            photo = Photo(
                filename=photo_info['filename'],
                thumb_filename=photo_info['thumb_filename'],
                caption=form.caption.data,
                location=form.location.data,
                uploader_id=current_user.id,
                width=photo_info['width'],
                height=photo_info['height'],
                file_size=photo_info['file_size']
            )
            
            db.session.add(photo)
            db.session.commit()
            
            flash('照片上传成功！', 'success')
            return redirect(url_for('album.photo_detail', photo_id=photo.id))
        
        except Exception as e:
            flash('上传失败: {}'.format(str(e)), 'danger')
    
    return render_template('album/upload.html', form=form)


@bp.route('/batch-upload', methods=['GET', 'POST'])
@login_required
def batch_upload():
    """批量照片上传"""
    form = BatchPhotoUploadForm()
    
    if form.validate_on_submit():
        files = request.files.getlist('photos')
        success_count = 0
        fail_count = 0
        
        for file in files:
            try:
                # 保存照片文件
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
                success_count += 1
            
            except Exception as e:
                fail_count += 1
                current_app.logger.error('批量上传失败: {}'.format(str(e)))
        
        db.session.commit()
        
        if success_count > 0:
            flash('成功上传 {} 张照片'.format(success_count), 'success')
        if fail_count > 0:
            flash('有 {} 张照片上传失败'.format(fail_count), 'warning')
        
        return redirect(url_for('album.gallery'))
    
    return render_template('album/batch_upload.html', form=form)


@bp.route('/<int:photo_id>/comment', methods=['POST'])
@login_required
def add_comment(photo_id):
    """添加照片评论"""
    photo = Photo.query.get_or_404(photo_id)
    
    body = request.form.get('body', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not body:
        flash('评论内容不能为空', 'warning')
        return redirect(url_for('album.photo_detail', photo_id=photo_id))
    
    comment = Comment(
        body=body,
        author_id=current_user.id,
        photo_id=photo_id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('评论已添加', 'success')
    return redirect(url_for('album.photo_detail', photo_id=photo_id))


@bp.route('/<int:photo_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_photo(photo_id):
    """编辑照片信息"""
    photo = Photo.query.get_or_404(photo_id)
    
    # 检查权限
    if photo.uploader_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = PhotoEditForm(obj=photo)
    
    if form.validate_on_submit():
        photo.caption = form.caption.data
        photo.location = form.location.data
        db.session.commit()
        
        flash('照片信息已更新', 'success')
        return redirect(url_for('album.photo_detail', photo_id=photo.id))
    
    return render_template('album/edit_photo.html', form=form, photo=photo)


@bp.route('/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """删除照片"""
    photo = Photo.query.get_or_404(photo_id)
    
    # 检查权限
    if photo.uploader_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    try:
        # 删除文件
        delete_photo_files(photo.filename, photo.thumb_filename)
        
        # 删除数据库记录（评论会级联删除）
        db.session.delete(photo)
        db.session.commit()
        
        flash('照片已删除', 'success')
    
    except Exception as e:
        flash('删除失败: {}'.format(str(e)), 'danger')
    
    return redirect(url_for('album.gallery'))


@bp.route('/<int:photo_id>')
def photo_detail(photo_id):
    """照片详情页"""
    photo = Photo.query.get_or_404(photo_id)
    
    # 获取评论
    comments = Comment.query.filter_by(photo_id=photo_id, parent_id=None) \
        .order_by(Comment.created_at.desc()).all()
    
    return render_template('album/photo_detail.html', photo=photo, comments=comments)

