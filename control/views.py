from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DetailView, UpdateView, ListView, CreateView

from control.forms import RegistrationForm, CourseForm, EditUser, ProfileForm, GroupAddForm, DisciplineAddForm, \
    LessonAddForm, TestAddForm, QuestionAddForm, AnswerAddForm, DirectionAddForm
from control.models import Course, Discipline, Group, Lesson, Test, Question, Answer, Direction, GroupTest

from filebrowser.sites import site

class Index(TemplateView):
    template_name = 'control/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_courses'] = Course.objects.all()
        a_groups = Group.objects.all().filter(study_start__gt=datetime.now()).values('course').distinct()
        context['avaible_courses'] = context['all_courses'].filter(id__in=a_groups)
        context['directions'] = Direction.objects.all()
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


class DirectionAdmin(TemplateView):
    template_name = 'control/settings/directions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['directions'] = Direction.objects.all()
        return context


class DirectionAdd(View):

    def get(self, request, *args, **kwargs):
        form = DirectionAddForm(request.POST)
        return render(request, 'control/settings/edit/direction_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = DirectionAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Направление создано.")
            return redirect('settings_directions')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/direction_edit.html', {'form': form,})


class DirectionEdit(UpdateView):
    model = Direction
    template_name = 'control/settings/edit/direction_edit.html'
    form_class = DirectionAddForm

    def get_success_url(self):
        return reverse('settings_directions', args=None)


class DirectionDel(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            direction = Direction.objects.get(pk=kwargs['pk'])
            direction.delete()
        return redirect('settings_directions')


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
        context['tests'] = Test.objects.all().filter(lesson=context['lesson'].id)
        return context


class LessonAdmin(TemplateView):
    template_name = 'control/settings/lessons.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = Lesson.objects.all()
        return context


class LessonAdd(View):

    def get(self, request, *args, **kwargs):
        form = LessonAddForm(request.POST)
        return render(request, 'control/settings/edit/lesson_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = LessonAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Занятие создано.")
            return redirect('settings_lessons')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/lesson_edit.html', {'form': form,})


class LessonEdit(UpdateView):
    model = Lesson
    template_name = 'control/settings/edit/lesson_edit.html'
    form_class = LessonAddForm

    def get_success_url(self):
        return reverse('settings_lessons', args=None)


class LessonDel(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            group = Lesson.objects.get(pk=kwargs['pk'])
            group.delete()
        return redirect('settings_lessons')


class TestAdmin(TemplateView):
    template_name = 'control/settings/tests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = Test.objects.all()
        return context


class TestAdd(CreateView):
    model = Test
    form_class = TestAddForm
    template_name = 'control/settings/edit/test_edit.html'

    def form_valid(self, form):
        test = form.save(commit=False)
        test.save()
        return redirect('test_edit', pk=test.id)


class TestEdit(UpdateView):
    model = Test
    template_name = 'control/settings/edit/test_edit.html'
    form_class = TestAddForm
    def get_success_url(self):
        return reverse('settings_tests', args=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = Question.objects.all().filter(test=context['object'])
        print(context)
        return context


class TestDel(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            test = Test.objects.get(pk=kwargs['pk'])
            test.delete()
        return redirect('settings_tests')


class QuestionAdd(CreateView):
    model = Question
    form_class = QuestionAddForm
    template_name = 'control/settings/edit/question_edit.html'

    def get(self, request, *args, **kwargs):
        self.parent = kwargs['pk']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.forms import inlineformset_factory
        context['answers'] = inlineformset_factory(Question, Answer, fields=['text', 'correct'], extra=4)
        context['parent'] = self.parent
        print(context)
        return context

    def post(self, request, *args, **kwargs):
        print(request.POST)
        return super().post(request, *args, **kwargs)
    def form_valid(self, form):

        test = form.save(commit=False)
        test
        test.save()

        return redirect('test_edit', pk=test.id)


class QuestionEdit(UpdateView):
    model = Test
    template_name = 'control/settings/edit/test_edit.html'
    form_class = TestAddForm
    def get_success_url(self):
        return reverse('settings_tests', args=None)


class QuestionDel(View):
    def post(self, request, *args, **kwargs):
        print(kwargs)
        if request.user.is_staff:
            question = Question.objects.get(pk=kwargs['pkq'])
            question.delete()
        return redirect('test_edit', pk=kwargs['pk'])


class GroupTestAdmin(TemplateView):
    template_name = 'control/settings/group_test.html'

    def get(self, request, *args, **kwargs):
        print()
        self.group_pk = request.POST['group_pk']
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_test'] = GroupTest.objects.all().filter(group=self.group_pk)
        return context



class GroupTestAdd(View):

    def get(self, request, *args, **kwargs):
        form = LessonAddForm(request.POST)
        return render(request, 'control/settings/edit/group_test_edit.html', {'form': form,})

    def post(self, request, *args, **kwargs):
        form = LessonAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Занятие создано.")
            return redirect('settings_lessons')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/lesson_edit.html', {'form': form,})


class GroupTestEdit(UpdateView):
    model = Lesson
    template_name = 'control/settings/edit/lesson_edit.html'
    form_class = LessonAddForm

    def get_success_url(self):
        return reverse('settings_lessons', args=None)


class GroupTestDel(View):

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            group = Lesson.objects.get(pk=kwargs['pk'])
            group.delete()
        return redirect('settings_lessons')




class TestView(DetailView):
    model = Test
    template_name = 'control/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(answers__correct=True, test=kwargs['object']).distinct()
        return context

    def get(self, request, *args, **kwargs):
        test_id = kwargs['pk']
        test = Test.objects.all().filter(id=test_id).first()

        if request.user.is_authenticated:
            pass
            '''
            if models.Result.objects.filter(user=request.user, test=test_id).first() is None:
                result = models.Result(user=request.user, test=test)
                result.save()
            else:
                messages.error(request, 'Вы уже прошли задание - %s' % test.name)
                return redirect(reverse('testing:test_list', kwargs=kwargs))
            '''
        else:
            if test.logged is True:
                messages.error(request, 'Вы не можете решать тестовые задания без авторизации')
                return redirect(reverse('testing:test_list', kwargs=kwargs))
        request.session['start_test_time'] = str(datetime.now())
        request.session['test'] = str(test.id)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, **kwargs):
        if request.POST:
            data = dict(request.POST)
            questions = Question.objects.all().filter(test_id=kwargs['pk'])
            dictionary = {}
            for question in questions:
                dictionary[str(question.id)] = []
                answers = Answer.objects.all().filter(question_id=question.id)
                for answer in answers:
                    if answer.correct:
                        dictionary[str(question.id)].append(str(answer.id))
                if len(dictionary[str(question.id)]) < 1:
                    del dictionary[str(question.id)]
            over = len(dictionary)
            test = Test.objects.all().filter(id=kwargs['pk']).first()
            max_points = 0
            points = 0
            full_correct = 0
            non_full_correct = 0
            for key in dictionary.keys():
                current_question = Question.objects.filter(id=key).first()
                max_points += current_question.score
                maxtrue = len(dictionary[key])
                try:
                    if maxtrue > 1:
                        count = 0
                        for element in dictionary[key]:
                            if element in data[key]:
                                count += 1
                        if maxtrue == count:
                            points += current_question.score
                            full_correct += 1
                        elif count > 0:
                            non_full_correct += 1
                            points += test.points
                    elif dictionary[key] == data[key]:
                        points += current_question.score
                        full_correct += 1
                except KeyError:
                    continue
            if request.user.is_authenticated:
                if test.logged:

                    msg = 'Тест завершен.'
                    return HttpResponse(msg, content_type='text/plain')
            msg = 'Тест завершен.\nНабрано баллов %d из %d\nПолных ответов: %d\nНеполных ответов: %d' % \
                  (points, max_points, full_correct, non_full_correct)
            return HttpResponse(msg, content_type='text/plain')


class SyncTime(View):
    def post(self, request, **kwargs):
        if request.POST:
            data_response = {'min': '0', 'sec': '0'}
            start_test_time = request.session.get('start_test_time')
            if start_test_time is None:
                return HttpResponse(JsonResponse(data_response), content_type="application/json")
            then = datetime.datetime.strptime(start_test_time, '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.datetime.now()
            delta_now = now - then
            test_id = request.session.get('test')
            if test_id is None:
                return HttpResponse(JsonResponse(data_response), content_type="application/json")
            test = Test.objects.filter(id=test_id).first()
            if test is None:
                return HttpResponse(JsonResponse(data_response), content_type="application/json")
            over_time = datetime.timedelta(minutes=test.time)
            delta = over_time - delta_now
            total_seconds = delta.total_seconds()
            data_response = {'min': total_seconds // 60, 'sec': int(total_seconds % 60)}
            return HttpResponse(JsonResponse(data_response), content_type="application/json")