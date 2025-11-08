# -*- coding: utf-8 -*-
"""
工具函数测试
"""

import pytest
from datetime import datetime, timedelta
from app.main.utils import get_days_together, get_next_anniversary, get_love_percentage


def test_get_days_together():
    """测试计算在一起天数"""
    # 使用固定日期进行测试
    start_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
    days = get_days_together(start_date)
    
    assert days >= 100
    assert days <= 101  # 考虑时区差异


def test_get_days_together_invalid_date():
    """测试无效日期"""
    days = get_days_together('invalid-date')
    assert days == 0


def test_get_next_anniversary():
    """测试获取下一个纪念日"""
    # 使用 50 天前的日期，下一个应该是 100 天纪念日
    start_date = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')
    next_ann = get_next_anniversary(start_date)
    
    assert next_ann is not None
    assert 'name' in next_ann
    assert 'days_left' in next_ann
    assert next_ann['days_left'] > 0


def test_get_love_percentage():
    """测试爱情进度百分比"""
    # 测试不同天数
    assert get_love_percentage(0) == 0
    assert get_love_percentage(1) > 0
    assert get_love_percentage(100) > get_love_percentage(10)
    assert get_love_percentage(1000) < 100  # 永远不到 100%


def test_get_love_percentage_consistency():
    """测试爱情进度的一致性"""
    result1 = get_love_percentage(100)
    result2 = get_love_percentage(100)
    
    assert result1 == result2  # 相同输入应得到相同输出

