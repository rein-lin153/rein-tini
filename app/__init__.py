# -*- coding: utf-8 -*-
"""
心语时光 - Flask 应用工厂
使用工厂模式创建 Flask 应用实例
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from app.config import get_config
from app.extensions import db, login_manager, csrf, limiter
from app.models import enable_wal_mode


def create_app(config_name=None):
    """
    应用工厂函数
    
    Args:
        config_name: 配置名称（development/testing/production）
    
    Returns:
        Flask 应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(get_config())
    
    # 确保必要的目录存在（必须在初始化扩展之前！）
    # 特别是 instance 目录，SQLite 数据库需要它
    ensure_directories(app)
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册上下文处理器
    register_context_processors(app)
    
    # 注册上传文件的静态路由（开发环境）
    register_upload_handler(app)
    
    # 配置日志
    configure_logging(app)
    
    # 启用 SQLite WAL 模式
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        enable_wal_mode()
    
    return app


def ensure_directories(app):
    """确保必要的目录存在"""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['PHOTOS_FOLDER'],
        app.config['THUMBS_FOLDER'],
        app.config['BACKGROUNDS_FOLDER'],
        app.config.get('MUSIC_FOLDER', os.path.join(app.config['BASE_DIR'], 'app', 'static', 'music')),
        app.config.get('COVER_FOLDER', os.path.join(app.config['BASE_DIR'], 'app', 'static', 'music', 'covers')),
        app.config['BACKUP_DIR'],
        os.path.dirname(app.config['LOG_FILE']),
        os.path.join(app.config['BASE_DIR'], 'instance')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, mode=0o755)
                app.logger.info('创建目录: {}'.format(directory))
            except OSError as e:
                app.logger.error('创建目录失败 {}: {}'.format(directory, str(e)))


def init_extensions(app):
    """初始化 Flask 扩展"""
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # 注意：不在这里创建数据库表
    # 数据库表的创建应该由 init_db.py 脚本负责


def register_blueprints(app):
    """注册蓝图"""
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.album import bp as album_bp
    app.register_blueprint(album_bp, url_prefix='/album')
    
    from app.post import bp as post_bp
    app.register_blueprint(post_bp, url_prefix='/posts')
    
    from app.message import bp as message_bp
    app.register_blueprint(message_bp, url_prefix='/messages')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    
    if app.config['ENABLE_API']:
        from app.api import bp as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')


def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('errors/413.html'), 413


def register_context_processors(app):
    """注册上下文处理器（模板全局变量）"""
    
    @app.context_processor
    def inject_config():
        """注入配置到模板"""
        return {
            'SITE_TITLE': app.config['SITE_TITLE'],
            'SITE_SUBTITLE': app.config['SITE_SUBTITLE'],
            'COUPLE_NAME_1': app.config['COUPLE_NAME_1'],
            'COUPLE_NAME_2': app.config['COUPLE_NAME_2'],
            'TOGETHER_DATE': app.config['TOGETHER_DATE'],
            'ENABLE_BACKGROUND_MUSIC': app.config.get('ENABLE_BACKGROUND_MUSIC', True),
            'ENABLE_MESSAGE_BOARD': app.config['ENABLE_MESSAGE_BOARD'],
            'ENABLE_COMMENTS': app.config['ENABLE_COMMENTS']
        }
    
    @app.context_processor
    def inject_now():
        """注入当前时间到模板"""
        from datetime import datetime
        return {'now': datetime.utcnow()}


def register_upload_handler(app):
    """注册上传文件的静态服务（仅用于开发环境）"""
    from flask import send_from_directory
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """提供上传文件的访问"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def configure_logging(app):
    """配置日志系统"""
    if not app.debug and not app.testing:
        # 文件日志
        log_file = app.config['LOG_FILE']
        log_dir = os.path.dirname(log_file)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT'],
            encoding='utf-8'
        )
        
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        
        log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
        file_handler.setLevel(log_level)
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        app.logger.info('心语时光启动完成')

