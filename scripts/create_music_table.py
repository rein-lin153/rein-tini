#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建 Music 数据库表
运行此脚本创建 music 表
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Music


def create_music_table():
    """创建 Music 表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建表
            db.create_all()
            
            # 检查表是否创建成功
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'music' in tables:
                print("✅ Music 表创建成功！")
                
                # 显示表结构
                columns = inspector.get_columns('music')
                print("\n表结构：")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ Music 表创建失败！")
                
        except Exception as e:
            print(f"❌ 创建表时出错: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    create_music_table()

