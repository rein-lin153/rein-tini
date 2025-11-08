# -*- coding: utf-8 -*-
"""
认证蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes

