# -*- coding: utf-8 -*-
"""
主页路由
"""

from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.main import bp
from app.main.utils import get_days_together, get_next_anniversary, get_love_percentage
from app.models import Photo, Post, Comment, Anniversary, SiteSetting
from app.extensions import db


@bp.route('/')
@bp.route('/index')
def index():
    """首页（Dashboard）"""
    # 获取在一起天数
    together_date = current_app.config['TOGETHER_DATE']
    days_together = get_days_together(together_date, current_app.config['TIMEZONE'])
    
    # 获取下一个纪念日
    next_anniversary = get_next_anniversary(together_date, current_app.config['TIMEZONE'])
    
    # 获取爱情进度
    love_percentage = get_love_percentage(days_together)
    
    # 获取最新 3 张照片
    latest_photos = Photo.query.order_by(Photo.created_at.desc()).limit(3).all()
    
    # 获取最新 3 篇日记
    latest_posts = Post.query.order_by(Post.created_at.desc()).limit(3).all()
    
    # 获取最新 5 条留言
    latest_comments = Comment.query.filter_by(post_id=None, photo_id=None) \
        .order_by(Comment.created_at.desc()).limit(5).all()
    
    # 获取自定义背景（如果有）
    custom_bg = SiteSetting.get('background_image')
    
    return render_template('index.html',
                         days_together=days_together,
                         next_anniversary=next_anniversary,
                         love_percentage=love_percentage,
                         latest_photos=latest_photos,
                         latest_posts=latest_posts,
                         latest_comments=latest_comments,
                         custom_bg=custom_bg)


@bp.route('/about')
def about():
    """关于页面"""
    together_date = current_app.config['TOGETHER_DATE']
    days_together = get_days_together(together_date)
    
    # 获取所有纪念日
    anniversaries = Anniversary.query.order_by(Anniversary.date).all()
    
    return render_template('main/about.html',
                         days_together=days_together,
                         anniversaries=anniversaries)




@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """站点设置（仅管理员）"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # 更新站点标题
        site_title = request.form.get('site_title')
        if site_title:
            SiteSetting.set('site_title', site_title)
        
        # 更新站点副标题
        site_subtitle = request.form.get('site_subtitle')
        if site_subtitle:
            SiteSetting.set('site_subtitle', site_subtitle)
        
        # 处理背景图片上传（简化版）
        # 实际项目中应该使用文件上传处理
        
        flash('设置已保存', 'success')
        return redirect(url_for('main.settings'))
    
    # 获取当前设置
    current_settings = {
        'site_title': SiteSetting.get('site_title', current_app.config['SITE_TITLE']),
        'site_subtitle': SiteSetting.get('site_subtitle', current_app.config['SITE_SUBTITLE'])
    }
    
    return render_template('main/settings.html', settings=current_settings)

