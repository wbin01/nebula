from django import template

register = template.Library()


@register.filter
def dict_key(value, arg):
    """
    {{ dict|dict_key:"key" }}
    """
    return value[arg]
