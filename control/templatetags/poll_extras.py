import pytz
from django import template
import random

from django.utils import timezone

from study_control import settings

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

@register.filter(name='collide_lesson')
def collide_lesson(groupplan, arg):
    if groupplan:
        curr = groupplan.filter(lesson=str(arg)).first()
        if curr:
            if curr.start:
                return timezone.localtime(curr.start).strftime('%Y-%m-%d %H:%M')
    return ""

@register.filter(name='collide_test_start')
def collide_test_start(testplan, arg):
    if testplan:
        curr = testplan.filter(test=str(arg)).first()
        if curr:
            if curr.start:
                return timezone.localtime(curr.start).strftime('%Y-%m-%d %H:%M')
    return ""

@register.filter(name='collide_test_end')
def collide_test_end(testplan, arg):
    if testplan:
        curr = testplan.filter(test=str(arg)).first()
        if curr:
            if curr.end:
                return timezone.localtime(curr.end).strftime('%Y-%m-%d %H:%M')
    return ""

@register.filter(name='collide_file_start')
def collide_file_start(fileplan, arg):
    if fileplan:
        curr = fileplan.filter(file=str(arg)).first()
        if curr:
            if curr.start:
                return timezone.localtime(curr.start).strftime('%Y-%m-%d %H:%M')
    return ""

@register.filter(name='collide_file_end')
def collide_file_end(fileplan, arg):
    if fileplan:
        curr = fileplan.filter(file=str(arg)).first()
        if curr:
            if curr.end:
                return timezone.localtime(curr.end).strftime('%Y-%m-%d %H:%M')
    return ""

@register.filter(name='studied_user')
def studied_user(course, user):
    if not user.is_authenticated:
        return False
    return course.studied_user(user)

@register.filter(name='in_discipline_plan')
def dicsipline_in_group_plan(dicsipline, group):
    return dicsipline.is_group_plan(group)

@register.filter(name='in_lesson_plan')
def lesson_in_group_plan(lesson, group):
    return lesson.is_group_plan(group)

@register.filter(name='is_passed')
def is_passed(test, user):
    return test.is_passed(user)

@register.filter(name='is_accepted')
def is_accepted(filetask, user):
    return filetask.is_passed(user)

@register.filter(name='is_owner')
def is_owner(course, user):
    return course.is_owner(user)

@register.filter(name='is_teacher')
def is_teacher(discipline, user):
    return discipline.is_teacher(user)