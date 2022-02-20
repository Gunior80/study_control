from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.timezone import make_aware
from django.views import View
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView

from control.forms import RegistrationForm, CourseForm, EditUser, ProfileForm, GroupAddForm, DisciplineAddForm, \
    LessonAddForm, TestAddForm, QuestionAddForm, DirectionAddForm, AnswerFormSet, FileTaskAddForm, ResultFileAddForm
from control.models import *


class Index(TemplateView):
    template_name = 'control/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_courses'] = Course.objects.all()
        a_groups = Group.objects.filter(study_start__gt=timezone.now()).values('course').distinct()
        context['avaible_courses'] = context['all_courses'].filter(id__in=a_groups)
        if self.request.user.is_authenticated:
            my_groups = Group.objects.filter(study_end__gt=timezone.now()).values('course').distinct().filter(
                students=self.request.user.id)
            context['my_courses'] = context['all_courses'].filter(id__in=my_groups)
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
        reg_form = RegistrationForm(request.GET or None)
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
                messages.info(request, f"{user.first_name}, здравствуйте!")
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
        reg_form = RegistrationForm(request.POST or None)
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
                      'profile_form': profile_form})

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
        form = DirectionAddForm(request.GET or None)
        return render(request, 'control/settings/edit/direction_edit.html', {'form': form, })

    def post(self, request, *args, **kwargs):
        form = DirectionAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.error(request, "Направление создано.")
            return redirect('settings_directions')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/direction_edit.html', {'form': form, })


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
        context['groups'] = context['course'].group.all().filter(study_start__gt=timezone.now())
        if self.request.user.is_authenticated:
            context['is_student'] = self.request.user.profile.is_study(self.object)
            context['is_request'] = self.request.user.profile.is_request(self.object)
        return context


class CourseAdd(View):

    def get(self, request, *args, **kwargs):
        form = CourseForm(request.GET or None)
        return render(request, 'control/settings/edit/course_edit.html', {'form': form, })

    def post(self, request, *args, **kwargs):
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Курс создан.")
            return redirect('settings_courses')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/course_edit.html', {'form': form, })


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
        if self.request.user.is_superuser:
            context['groups'] = Group.objects.all()
        else:
            context['groups'] = Group.objects.all().filter(Q(course__discipline__teacher=self.request.user) |
                                                           Q(course__owner=self.request.user))
        return context


class GroupAdd(View):

    def get(self, request, *args, **kwargs):
        form = GroupAddForm(request.GET or None)
        if not self.request.user.is_superuser:
            form.fields['course'].queryset = Course.objects.all().filter(owner=request.user)
        return render(request, 'control/settings/edit/group_edit.html', {'form': form, })

    def post(self, request, *args, **kwargs):
        form = GroupAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Группа создана.")
            return redirect('settings_groups')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/group_edit.html', {'form': form, })


class GroupEdit(UpdateView):
    model = Group
    template_name = 'control/settings/edit/group_edit.html'
    form_class = GroupAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            context['form'].fields['course'].queryset = Course.objects.all().filter(owner=self.request.user)
        return context

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
        if self.request.user.is_superuser:
            context['disciplines'] = Discipline.objects.all()
        else:
            owner = Discipline.objects.all().filter(course__owner=self.request.user).count() > 0
            context['disciplines'] = Discipline.objects.all().filter(Q(teacher=self.request.user) |
                                                                     Q(course__owner=self.request.user))
            context['owner'] = owner
        return context


class DisciplineAdd(View):

    def get(self, request, *args, **kwargs):
        form = DisciplineAddForm(request.GET or None)
        if not request.user.is_superuser:
            form.fields['course'].queryset = Course.objects.filter(owner=request.user)
        return render(request, 'control/settings/edit/discipline_edit.html', {'form': form, })

    def post(self, request, *args, **kwargs):
        form = DisciplineAddForm(request.POST)
        if form.is_valid():
            f = form.save()
            messages.error(request, "Дисциплина создана.")
            return redirect('settings_disciplines')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/discipline_edit.html', {'form': form, })


class DisciplineEdit(UpdateView):
    model = Discipline
    template_name = 'control/settings/edit/discipline_edit.html'
    form_class = DisciplineAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            context['form'].fields['course'].queryset = Course.objects.filter(owner=self.request.user)
        return context

    def get_success_url(self):
        return reverse('settings_disciplines', args=None)


class LessonDetail(DetailView):
    template_name = 'control/lesson.html'
    model = Lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.request.user.profile.is_study(self.object.discipline.course)
        context['testplans'] = self.object.get_plan(group).testplan.all().filter(start__isnull=False,
                                                                                end__isnull=False,
                                                                                test__in=self.object.test.all())
        context['fileplans'] = self.object.get_plan(group).fileplan.all().filter(start__isnull=False,
                                                                                end__isnull=False,
                                                                                file__in=self.object.filetask.all())

        return context


class LessonAdmin(TemplateView):
    template_name = 'control/settings/lessons.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['lessons'] = Lesson.objects.all()
        else:
            context['lessons'] = Lesson.objects.all().filter(Q(discipline__teacher=self.request.user) |
                                                             Q(discipline__course__owner=self.request.user))

        return context


class LessonAdd(View):

    def get(self, request, *args, **kwargs):
        form = LessonAddForm(request.GET or None)
        if not request.user.is_superuser:
            form.fields['discipline'].queryset = Discipline.objects.filter(Q(teacher=request.user) |
                                                                           Q(course__owner=request.user))
        return render(request, 'control/settings/edit/lesson_edit.html', {'form': form, })

    def post(self, request, *args, **kwargs):
        form = LessonAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.error(request, "Занятие создано.")
            return redirect('settings_lessons')
        else:
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/settings/edit/lesson_edit.html', {'form': form, })


class LessonEdit(UpdateView):
    model = Lesson
    template_name = 'control/settings/edit/lesson_edit.html'
    form_class = LessonAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            context['form'].fields['discipline'].queryset = Discipline.objects.filter(teacher=self.request.user)
        return context

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
        if self.request.user.is_superuser:
            context['tests'] = Test.objects.all()
        else:
            context['tests'] = Test.objects.all().filter(Q(lesson__discipline__teacher=self.request.user) |
                                                         Q(lesson__discipline__course__owner=self.request.user))
        return context


class TestAdd(CreateView):
    model = Test
    form_class = TestAddForm
    template_name = 'control/settings/edit/test_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            context['form'].fields['lesson'].queryset = \
                Lesson.objects.filter(Q(discipline__teacher=self.request.user) |
                                      Q(discipline__course__owner=self.request.user))
        return context

    def form_valid(self, form):
        test = form.save(commit=False)
        test.save()
        return redirect('test_edit', pk=test.id)


class TestEdit(UpdateView):
    model = Test
    template_name = 'control/settings/edit/test_edit.html'
    form_class = TestAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = Question.objects.all().filter(test=context['object'])
        if not self.request.user.is_superuser:
            context['form'].fields['lesson'].queryset = \
                Lesson.objects.filter(Q(discipline__teacher=self.request.user) |
                                      Q(discipline__course__owner=self.request.user))
        return context

    def get_success_url(self):
        return reverse('settings_tests', args=None)


class TestDel(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            test = Test.objects.get(pk=kwargs['pk'])
            test.delete()
        return redirect('settings_tests')


class QuestionAdd(View):
    template_name = 'control/settings/edit/question_edit.html'

    def get(self, request, *args, **kwargs):
        parent = kwargs['pk']
        question = QuestionAddForm(data=request.GET or None, initial={'test': parent})
        formset = AnswerFormSet()
        return render(request, self.template_name, {'form': question, "answers": formset, "parent": parent})

    def post(self, request, *args, **kwargs):
        question = QuestionAddForm(request.POST)
        formset = AnswerFormSet(request.POST)
        if question.is_valid() and formset.is_valid():
            question = question.save()
            for form in formset:
                if not form.cleaned_data:
                    continue
                answer = form.save(commit=False)
                if form.cleaned_data.get('DELETE') or form.cleaned_data.get('text') == "":
                    continue
                else:
                    answer.question = question
                    answer.save()
            return redirect("test_edit", pk=self.request.POST.get('next'))

        messages.error(request, "Проверьте поля формы.")
        return render(request, self.template_name, {'form': question, 'answers': formset,
                                                    "parent": self.request.POST.get('next')})


class QuestionEdit(UpdateView):
    model = Question
    template_name = 'control/settings/edit/question_edit.html'
    form_class = QuestionAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = AnswerFormSet(initial=self.object.answer.all().values())
        context['parent'] = self.object.test.pk
        return context

    def post(self, request, *args, **kwargs):
        question = Question.objects.get(pk=self.kwargs['pk'])
        question_form = QuestionAddForm(request.POST)
        formset = AnswerFormSet(request.POST)

        if question_form.is_valid() and formset.is_valid():
            question.text = question_form.cleaned_data.get('text')
            question.save()
            for form in formset:
                if not form.cleaned_data:
                    continue
                print(form.cleaned_data)
                answer = form.save(commit=False)
                if form.cleaned_data.get('id'):
                    obj = Answer.objects.get(id=form.cleaned_data.get('id'))
                    if form.cleaned_data.get('DELETE') or form.cleaned_data.get('text') == "":
                        obj.delete()
                    else:
                        obj.text = answer.text
                        obj.correct = answer.correct
                        obj.save()
                else:
                    if form.cleaned_data.get('DELETE') or form.cleaned_data.get('text') == "":
                        continue
                    else:
                        answer.question = question
                        answer.save()
            return redirect("test_edit", pk=self.request.POST.get('next'))

        messages.error(request, "Проверьте поля формы.")
        return render(request, self.template_name,
                      {'form': question_form, 'answers': formset, "parent": self.request.POST.get('next')})


class QuestionDel(View):

    def get(self, request, *args, **kwargs):
        question = Question.objects.get(pk=kwargs['pk'])
        test = question.test.pk
        if request.user.is_staff:
            question.delete()
        return redirect('test_edit', pk=test)


class TestView(DetailView):
    model = Test
    template_name = 'control/test.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['questions'] = Question.objects.filter(answer__correct=True, test=kwargs['object']).distinct()
        return context

    def get(self, request, *args, **kwargs):
        test_id = kwargs['pk']
        test = Test.objects.all().filter(id=test_id).first()
        user_try = request.user.resulttest.all().count() + 1

        if test.is_passed(request.user):
            messages.error(request, 'Вы уже успешно выполнили это задание - %s' % test.name)
            return redirect(test.lesson.get_absolute_url())

        if test.tryes >= user_try:
            result = ResultTest(user=request.user, test=test, start_time=timezone.now(),
                                end_time=timezone.now())
            result.save()
        else:
            messages.error(request, 'Вы израсходовали все попытки - %s' % test.name)
            return redirect(test.lesson.get_absolute_url())

        request.session['try'] = user_try
        request.session['start_test_time'] = str(datetime.datetime.now())
        request.session['test'] = str(test.id)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, **kwargs):
        if request.POST:
            data = dict(request.POST)
            test = Test.objects.all().filter(id=kwargs['pk']).first()
            result = ResultTest.objects.filter(user=request.user, test=test).order_by('-start_time').first()
            result.end_time = timezone.now()

            questions = Question.objects.all().filter(test_id=kwargs['pk'])
            dictionary = {}
            resultadic = {}
            for question in questions:
                q = ResultQuestion(test=result, text=question.text)
                q.save()
                answers = Answer.objects.all().filter(question_id=question.id)
                for answer in answers:
                    a = ResultAnswer(question=q, text=answer.text, correct=answer.correct)
                    a.save()
                    resultadic[str(answer.id)] = str(a.id)

            del data['question_id']
            del data['csrfmiddlewaretoken']

            if len(data):
                for key in data.keys():
                    print(key)
                    for id_ans in data[key]:
                        ra = ResultAnswer.objects.get(pk=int(resultadic[str(id_ans)]))
                        ra.given = True
                        ra.save()
            result.save()
            if test.pass_percent > result.get_percent():
                msg = 'Тест не пройден.'
            else:
                msg = 'Тест пройден.'
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
            over_time = timedelta(minutes=test.time)
            delta = over_time - delta_now
            total_seconds = delta.total_seconds()
            data_response = {'min': total_seconds // 60, 'sec': int(total_seconds % 60)}
            return HttpResponse(JsonResponse(data_response), content_type="application/json")


class TestResultsView(DetailView):
    model = Test
    template_name = 'control/settings/test_results.html'

    def get_context_data(self, **kwargs):
        context = super(TestResultsView, self).get_context_data(**kwargs)
        context['resulttests'] = ResultTest.objects.all().filter(test=kwargs['object'])
        return context

    def post(self, request, **kwargs):
        if request.POST:
            if request.user.is_staff:
                result = ResultTest.objects.get(pk=request.POST['result'])
                result.delete()
        return redirect('test_results', pk=kwargs['pk'])


class TestDetailView(DetailView):
    model = ResultTest
    template_name = 'control/settings/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = Test.objects.all()
        if self.request.user.is_superuser:
            context['tests'] = Test.objects.all()
        else:
            context['tests'] = Test.objects.all().filter(Q(lesson__discipline__teacher=self.request.user) |
                                                         Q(lesson__discipline__course__owner=self.request.user))
        return context


class FileAdmin(TemplateView):
    template_name = 'control/settings/files.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = FileTask.objects.all()
        if self.request.user.is_superuser:
            context['files'] = FileTask.objects.all()
        else:
            context['files'] = FileTask.objects.all().filter(Q(lesson__discipline__teacher=self.request.user) |
                                                             Q(lesson__discipline__course__owner=self.request.user))
        return context


class FileAdd(CreateView):
    model = FileTask
    form_class = FileTaskAddForm
    template_name = 'control/settings/edit/file_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_superuser:
            context['form'].fields['lesson'].queryset = \
                Lesson.objects.filter(Q(discipline__teacher=self.request.user) |
                                      Q(discipline__course__owner=self.request.user))
        return context

    def form_valid(self, form):
        file = form.save(commit=False)
        file.save()
        return redirect('settings_files')


class FileEdit(UpdateView):
    model = FileTask
    template_name = 'control/settings/edit/file_edit.html'
    form_class = FileTaskAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('settings_files', args=None)


class FileDel(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            test = FileTask.objects.get(pk=kwargs['pk'])
            test.delete()
        return redirect('settings_files')


class FileResultsView(DetailView):
    model = FileTask
    template_name = 'control/settings/file_results.html'

    def get_context_data(self, **kwargs):
        context = super(FileResultsView, self).get_context_data(**kwargs)

        context['resultfiles'] = ResultFile.objects.all().filter(filetask=kwargs['object'])
        return context

    def post(self, request, **kwargs):
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken')
        data.pop('table_length')
        print(data)
        for key, value in data.items():
            result = ResultFile.objects.get(pk=key)
            result.accepted = int(value)
            result.save()
        return redirect('settings_files')


class FileDetailView(UpdateView):
    model = ResultFile
    template_name = 'control/settings/file_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tests'] = FileTask.objects.all()
        if self.request.user.is_superuser:
            context['files'] = FileTask.objects.all()
        else:
            context['files'] = FileTask.objects.all().filter(Q(lesson__discipline__teacher=self.request.user) |
                                                             Q(lesson__discipline__course__owner=self.request.user))
        return context


class FileView(View):

    def get(self, request, *args, **kwargs):
        object = FileTask.objects.get(pk=self.kwargs['pk'])
        result = ResultFile.objects.filter(filetask=object, user=request.user).first()
        if result:
            form = ResultFileAddForm(instance=result)
        else:
            form = ResultFileAddForm(request.GET or None)
        return render(request, 'control/file.html', {'form': form, 'filetask':object})

    def post(self, request, *args, **kwargs):
        object = FileTask.objects.get(pk=self.kwargs['pk'])
        form = ResultFileAddForm(request.POST, request.FILES)
        form.fields['filetask'].initial = object.id
        form.fields['user'].initial = request.user.id
        result = ResultFile.objects.filter(filetask=object, user=request.user).first()
        if form.is_valid():
            if result:
                obj = form.save(commit=False)
                result.file = obj.file
            else:
                result = form.save(commit=False)
                result.filetask = object
                result.user = request.user
            result.accepted = None
            result.save()
            messages.error(request, "Ответ сохранен")
            return redirect('lesson', slug=object.lesson.discipline.course.slug, pk=object.lesson.id )
        else:
            print(form.errors)
            messages.error(request, "Проверьте поля формы.")
        return render(request, 'control/file.html', {'form': form, })


class GroupSPlan(DetailView):
    model = Group
    template_name = 'control/settings/group_plan.html'

    def get_context_data(self, **kwargs):
        context = super(GroupSPlan, self).get_context_data(**kwargs)
        return context

    def post(self, request, **kwargs):
        data = dict(request.POST)
        del data['table_length']
        del data['csrfmiddlewaretoken']
        group = Group.objects.get(pk=kwargs['pk'])
        for key, dt in data.items():
            if key.isalnum():
                curr_datetime = self.get_date(dt[0])
                lesson = Lesson.objects.get(pk=key)
                lesson_plan, created = LessonPlan.objects.get_or_create(group=group, lesson=lesson)
                lesson_plan.start = curr_datetime
                lesson_plan.save()
            else:
                curr_datetime = self.get_date(dt[0])
                info_datetime = key.split("_")
                if info_datetime[0] == 'test':
                    task = Test.objects.get(pk=info_datetime[2])
                    task_plan, created = TestPlan.objects.get_or_create(test=task, lessonplan=task.lesson.get_plan(group))
                elif info_datetime[0] == 'file':
                    task = FileTask.objects.get(pk=info_datetime[2])
                    task_plan, created = FilePlan.objects.get_or_create(file=task, lessonplan=task.lesson.get_plan(group))

                if info_datetime[1] == "start":
                    task_plan.start = curr_datetime
                elif info_datetime[1] == "end":
                    task_plan.end = curr_datetime
                task_plan.check_datetimes()
                task_plan.save()

        return redirect('group_plan', pk=kwargs['pk'])

    def get_date(self, string):
        try:
            return make_aware(datetime.datetime.strptime(string, '%Y-%m-%d %H:%M'))
        except ValueError:
            return None

class GroupStatistics(DetailView):
    model = Group
    template_name = 'control/settings/group_statistics.html'

    def get_context_data(self, **kwargs):
        context = super(GroupStatistics, self).get_context_data(**kwargs)

        return context

