# -*- coding: utf-8 -*-
"""
API 接口测试
"""

import pytest
import json


def test_api_status(client):
    """测试状态接口"""
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'couple_names' in data
    assert 'days_together' in data
    assert 'next_anniversary' in data


def test_api_get_posts(client, db_session, test_user):
    """测试获取日记列表"""
    from app.models import Post
    
    # 创建测试日记
    post = Post(title='API测试', body='内容', author_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    
    response = client.get('/api/posts')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'posts' in data
    assert 'pagination' in data
    assert len(data['posts']) > 0


def test_api_get_single_post(client, db_session, test_user):
    """测试获取单篇日记"""
    from app.models import Post
    
    post = Post(title='API测试', body='内容', author_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    
    response = client.get(f'/api/posts/{post.id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['title'] == 'API测试'
    assert data['body'] == '内容'


def test_api_get_photos(client):
    """测试获取照片列表"""
    response = client.get('/api/photos')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'photos' in data
    assert 'pagination' in data


def test_api_get_anniversaries(client):
    """测试获取纪念日列表"""
    response = client.get('/api/anniversaries')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'anniversaries' in data
    assert isinstance(data['anniversaries'], list)

