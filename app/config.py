# -*- coding: utf-8 -*-
"""
心语时光 - 配置文件
支持多环境配置（开发/测试/生产）
"""

import os
from datetime import timedelta


class Config:
    """基础配置类"""
    
    # ========== 核心配置 ==========
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # ========== 数据库配置 ==========
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'heartmoments.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # SQLite 优化配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False,
            'timeout': 10
        },
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    # ========== 情侣信息 ==========
    COUPLE_NAME_1 = os.environ.get('COUPLE_NAME_1', 'Rein')
    COUPLE_NAME_2 = os.environ.get('COUPLE_NAME_2', 'Nana')
    TOGETHER_DATE = os.environ.get('TOGETHER_DATE', '2025-02-20')  # YYYY-MM-DD
    
    # ========== 文件上传配置 ==========
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'photos')
    THUMBS_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbs')
    BACKGROUNDS_FOLDER = os.path.join(UPLOAD_FOLDER, 'backgrounds')

    # ========== 音乐文件配置 ==========
    MUSIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music')
    COVER_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'music', 'covers')
    BACKGROUND_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'backgrounds')
    ALLOWED_MUSIC_EXTENSIONS = {'mp3'}  # 仅支持 MP3
    ALLOWED_MUSIC_EXT = ALLOWED_MUSIC_EXTENSIONS  # 别名
    ALLOWED_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    ALLOWED_IMAGE_EXT = ALLOWED_COVER_EXTENSIONS  # 别名
    MAX_MUSIC_SIZE = int(os.environ.get('MAX_MUSIC_SIZE', 30 * 1024 * 1024))  # 30MB
    MAX_COVER_SIZE = int(os.environ.get('MAX_COVER_SIZE', 2 * 1024 * 1024))  # 2MB
    
    # 管理员上传令牌
    ADMIN_UPLOAD_TOKEN = os.environ.get('ADMIN_UPLOAD_TOKEN', 'changeme123')
    
    # 文件大小限制（30MB，用于音乐上传）
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 30 * 1024 * 1024))
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
    
    # 图片处理配置
    THUMBNAIL_WIDTH = int(os.environ.get('THUMBNAIL_WIDTH', 300))
    MAX_IMAGE_WIDTH = int(os.environ.get('MAX_IMAGE_WIDTH', 1200))
    JPEG_QUALITY = int(os.environ.get('JPEG_QUALITY', 75))
    
    # ========== 分页配置 ==========
    PHOTOS_PER_PAGE = int(os.environ.get('PHOTOS_PER_PAGE', 20))
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', 10))
    MESSAGES_PER_PAGE = int(os.environ.get('MESSAGES_PER_PAGE', 15))
    
    # ========== 会话配置 ==========
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 7)))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # 生产环境使用 HTTPS 时启用
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # ========== CSRF 配置 ==========
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = None  # 不限制 CSRF token 时间
    
    # ========== 速率限制配置 ==========
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 15))
    
    # ========== 站点设置 ==========
    SITE_TITLE = os.environ.get('SITE_TITLE', '心语时光')
    SITE_SUBTITLE = os.environ.get('SITE_SUBTITLE', '记录我们的美好瞬间')
    TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Shanghai')
    
    # ========== 日志配置 ==========
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, os.environ.get('LOG_FILE', 'logs/heartmoments.log'))
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # ========== 备份配置 ==========
    BACKUP_DIR = os.path.join(BASE_DIR, os.environ.get('BACKUP_DIR', 'backups'))
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    
    # ========== 功能开关 ==========
    ENABLE_BACKGROUND_MUSIC = os.environ.get('ENABLE_BACKGROUND_MUSIC', 'True').lower() == 'true'
    ENABLE_MESSAGE_BOARD = os.environ.get('ENABLE_MESSAGE_BOARD', 'True').lower() == 'true'
    ENABLE_API = os.environ.get('ENABLE_API', 'True').lower() == 'true'
    ENABLE_COMMENTS = os.environ.get('ENABLE_COMMENTS', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境强制要求设置 SECRET_KEY
    # 注意：在部署到生产环境前，务必在 .env 中设置 SECRET_KEY


# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """获取当前配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

