# -*- coding: utf-8 -*-
"""
音乐模块 - 蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('music', __name__, url_prefix='/music')

from app.music import routes
# 注意：routes_api 已移除，API 路由现在在 routes.py 中

