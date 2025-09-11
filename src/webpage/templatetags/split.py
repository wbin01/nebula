from django import template

register = template.Library()


@register.filter
def split(value, arg):
    """
    {{ "a,b,c"|split:"," }}
    {{ "a,b,c"|split:",|0" }}
    """
    if '|' in arg:
        arg, index = arg.split('|')
        return value.split(arg)[int(index)]
    return value.split(arg)
