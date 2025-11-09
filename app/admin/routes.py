# -*- coding: utf-8 -*-
"""
管理员路由
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.forms import AddUserForm, EditUserForm
from app.models import User
from app.extensions import db


def admin_required(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@bp.route('/users')
@login_required
@admin_required
def users():
    """用户管理页面"""
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)


@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """添加用户"""
    form = AddUserForm()
    
    if form.validate_on_submit():
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('该用户名已被使用', 'danger')
            return render_template('admin/add_user.html', form=form)
        
        # 创建新用户
        user = User(
            username=form.username.data,
            display_name=form.display_name.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('用户创建成功！', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建用户失败：{str(e)}', 'danger')
    
    return render_template('admin/add_user.html', form=form)


@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if request.method == 'GET':
        form.user_id.data = user.id
        form.display_name.data = user.display_name
        form.is_admin.data = user.is_admin
    
    if form.validate_on_submit():
        # 不能修改自己的管理员权限
        if user.id == current_user.id:
            # 保持原有的管理员权限
            user.display_name = form.display_name.data
            # 如果提供了新密码，则更新密码
            if form.password.data:
                user.set_password(form.password.data)
        else:
            # 更新用户信息
            user.display_name = form.display_name.data
            user.is_admin = form.is_admin.data
            # 如果提供了新密码，则更新密码
            if form.password.data:
                user.set_password(form.password.data)
        
        try:
            db.session.commit()
            flash('用户信息已更新', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新用户失败：{str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', form=form, user=user)


@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == current_user.id:
        flash('不能删除自己的账户', 'danger')
        return redirect(url_for('admin.users'))
    
    # 检查用户数量，至少保留一个用户
    user_count = User.query.count()
    if user_count <= 1:
        flash('至少需要保留一个用户', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        # 删除用户（关联的数据会通过 cascade 自动删除）
        db.session.delete(user)
        db.session.commit()
        flash(f'用户 {user.username} 已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除用户失败：{str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """切换用户管理员权限"""
    # CSRF token验证由Flask-WTF自动处理（通过请求头X-CSRFToken）
    # 如果验证失败，会自动返回403错误
    
    user = User.query.get_or_404(user_id)
    
    # 不能修改自己的管理员状态
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能修改自己的管理员权限'}), 400
    
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = '管理员' if user.is_admin else '普通用户'
        return jsonify({
            'success': True,
            'message': f'已将 {user.username} 设置为{status}',
            'is_admin': user.is_admin
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败：{str(e)}'}), 500

