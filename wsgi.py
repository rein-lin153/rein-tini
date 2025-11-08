# -*- coding: utf-8 -*-
"""
心语时光 - WSGI 入口文件
用于 Gunicorn 等 WSGI 服务器
"""

import os
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 创建应用实例
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()

