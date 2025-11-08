# -*- coding: utf-8 -*-
"""
创建管理员用户脚本
"""

import os
import sys
import getpass

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_admin():
    """创建管理员用户"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('💖 心语时光 - 创建管理员账户')
        print('=' * 60)
        
        # 检查是否已有用户
        user_count = User.query.count()
        if user_count >= 2:
            print('⚠️  警告: 已存在 2 个用户')
            response = input('是否继续创建新用户？(y/N): ')
            if response.lower() != 'y':
                print('已取消')
                return
        
        # 输入用户信息
        print('\n请输入用户信息:')
        username = input('用户名: ').strip()
        
        if not username:
            print('❌ 用户名不能为空')
            return
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            print(f'❌ 用户名 {username} 已存在')
            return
        
        display_name = input('显示名称 (如: Rein): ').strip()
        if not display_name:
            display_name = username
        
        # 输入密码（隐藏）
        while True:
            password = getpass.getpass('密码: ')
            if len(password) < 6:
                print('❌ 密码至少需要 6 个字符，请重新输入')
                continue
            
            password_confirm = getpass.getpass('确认密码: ')
            if password != password_confirm:
                print('❌ 两次密码不一致，请重新输入')
                continue
            
            break
        
        # 是否为管理员
        is_admin_input = input('是否设为管理员？(Y/n): ').strip().lower()
        is_admin = is_admin_input != 'n'
        
        # 创建用户
        user = User(
            username=username,
            display_name=display_name,
            is_admin=is_admin
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            print('\n' + '=' * 60)
            print('✓ 用户创建成功！')
            print('=' * 60)
            print(f'用户名: {username}')
            print(f'显示名称: {display_name}')
            print(f'管理员权限: {"是" if is_admin else "否"}')
            print('=' * 60)
            print('\n您现在可以使用此账户登录系统')
            print(f'登录地址: http://localhost:5000/auth/login')
            print('=' * 60)
        
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ 创建失败: {str(e)}')


if __name__ == '__main__':
    create_admin()

