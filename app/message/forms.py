# -*- coding: utf-8 -*-
"""
留言板表单
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class MessageForm(FlaskForm):
    """留言表单"""
    body = TextAreaField('留言内容', validators=[
        DataRequired(message='请输入留言内容'),
        Length(min=1, max=500, message='留言长度应在 1-500 个字符之间')
    ])
    is_private = BooleanField('私密留言（仅我们可见）')
    submit = SubmitField('发送')

