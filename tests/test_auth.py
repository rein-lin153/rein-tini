# -*- coding: utf-8 -*-
"""
认证功能测试
"""

import pytest
from flask import session


def test_login_page(client):
    """测试登录页面是否可访问"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert '登录'.encode('utf-8') in response.data


def test_login_success(client, test_user):
    """测试成功登录"""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert '欢迎回来'.encode('utf-8') in response.data


def test_login_invalid_username(client):
    """测试无效用户名"""
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    
    assert '用户名或密码错误'.encode('utf-8') in response.data


def test_login_invalid_password(client, test_user):
    """测试无效密码"""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
        'remember_me': False
    }, follow_redirects=True)
    
    assert '用户名或密码错误'.encode('utf-8') in response.data


def test_logout(auth_client):
    """测试登出"""
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert '退出登录'.encode('utf-8') in response.data

