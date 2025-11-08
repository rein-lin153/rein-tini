# -*- coding: utf-8 -*-
"""
日记表单
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class PostForm(FlaskForm):
    """日记表单"""
    title = StringField('标题', validators=[
        DataRequired(message='请输入标题'),
        Length(min=1, max=128, message='标题长度应在 1-128 个字符之间')
    ])
    body = TextAreaField('正文', validators=[
        DataRequired(message='请输入正文内容'),
        Length(min=1, message='正文不能为空')
    ])
    mood = SelectField('心情', choices=[
        ('', '不设置'),
        ('happy', '😊 开心'),
        ('love', '💖 甜蜜'),
        ('moved', '😭 感动'),
        ('calm', '😌 平静'),
        ('excited', '🤩 兴奋'),
        ('sad', '😔 难过'),
        ('thoughtful', '🤔 思考')
    ], validators=[Optional()])
    is_private = BooleanField('设为私密（仅自己可见）')
    submit = SubmitField('发布')

