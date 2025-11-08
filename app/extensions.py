# -*- coding: utf-8 -*-
"""
心语时光 - Flask 扩展初始化
集中管理所有 Flask 扩展实例
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 数据库实例
db = SQLAlchemy()

# 登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录访问此页面'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# CSRF 保护
csrf = CSRFProtect()

# 速率限制器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    from app.models import User
    return User.query.get(int(user_id))

