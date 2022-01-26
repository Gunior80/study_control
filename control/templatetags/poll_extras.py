from django import template
import random

register = template.Library()

@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp


@register.filter(name='splitter')
def splitter(text):
    print(text)
    if len(text) > 50:
        return text[0:49]+'...'
    else:
        return text

@register.filter(name='count_of_true_param')
def count_of_true_param(values, arg):
    count = 0
    for value in values:
        if getattr(value, arg):
            count += 1
    return count


