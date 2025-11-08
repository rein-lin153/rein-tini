# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建所有数据表并启用 SQLite 优化
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量（必须在导入 app 之前！）
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import enable_wal_mode

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('💖 心语时光 - 数据库初始化')
        print('=' * 60)
        
        # 启用 WAL 模式（仅 SQLite）
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            print('检测到 SQLite 数据库，启用 WAL 模式...')
            enable_wal_mode()
        
        # 创建所有表
        print('正在创建数据库表...')
        db.create_all()
        print('✓ 数据库表创建完成')
        
        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print('\n已创建的表:')
        for table in tables:
            print(f'  - {table}')
        
        print('\n' + '=' * 60)
        print('✓ 数据库初始化完成！')
        print('=' * 60)
        print('\n下一步:')
        print('  1. 运行 scripts/create_admin.py 创建管理员账户')
        print('  2. 运行 python app.py 启动开发服务器')
        print('=' * 60)


if __name__ == '__main__':
    init_database()

