# -*- coding: utf-8 -*-
"""
相册蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('album', __name__)

from app.album import routes

