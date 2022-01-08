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
    DashboardAdmin, UserAdmin, CourseAdmin, GroupAdmin, UserDel, GroupAdd, LessonDetail
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', Index.as_view(), name='index'),

    path('login/', Login.as_view(), name="login"),
    path('registration', Registration.as_view(), name='registration'),
    path("logout/", LogoutView.as_view(), {'next_page': '/'}, name="logout"),

    path('course/add', CourseAdd.as_view(), name='course_add'),
    path('course/<slug:slug>', CourseDetail.as_view(), name='course'),
    path('course/<slug:slug>/edit', CourseEdit.as_view(), name='course_edit'),

    path('course/<slug:slug>/lesson/<int:pk>', login_required(LessonDetail.as_view()), name='lesson'),

    path('settings/dashboard', login_required(DashboardAdmin.as_view()), name='settings_dashboard'),
    path('settings/users', login_required(UserAdmin.as_view()), name='settings_users'),
    path('settings/groups', login_required(GroupAdmin.as_view()), name='settings_groups'),
    path('settings/courses', login_required(CourseAdmin.as_view()), name='settings_courses'),

    path('settings/groups/add', GroupAdd.as_view(), name='group_add'),

    path('user/add', UserAdd.as_view(), name='user_add'),
    #path('user/<int:pk>', UserDetail.as_view(), name='user'),
    path('user/<int:pk>/edit', login_required(UserEdit.as_view()), name='user_edit'),
    path('user/<int:pk>/del', login_required(UserDel.as_view()), name='user_del'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)