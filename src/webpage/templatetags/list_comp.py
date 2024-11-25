from django import template

register = template.Library()


@register.filter
def list_comp(iter_value, attribute) -> list:
    """
    {{ Iter|list_comp:'attribute' }}
    """
    if hasattr(iter_value[0], attribute):
        return [x.__getattribute__(attribute) for x in iter_value]
    return []
