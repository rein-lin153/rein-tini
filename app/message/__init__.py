# -*- coding: utf-8 -*-
"""
留言板蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('message', __name__)

from app.message import routes

