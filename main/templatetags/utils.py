from django import template
register = template.Library()

@register.filter(name='convert_to_eth')
def convert_to_eth(value):
    return (int(value) / 10 ** 18)

@register.filter(name='convert_to_custom')
def convert_to_custom(value, decimals):
    return (int(value) / 10 ** int(decimals))

@register.filter(name='subtract')
def subtract(x, y):
    return int(x) - int(y)

@register.filter(name='add')
def add(x, y):
    return float(x) + float(y)

@register.filter(name='to_fixed')
def to_fixed(value):
    return round(float(value), 2)