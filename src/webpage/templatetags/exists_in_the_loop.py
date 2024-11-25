from django import template

register = template.Library()


@register.filter
def exists_in_the_loop(iter_value, break_value_and_type) -> bool:
    """
    Replacing filter
    Use:
     `{{ "aaa"|exists_in_the_loop:"value|str" }}`
     `{{ [1, 2]|exists_in_the_loop:"2|int" }}`
     `{{ (1, 2)|exists_in_the_loop:"2.0|float" }}`
     `{{ Iter|exists_in_the_loop:"False|bool" }}`
    """
    if len(break_value_and_type.split('|')) != 2:
        return iter_value

    break_, type_ = break_value_and_type.split('|')
    for item in iter_value:
        if type_ == 'str':
            if item == break_:
                return True

        elif type_ == 'int':
            if item == int(break_):
                return True

        elif type_ == 'float':
            if item == float(break_):
                return True

        elif type_ == 'bool':
            if not item and break_ == 'False':
                return True

            elif item and break_ == 'True':
                return True

    return False
