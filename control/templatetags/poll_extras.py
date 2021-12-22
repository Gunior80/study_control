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

