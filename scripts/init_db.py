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
    print('=' * 60)
    print('💖 心语时光 - 数据库初始化')
    print('=' * 60)
    
    # 在创建 app 之前，先确保 instance 目录存在
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instance_dir = os.path.join(project_root, 'instance')
    
    if not os.path.exists(instance_dir):
        print(f'\n创建 instance 目录: {instance_dir}')
        os.makedirs(instance_dir, mode=0o755)
    else:
        print(f'\n✓ instance 目录已存在: {instance_dir}')
    
    # 检查目录权限
    try:
        test_file = os.path.join(instance_dir, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f'✓ instance 目录可写')
    except Exception as e:
        print(f'✗ instance 目录不可写: {e}')
        print(f'\n请运行以下命令修复权限：')
        print(f'  chmod 755 {instance_dir}')
        print(f'  chown $USER:$USER {instance_dir}')
        return
    
    print('\n正在创建 Flask 应用...')
    app = create_app()
    
    with app.app_context():
        print(f'数据库 URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        print()
        
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

