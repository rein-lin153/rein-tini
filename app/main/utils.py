# -*- coding: utf-8 -*-
"""
主页工具函数（日期计算等）
"""

from datetime import datetime, date, timedelta
import pytz


def get_days_together(start_date_str, timezone='Asia/Shanghai'):
    """
    计算在一起的天数
    
    Args:
        start_date_str: 开始日期字符串（YYYY-MM-DD）
        timezone: 时区
    
    Returns:
        在一起的天数
    """
    try:
        tz = pytz.timezone(timezone)
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        today = datetime.now(tz).date()
        delta = today - start_date
        return delta.days
    except Exception as e:
        return 0


def get_next_anniversary(start_date_str, timezone='Asia/Shanghai'):
    """
    获取下一个重要纪念日（如 100 天、1 年、2 年等）
    
    Args:
        start_date_str: 开始日期字符串（YYYY-MM-DD）
        timezone: 时区
    
    Returns:
        字典包含 name（名称）、date（日期）、days_left（剩余天数）
    """
    try:
        tz = pytz.timezone(timezone)
        start_date = datetime.strptime(start_date_str, '%Y-%m-% d').date()
        today = datetime.now(tz).date()
        days_together = (today - start_date).days
        
        # 定义重要纪念日里程碑
        milestones = [
            (100, '100天纪念日'),
            (365, '1周年纪念日'),
            (500, '500天纪念日'),
            (730, '2周年纪念日'),
            (1000, '1000天纪念日'),
            (1095, '3周年纪念日'),
            (1460, '4周年纪念日'),
            (1825, '5周年纪念日'),
        ]
        
        # 找到下一个未到的纪念日
        for days, name in milestones:
            if days_together < days:
                anniversary_date = start_date + timedelta(days=days)
                days_left = (anniversary_date - today).days
                return {
                    'name': name,
                    'date': anniversary_date,
                    'days_left': days_left
                }
        
        # 如果超过所有预设里程碑，计算下一个整年纪念日
        years_together = days_together // 365
        next_year = years_together + 1
        next_anniversary_date = start_date + timedelta(days=next_year * 365)
        days_left = (next_anniversary_date - today).days
        
        return {
            'name': '{}周年纪念日'.format(next_year),
            'date': next_anniversary_date,
            'days_left': days_left
        }
    
    except Exception as e:
        return {
            'name': '计算错误',
            'date': None,
            'days_left': 0
        }


def format_date_chinese(date_obj):
    """
    格式化日期为中文
    
    Args:
        date_obj: date 对象
    
    Returns:
        中文格式日期（如：2023年1月14日）
    """
    if date_obj:
        return '{}年{}月{}日'.format(date_obj.year, date_obj.month, date_obj.day)
    return ''


def get_love_percentage(days_together):
    """
    计算爱情进度百分比（趣味功能）
    
    Args:
        days_together: 在一起的天数
    
    Returns:
        百分比（0-100）
    """
    # 简单的增长曲线，永远接近但不到 100%
    if days_together <= 0:
        return 0
    
    # 使用对数函数，让增长逐渐变缓
    import math
    percentage = min(99.99, 50 + 10 * math.log10(days_together + 1))
    return round(percentage, 2)

