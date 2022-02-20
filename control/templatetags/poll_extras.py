import pytz
from django import template
import random

from django.utils import timezone

register = template.Library()

@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp


@register.filter(name='splitter')
def splitter(text):
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


@register.simple_tag(name='plan')
def plan(obj, arg, group):
    if obj:
        plan = obj.get_plan(group)
        if plan:
            if arg == 'start':
                if plan.start:
                    return timezone.localtime(plan.start).strftime('%Y-%m-%d %H:%M')
            elif arg == 'end':
                if plan.end:
                    return timezone.localtime(plan.end).strftime('%Y-%m-%d %H:%M')
            elif arg == 'obj':
                return plan
    return ""


@register.filter(name='in_plan')
def in_plan(obj, group):
    return obj.in_plan(group)


@register.filter(name='is_passed')
def is_passed(obj, user):
    return obj.is_passed(user)


@register.filter(name='is_sended')
def is_sended(filetask, user):
    return filetask.is_sended(user)


@register.filter(name='is_owner')
def is_owner(course, user):
    return course.is_owner(user)


@register.filter(name='is_teacher')
def is_teacher(discipline, user):
    return discipline.is_teacher(user)