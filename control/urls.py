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
from django.urls import path
from control.views import Index, Registration, Login, CourseDetail, CourseAdd, CourseEdit, Settings, UserAdd, UserEdit
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('login/', Login.as_view(), name="login"),
    path('registration', Registration.as_view(), name='registration'),

    path("logout/", LogoutView.as_view(), {'next_page': '/'}, name="logout"),
    path('course/add', CourseAdd.as_view(), name='course_add'),
    path('course/<slug:slug>', CourseDetail.as_view(), name='course'),
    path('course/<slug:slug>/edit', CourseEdit.as_view(), name='course_edit'),
    path('settings', Settings.as_view(), name='settings'),
    path('user/add', UserAdd.as_view(), name='user_add'),
    #path('user/<int:pk>', UserDetail.as_view(), name='user'),
    path('user/<int:pk>/edit', UserEdit.as_view(), name='user_edit'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)