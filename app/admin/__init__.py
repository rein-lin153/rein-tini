# -*- coding: utf-8 -*-
"""
管理员蓝图
"""

from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin import routes

