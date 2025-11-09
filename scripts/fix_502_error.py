#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 502 错误脚本
自动诊断并修复常见问题
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_database_table():
    """检查数据库表是否存在"""
    try:
        from app import create_app, db
        from app.models import Music
        from sqlalchemy import inspect
        
        app = create_app()
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'music' in tables:
                print("✅ Music 表已存在")
                return True
            else:
                print("❌ Music 表不存在")
                return False
    except Exception as e:
        print(f"❌ 检查数据库表时出错: {str(e)}")
        return False

def create_music_table():
    """创建 Music 表"""
    try:
        from app import create_app, db
        from app.models import Music
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Music 表创建成功")
            return True
    except Exception as e:
        print(f"❌ 创建表时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_imports():
    """检查导入是否正确"""
    errors = []
    
    try:
        from app.models import Music
        print("✅ 可以导入 Music 模型")
    except Exception as e:
        print(f"❌ 无法导入 Music 模型: {str(e)}")
        errors.append(f"Music 模型导入失败: {str(e)}")
    
    try:
        from app.music.models_db import MusicManager
        print("✅ 可以导入 MusicManager")
    except Exception as e:
        print(f"❌ 无法导入 MusicManager: {str(e)}")
        errors.append(f"MusicManager 导入失败: {str(e)}")
    
    try:
        from app.music import routes_api
        print("✅ 可以导入 routes_api")
    except Exception as e:
        print(f"❌ 无法导入 routes_api: {str(e)}")
        errors.append(f"routes_api 导入失败: {str(e)}")
    
    return len(errors) == 0, errors

def check_app_startup():
    """检查应用是否可以启动"""
    try:
        from app import create_app
        app = create_app()
        print("✅ 应用可以正常创建")
        return True
    except Exception as e:
        print(f"❌ 应用创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("502 错误诊断和修复工具")
    print("=" * 60)
    print()
    
    # 检查导入
    print("1. 检查模块导入...")
    imports_ok, import_errors = check_imports()
    print()
    
    if not imports_ok:
        print("❌ 导入检查失败，请先修复导入错误：")
        for error in import_errors:
            print(f"   - {error}")
        return 1
    
    # 检查应用启动
    print("2. 检查应用启动...")
    if not check_app_startup():
        print("❌ 应用无法启动，请检查错误信息")
        return 1
    print()
    
    # 检查数据库表
    print("3. 检查数据库表...")
    table_exists = check_database_table()
    print()
    
    if not table_exists:
        print("4. 创建数据库表...")
        if create_music_table():
            print("✅ 数据库表创建成功")
        else:
            print("❌ 数据库表创建失败")
            return 1
        print()
    else:
        print("✅ 数据库表已存在，无需创建")
        print()
    
    # 最终检查
    print("5. 最终验证...")
    table_exists = check_database_table()
    imports_ok, _ = check_imports()
    app_ok = check_app_startup()
    
    print()
    print("=" * 60)
    if table_exists and imports_ok and app_ok:
        print("✅ 所有检查通过！应用应该可以正常启动了。")
        print()
        print("下一步：")
        print("1. 重启应用：sudo systemctl restart heartmoments")
        print("2. 或重新启动 Gunicorn")
        print("3. 检查日志：tail -f logs/heartmoments.log")
        return 0
    else:
        print("❌ 仍有问题需要解决")
        return 1

if __name__ == '__main__':
    sys.exit(main())

