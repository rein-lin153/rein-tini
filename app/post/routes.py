# -*- coding: utf-8 -*-
"""
日记路由
"""

from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.post import bp
from app.post.forms import PostForm
from app.models import Post, Comment
from app.extensions import db
from flask import current_app
import bleach
import markdown as md


def safe_markdown(text):
    """安全的 Markdown 渲染（防止 XSS）"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'img']
    allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt', 'title']}
    
    # 渲染 Markdown
    html = md.markdown(text, extensions=['extra', 'nl2br'])
    
    # 净化 HTML
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    
    return clean_html


@bp.route('/')
def list_posts():
    """日记列表"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['POSTS_PER_PAGE']
    
    # 如果未登录，只显示公开日记
    if not current_user.is_authenticated:
        posts = Post.query.filter_by(is_private=False).order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # 已登录用户可以看到所有日记
        posts = Post.query.order_by(Post.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('post/list.html', posts=posts)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """创建新日记"""
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data,
            mood=form.mood.data if form.mood.data else None,
            is_private=form.is_private.data,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('日记发布成功！', 'success')
        return redirect(url_for('post.detail', post_id=post.id))
    
    return render_template('post/edit.html', form=form, is_new=True)


@bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """添加日记评论"""
    post = Post.query.get_or_404(post_id)
    
    # 检查是否为私密日记（非作者无法评论）
    if post.is_private and post.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限评论这篇私密日记', 'danger')
        return redirect(url_for('post.list_posts'))
    
    body = request.form.get('body', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not body:
        flash('评论内容不能为空', 'warning')
        return redirect(url_for('post.detail', post_id=post_id))
    
    comment = Comment(
        body=body,
        author_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('评论已添加', 'success')
    return redirect(url_for('post.detail', post_id=post_id))


@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """编辑日记"""
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.mood = form.mood.data if form.mood.data else None
        post.is_private = form.is_private.data
        
        db.session.commit()
        
        flash('日记已更新', 'success')
        return redirect(url_for('post.detail', post_id=post.id))
    
    return render_template('post/edit.html', form=form, post=post, is_new=False)


@bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """删除日记"""
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('日记已删除', 'success')
    return redirect(url_for('post.list_posts'))


@bp.route('/<int:post_id>')
def detail(post_id):
    """日记详情"""
    post = Post.query.get_or_404(post_id)
    
    # 检查是否为私密日记
    if post.is_private and not current_user.is_authenticated:
        abort(403)
    
    # 渲染 Markdown
    post.body_html = safe_markdown(post.body)
    
    # 获取评论
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None) \
        .order_by(Comment.created_at.asc()).all()
    
    return render_template('post/detail.html', post=post, comments=comments)

