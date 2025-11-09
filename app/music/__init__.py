# -*- coding: utf-8 -*-
"""
音乐模块 - 蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('music', __name__, url_prefix='/music')

from app.music import routes, routes_api

