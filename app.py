# -*- coding: utf-8 -*-
"""
心语时光 - 开发服务器入口文件
仅用于开发和测试，生产环境请使用 wsgi.py
"""

import os
from app import create_app
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发服务器配置
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print('=' * 60)
    print('💖 心语时光 (HeartMoments) 正在启动...')
    print('=' * 60)
    print(f'环境: {os.environ.get("FLASK_ENV", "development")}')
    print(f'地址: http://{host}:{port}')
    print(f'调试模式: {"开启" if debug else "关闭"}')
    print('=' * 60)
    print('提示: 开发服务器仅用于开发测试')
    print('     生产环境请使用 Gunicorn + Nginx')
    print('=' * 60)
    
    app.run(host=host, port=port, debug=debug)

