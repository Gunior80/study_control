from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DetailView, UpdateView, ListView

from control.forms import RegistrationForm, CourseForm, EditUser, ProfileForm, GroupAddForm, DisciplineAddForm
from control.models import Course, Discipline, Group, Lesson


class Index(TemplateView):
    template_name = 'control/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_courses'] = Course.objects.all()
        a_groups = Group.objects.all().filter(study_start__gt=datetime.now()).values('course').distinct()
        context['avaible_courses'] = context['all_courses'].filter(id__in=a_groups)
        return context


class Registration(View):

    def post(self, request):
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data.get('username')
            password = reg_form.cleaned_data.get('password')
            reg_form.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect('index')
        else:
            return render(request, 'control/registration.html', {
                'reg_form': reg_form,
            })

    def get(self, request):
        reg_form = RegistrationForm()
        return render(request, 'control/registration.html', {
            'reg_form': reg_form,
        })


class Login(View):

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"{username}, здравствуйте!")
                return redirect("index")
            else:
                messages.error(request, "Неверный логин или пароль.")
        else:
            messages.error(request, "Неверный логин или пароль.")
        return render(request, 'control/login.html', {
            'login_form': form,
        })

    def get(self, request):
        form = AuthenticationForm(request.POST)
        return render(request, 'control/login.html', {
            'login_form': form,
        })


class Request(View):
    # Запрос на включение в список группы
    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=request.POST.get('group_id'))
        user = request.user
        group.requests.add(user)
        return redirect('course', slug=kwargs['slug'])

class Unrequest(View):
    # Запрос на удаление заявки в список группы
    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=request.POST.get('group_id'))
        user = request.user
        group.requests.remove(user)
        return redirect('course', slug=kwargs['slug'])


class UserAdmin(TemplateView):
    template_name = 'control/settings/users.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


class UserAdd(View):

    def post(self, request):
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            reg_form.save()
            messages.error(request, "Пользователь успешно добавлен.")
            return redirect('settings_users')
        else:
            return render(request, 'control/registration.html', {
                'reg_form': reg_form,
            })

    def get(self, request):
        reg_form = RegistrationForm()
        return render(request, 'control/registration.html', {
            'reg_form': reg_form,
        })


class UserEdit(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            user = User.objects.get(pk=kwargs['pk'])
            user_form = EditUser(instance=user)
            profile_form = ProfileForm(instance=user.profile)
        else:
            user_form = EditUser(instance=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'control/settings/edit/profile_edit.html', {
                      'user_form': user_form,
                      'profile_form': profile_form
    })

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            user = User.objects.get(pk=kwargs['pk'])
            user_form = EditUser(request.POST, instance=user)
            profile_form = ProfileForm(request.POST, instance=user.profile)
        else:
            user_form = EditUser(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен')
            if request.user.is_staff:
                return redirect('settings_users')
        else:
            messages.error(request, 'Ошибка обновления профиля')
        return render(request, 'control/settings/edit/profile_edit.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })


class UserDel(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            user = User.objects.get(pk=kwargs['pk'])
        else:
            user = request.user
        user.delete()
        return redirect('settings_users')


class DashboardAdmin(TemplateView):
    template_name = 'control/settings/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


class CourseAdmin(TemplateView):
    template_name = 'control/settings/courses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        return context


class CourseDetail(DetailView):
    template_name = 'control/course.html'
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = context['course'].group.all().filter(study_start__gt=datetime.now())
        return context


class CourseAdd(View):

    def get(self, request, *args, **kwargs):
        form = CourseForm(request.POST)
        return render(request, 'control/settings/edit/course_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Курс создан.")
            return redirect('settings_courses')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/course_edit.html', {'form': form,})


class CourseEdit(UpdateView):
    model = Course
    template_name = 'control/settings/edit/course_edit.html'
    form_class = CourseForm

    def get_success_url(self):
        return reverse('settings_courses', args=None)



class GroupAdmin(TemplateView):
    template_name = 'control/settings/groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context


class GroupAdd(View):

    def get(self, request, *args, **kwargs):
        form = GroupAddForm(request.POST)
        return render(request, 'control/settings/edit/group_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = GroupAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Группа создана.")
            return redirect('settings_groups')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/group_edit.html', {'form': form,})


class GroupEdit(UpdateView):
    model = Group
    template_name = 'control/settings/edit/group_edit.html'
    form_class = GroupAddForm

    def get_success_url(self):
        return reverse('settings_groups', args=None)


class GroupRequests(View):

    def get(self, request, *args, **kwargs):
        group = Group.objects.get(pk=kwargs['pk'])
        return render(request, 'control/settings/edit/group_requests.html', {'group': group, })

    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=kwargs['pk'])
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken')
        group.add_students(data.dict())
        return redirect('settings_groups')


class GroupStudents(View):
    # Результаты обучения и меры
    def get(self, request, *args, **kwargs):
        group = Group.objects.get(pk=kwargs['pk'])
        i = User.objects.get(pk=1)
        return render(request, 'control/settings/edit/group_students.html', {'group': group, })

    def post(self, request, *args, **kwargs):
        group = Group.objects.get(pk=kwargs['pk'])
        user = User.objects.get(pk=request.POST.get("user_id"))
        group.students.remove(user)
        return redirect('students_group', pk=kwargs['pk'])


class GroupDel(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            group = Group.objects.get(pk=kwargs['pk'])
            group.delete()
        return redirect('settings_groups')


class DisciplineAdmin(TemplateView):
    template_name = 'control/settings/disciplines.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disciplines'] = Discipline.objects.all()
        return context


class DisciplineAdd(View):

    def get(self, request, *args, **kwargs):
        form = DisciplineAddForm(request.POST)
        return render(request, 'control/settings/edit/discipline_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = DisciplineAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Дисциплина создана.")
            return redirect('settings_disciplines')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/discipline_edit.html', {'form': form,})


class DisciplineEdit(UpdateView):
    model = Discipline
    template_name = 'control/settings/edit/discipline_edit.html'
    form_class = DisciplineAddForm

    def get_success_url(self):
        return reverse('settings_disciplines', args=None)


class LessonDetail(DetailView):
    template_name = 'control/lesson.html'
    model = Lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
