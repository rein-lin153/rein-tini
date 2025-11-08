# -*- coding: utf-8 -*-
"""
API 蓝图初始化
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes

