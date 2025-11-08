# -*- coding: utf-8 -*-
"""
数据模型测试
"""

import pytest
from app.models import User, Post, Photo, Comment, Anniversary
from datetime import datetime, date


def test_user_password_hashing(db_session):
    """测试用户密码哈希"""
    user = User(username='test', display_name='Test')
    user.set_password('password123')
    
    assert user.password_hash is not None
    assert user.password_hash != 'password123'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')


def test_create_user(db_session):
    """测试创建用户"""
    user = User(
        username='newuser',
        display_name='新用户',
        is_admin=False
    )
    user.set_password('password123')
    
    db_session.add(user)
    db_session.commit()
    
    saved_user = User.query.filter_by(username='newuser').first()
    assert saved_user is not None
    assert saved_user.display_name == '新用户'
    assert saved_user.is_admin is False


def test_create_post(db_session, test_user):
    """测试创建日记"""
    post = Post(
        title='测试日记',
        body='这是测试内容',
        author_id=test_user.id,
        mood='happy'
    )
    
    db_session.add(post)
    db_session.commit()
    
    saved_post = Post.query.filter_by(title='测试日记').first()
    assert saved_post is not None
    assert saved_post.author_id == test_user.id
    assert saved_post.mood == 'happy'


def test_post_author_relationship(db_session, test_user):
    """测试日记和作者的关系"""
    post = Post(
        title='测试关系',
        body='内容',
        author_id=test_user.id
    )
    
    db_session.add(post)
    db_session.commit()
    
    assert post.author.username == 'testuser'
    assert post in test_user.posts.all()


def test_create_comment(db_session, test_user):
    """测试创建评论"""
    post = Post(title='日记', body='内容', author_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    
    comment = Comment(
        body='评论内容',
        author_id=test_user.id,
        post_id=post.id
    )
    
    db_session.add(comment)
    db_session.commit()
    
    assert comment.post_id == post.id
    assert comment.author_id == test_user.id
    assert post.comments.count() == 1


def test_create_anniversary(db_session):
    """测试创建纪念日"""
    anniversary = Anniversary(
        name='相识纪念日',
        date=date(2023, 1, 14),
        recurrence='annual',
        description='我们相识的日子'
    )
    
    db_session.add(anniversary)
    db_session.commit()
    
    saved = Anniversary.query.filter_by(name='相识纪念日').first()
    assert saved is not None
    assert saved.recurrence == 'annual'

