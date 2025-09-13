from django import template

register = template.Library()


@register.filter
def add(value, arg):
    """Soma value + arg"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value
