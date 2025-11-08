# -*- coding: utf-8 -*-
"""
Pytest 配置文件
提供测试固件（fixtures）
"""

import pytest
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User, Post, Photo, Comment, Anniversary


@pytest.fixture(scope='session')
def app():
    """创建测试应用"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """创建 CLI 运行器"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """创建数据库会话"""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username='testuser',
        display_name='测试用户',
        is_admin=False
    )
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_admin(db_session):
    """创建测试管理员"""
    admin = User(
        username='admin',
        display_name='管理员',
        is_admin=True
    )
    admin.set_password('admin123')
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def auth_client(client, test_user):
    """已登录的测试客户端"""
    client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    return client

