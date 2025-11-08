# -*- coding: utf-8 -*-
"""
心语时光 - 数据库模型
包含所有数据表的 ORM 模型定义
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """用户模型（支持双用户：情侣二人）"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(64), nullable=False)  # 显示名称（如 Rein、Nana）
    avatar = db.Column(db.String(256))  # 头像路径
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='uploader', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码（哈希）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    """日记模型"""
    
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = db.Column(db.Boolean, default=False)  # 是否私密
    mood = db.Column(db.String(32))  # 心情标签（开心、感动、平淡等）
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic', 
                             foreign_keys='Comment.post_id', cascade='all, delete-orphan')
    
    @property
    def word_count(self):
        """计算字数（中文字符 + 英文单词）"""
        import re
        # 中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', self.body))
        # 英文单词（简单统计，按空格分隔）
        english_words = len(re.findall(r'[a-zA-Z]+', self.body))
        return chinese_chars + english_words
    
    @property
    def reading_time(self):
        """估算阅读时间（分钟），假设每分钟阅读 300 字"""
        minutes = max(1, round(self.word_count / 300))
        return minutes
    
    def __repr__(self):
        return '<Post {}>'.format(self.title)


class Photo(db.Model):
    """照片模型"""
    
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)  # 原图文件名
    thumb_filename = db.Column(db.String(256), nullable=False)  # 缩略图文件名
    caption = db.Column(db.String(256))  # 图片描述
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    width = db.Column(db.Integer)  # 原图宽度
    height = db.Column(db.Integer)  # 原图高度
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    location = db.Column(db.String(128))  # 拍摄地点
    
    # 关系
    comments = db.relationship('Comment', backref='photo', lazy='dynamic',
                             foreign_keys='Comment.photo_id', cascade='all, delete-orphan')
    
    def __repr__(self):
        return '<Photo {}>'.format(self.filename)


class Comment(db.Model):
    """评论/留言模型（可关联到 Post 或 Photo）"""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 可以评论日记或照片
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.id'), nullable=True)
    
    # 回复功能（评论可以回复评论）
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                            lazy='dynamic', cascade='all, delete-orphan')
    
    is_private = db.Column(db.Boolean, default=False)  # 是否私密留言
    
    def __repr__(self):
        return '<Comment {}>'.format(self.id)


class Anniversary(db.Model):
    """纪念日模型"""
    
    __tablename__ = 'anniversaries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)  # 纪念日名称（如：相识日、确定关系日）
    date = db.Column(db.Date, nullable=False, index=True)
    recurrence = db.Column(db.String(16), default='annual')  # annual（年度）、once（一次性）
    description = db.Column(db.Text)  # 描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Anniversary {}>'.format(self.name)


class SiteSetting(db.Model):
    """站点设置模型（键值对存储）"""
    
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get(key, default=None):
        """获取配置值"""
        setting = SiteSetting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value):
        """设置配置值"""
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return '<SiteSetting {}={}>'.format(self.key, self.value[:20] if self.value else '')


# 数据库初始化辅助函数
def init_db():
    """初始化数据库（创建表）"""
    db.create_all()
    print("数据库表创建完成！")


def enable_wal_mode():
    """启用 SQLite WAL 模式以提高并发性能"""
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        if 'sqlite' in str(dbapi_conn):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=30000000000")
            cursor.close()
    
    print("SQLite WAL 模式已启用！")

