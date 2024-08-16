from django import template


register = template.Library()


@register.filter
def times(number:int, norating=None):
    try:
        if not norating:
            return 'a'*number
        return range(5 - number)
    except (TypeError, ValueError):
        return number