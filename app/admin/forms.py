# -*- coding: utf-8 -*-
"""
管理员表单
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User


class AddUserForm(FlaskForm):
    """添加用户表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=64, message='用户名长度应在 3-64 个字符之间')
    ])
    display_name = StringField('显示名称', validators=[
        DataRequired(message='请输入显示名称'),
        Length(min=1, max=64, message='显示名称长度应在 1-64 个字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, message='密码至少需要 6 个字符')
    ])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    is_admin = BooleanField('设为管理员', default=False)
    submit = SubmitField('创建用户')
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')


class EditUserForm(FlaskForm):
    """编辑用户表单"""
    user_id = HiddenField('用户ID')
    display_name = StringField('显示名称', validators=[
        DataRequired(message='请输入显示名称'),
        Length(min=1, max=64, message='显示名称长度应在 1-64 个字符之间')
    ])
    password = PasswordField('新密码（留空则不修改）')
    password_confirm = PasswordField('确认新密码')
    is_admin = BooleanField('设为管理员', default=False)
    submit = SubmitField('保存修改')
    
    def validate_password(self, password):
        """如果填写了密码，则必须确认密码"""
        if password.data:
            if len(password.data) < 6:
                raise ValidationError('密码至少需要 6 个字符')
    
    def validate_password_confirm(self, password_confirm):
        """如果填写了密码，则必须填写确认密码"""
        if self.password.data and not password_confirm.data:
            raise ValidationError('请确认新密码')
        if self.password.data and password_confirm.data != self.password.data:
            raise ValidationError('两次输入的密码不一致')

