# -*- coding: utf-8 -*-
"""
相册表单
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import Optional, Length


class PhotoUploadForm(FlaskForm):
    """单张照片上传表单"""
    photo = FileField('选择照片', validators=[
        FileRequired(message='请选择一张照片'),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], message='仅支持 JPG、PNG、WebP、GIF 格式')
    ])
    caption = StringField('照片描述', validators=[
        Optional(),
        Length(max=256, message='描述最多 256 个字符')
    ])
    location = StringField('拍摄地点', validators=[
        Optional(),
        Length(max=128, message='地点最多 128 个字符')
    ])
    submit = SubmitField('上传')


class BatchPhotoUploadForm(FlaskForm):
    """批量照片上传表单"""
    photos = MultipleFileField('选择多张照片', validators=[
        FileRequired(message='请至少选择一张照片')
    ])
    submit = SubmitField('批量上传')


class PhotoEditForm(FlaskForm):
    """照片编辑表单"""
    caption = StringField('照片描述', validators=[
        Optional(),
        Length(max=256, message='描述最多 256 个字符')
    ])
    location = StringField('拍摄地点', validators=[
        Optional(),
        Length(max=128, message='地点最多 128 个字符')
    ])
    submit = SubmitField('保存')

