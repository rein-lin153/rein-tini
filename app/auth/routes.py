# -*- coding: utf-8 -*-
"""
认证路由
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User
from app.extensions import db, limiter


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per 15 minutes")
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 登录用户
        login_user(user, remember=form.remember_me.data)
        
        flash('欢迎回来，{}！'.format(user.display_name), 'success')
        
        # 跳转到原页面或首页
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    """登出"""
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('main.index'))

