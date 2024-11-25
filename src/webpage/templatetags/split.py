from django import template

register = template.Library()


@register.filter
def split(value, arg):
    """
    {{ "a,b,c"|split:"," }}
    """
    return value.split(arg)
