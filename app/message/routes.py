# -*- coding: utf-8 -*-
"""
留言板路由
"""

from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.message import bp
from app.message.forms import MessageForm
from app.models import Comment
from app.extensions import db
import bleach


@bp.route('/', methods=['GET', 'POST'])
def board():
    """留言板主页"""
    if not current_app.config['ENABLE_MESSAGE_BOARD']:
        flash('留言板功能未启用', 'info')
        return redirect(url_for('main.index'))
    
    form = MessageForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('请先登录再留言', 'warning')
            return redirect(url_for('auth.login'))
        
        # 净化留言内容（防 XSS）
        clean_body = bleach.clean(form.body.data, tags=[], strip=True)
        
        comment = Comment(
            body=clean_body,
            author_id=current_user.id,
            is_private=form.is_private.data,
            post_id=None,  # 留言板留言不关联日记或照片
            photo_id=None
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('留言已发送', 'success')
        return redirect(url_for('message.board'))
    
    # 获取留言列表
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MESSAGES_PER_PAGE']
    
    # 如果未登录，只显示公开留言
    if not current_user.is_authenticated:
        messages = Comment.query.filter_by(
            post_id=None, photo_id=None, is_private=False, parent_id=None
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # 已登录用户可以看到所有留言
        messages = Comment.query.filter_by(
            post_id=None, photo_id=None, parent_id=None
        ).order_by(Comment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('message/board.html', form=form, messages=messages)


@bp.route('/<int:message_id>/reply', methods=['POST'])
@login_required
def reply(message_id):
    """回复留言"""
    parent_message = Comment.query.get_or_404(message_id)
    
    body = request.form.get('body', '').strip()
    
    if not body:
        flash('回复内容不能为空', 'warning')
        return redirect(url_for('message.board'))
    
    # 净化内容
    clean_body = bleach.clean(body, tags=[], strip=True)
    
    reply = Comment(
        body=clean_body,
        author_id=current_user.id,
        parent_id=message_id,
        post_id=None,
        photo_id=None
    )
    
    db.session.add(reply)
    db.session.commit()
    
    flash('回复已发送', 'success')
    return redirect(url_for('message.board'))


@bp.route('/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """删除留言"""
    message = Comment.query.get_or_404(message_id)
    
    # 检查权限
    if message.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此留言', 'danger')
        return redirect(url_for('message.board'))
    
    db.session.delete(message)
    db.session.commit()
    
    flash('留言已删除', 'success')
    return redirect(url_for('message.board'))

