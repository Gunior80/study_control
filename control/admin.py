from django.contrib import admin
from django.contrib.admin import AdminSite

from control.models import *


class MyAdminSite(AdminSite):
    site_header = 'Контроль обучения'
    site_url = None


test_admin = MyAdminSite(name='myadmin')

test_admin.register(Course)
test_admin.register(Discipline)
test_admin.register(Lesson)
test_admin.register(Group)
test_admin.register(User)
test_admin.register(Profile)
