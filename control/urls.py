"""study_control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from control.views import Index, Registration, Login, CourseDetail, CourseAdd, CourseEdit, UserEdit, UserAdd, \
    UserAdmin, CourseAdmin, GroupAdmin, UserDel, GroupAdd, LessonDetail, GroupDel, GroupEdit, Request, \
    Unrequest, GroupRequests, GroupStudents, DisciplineAdmin, DisciplineAdd, DisciplineEdit, LessonAdmin, LessonAdd, \
    LessonEdit, LessonDel, TestAdmin, TestAdd, TestEdit, TestDel, QuestionAdd, QuestionEdit, QuestionDel, TestView, \
    DirectionAdmin, DirectionAdd, DirectionEdit, DirectionDel, SyncTime, GroupTestAdd, GroupTestEdit, GroupTestDel, \
    GroupTestAdmin
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', Index.as_view(), name='index'),

    path('login/', Login.as_view(), name="login"),
    path('registration', Registration.as_view(), name='registration'),
    path("logout/", LogoutView.as_view(), {'next_page': '/'}, name="logout"),
    path('sync', SyncTime.as_view(), name='sync'),

    path('settings/direction', login_required(DirectionAdmin.as_view()), name='settings_directions'),
    path('settings/direction/add', login_required(DirectionAdd.as_view()), name='direction_add'),
    path('settings/direction/<int:pk>/edit', login_required(DirectionEdit.as_view()), name='direction_edit'),
    path('settings/direction/<int:pk>/del', login_required(DirectionDel.as_view()), name='direction_del'),

    path('course/<slug:slug>', CourseDetail.as_view(), name='course'),
    path('course/<slug:slug>/request', Request.as_view(), name="request"),
    path('course/<slug:slug>/unrequest', Unrequest.as_view(), name="unrequest"),
    path('course/<slug:slug>/lesson/<int:pk>', login_required(LessonDetail.as_view()), name='lesson'),
    path('course/<slug:slug>/test/<int:pk>', login_required(TestView.as_view()), name='test'),

    path('settings/courses', login_required(CourseAdmin.as_view()), name='settings_courses'),
    path('settings/course/add', login_required(CourseAdd.as_view()), name='course_add'),
    path('settings/course/<slug:slug>/edit', login_required(CourseEdit.as_view()), name='course_edit'),

    path('settings/disciplines', login_required(DisciplineAdmin.as_view()), name='settings_disciplines'),
    path('settings/discipline/add', login_required(DisciplineAdd.as_view()), name='discipline_add'),
    path('settings/discipline/<int:pk>/edit', login_required(DisciplineEdit.as_view()), name='discipline_edit'),

    path('settings/groups', login_required(GroupAdmin.as_view()), name='settings_groups'),
    path('settings/groups/add', login_required(GroupAdd.as_view()), name='group_add'),
    path('settings/groups/<int:pk>/edit', login_required(GroupEdit.as_view()), name='group_edit'),
    path('settings/groups/<int:pk>/del', login_required(GroupDel.as_view()), name='group_del'),
    path('settings/groups/<int:pk>/requests', login_required(GroupRequests.as_view()), name='requests_group'),
    path('settings/groups/<int:pk>/students', login_required(GroupStudents.as_view()), name='students_group'),

    path('settings/users', login_required(UserAdmin.as_view()), name='settings_users'),
    path('settings/users/add', login_required(UserAdd.as_view()), name='user_add'),
    #path('settings/users/<int:pk>', UserDetail.as_view(), name='user'),
    path('settings/users/<int:pk>/edit', login_required(UserEdit.as_view()), name='user_edit'),
    path('settings/users/<int:pk>/del', login_required(UserDel.as_view()), name='user_del'),

    path('settings/lessons', login_required(LessonAdmin.as_view()), name='settings_lessons'),
    path('settings/lesson/add', login_required(LessonAdd.as_view()), name='lesson_add'),
    path('settings/lesson/<int:pk>/edit', login_required(LessonEdit.as_view()), name='lesson_edit'),
    path('settings/lesson/<int:pk>/del', login_required(LessonDel.as_view()), name='lesson_del'),

    path('settings/tests', login_required(TestAdmin.as_view()), name='settings_tests'),
    path('settings/test/add', login_required(TestAdd.as_view()), name='test_add'),
    path('settings/test/<int:pk>/edit', login_required(TestEdit.as_view()), name='test_edit'),
    path('settings/test/<int:pk>/del', login_required(TestDel.as_view()), name='test_del'),

    path('settings/question/add', login_required(QuestionAdd.as_view()), name='question_add'),
    path('settings/question/<int:pk>/edit', login_required(QuestionEdit.as_view()), name='question_edit'),
    path('settings/question/<int:pk>/del', login_required(QuestionDel.as_view()), name='question_del'),

    path('settings/group-test', login_required(GroupTestAdmin.as_view()), name='group_test'),
    path('settings/group-test/add', login_required(GroupTestAdd.as_view()), name='group_test_add'),
    path('settings/group-test/edit', login_required(GroupTestEdit.as_view()), name='group_test_edit'),
    path('settings/group-test/<int:pk>/del', login_required(GroupTestDel.as_view()), name='group_test_del'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)