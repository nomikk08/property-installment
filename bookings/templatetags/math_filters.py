from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return value - arg
    except:
        return 0
