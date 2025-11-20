from django import template
from ..utils import get_zodiac_by_number

register = template.Library()

@register.filter(name='get_zodiac')
def get_zodiac(value):
    """获取数字对应的生肖"""
    return get_zodiac_by_number(value)
