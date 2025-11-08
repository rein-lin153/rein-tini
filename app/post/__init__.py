# -*- coding: utf-8 -*-
"""
日记蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('post', __name__)

from app.post import routes

