from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import formset_factory
from pytils.translit import slugify
from tinymce.widgets import TinyMCE
from control.models import Course, Profile, Group, Discipline, Lesson, Test, Question, Answer, Direction, FileTask, \
    ResultFile


class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Логин')
    first_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Фамилия')
    email = forms.EmailField(max_length=100, required=True, help_text='Введите ваш email адрес')
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()
    is_staff = forms.BooleanField(required=False, label='Работник')
    is_superuser = forms.BooleanField(required=False, label='Администратор')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'is_staff',
            'is_superuser',
            ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            if User.objects.all().count() == 0:
                user.is_staff = True
                user.is_superuser = True
            user.save()
        return user


class EditUser(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
        ]


class ProfileForm(forms.ModelForm):
    patronymic = forms.CharField(max_length=30, required=False, label='Отчество')
    birth_date = forms.DateTimeField(required=False, label='День рождения')
    about = forms.CharField(widget=TinyMCE(), required=False, label='О себе')

    class Meta:
        model = Profile
        fields = ['patronymic', 'about', 'birth_date', ]


class DirectionAddForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = '__all__'


class CourseForm(forms.ModelForm):
    name = forms.CharField(max_length=50, required=True,
                           label='Наименование курса')
    image = forms.ImageField(required=False, help_text='Превью курса',
                             label='Изображение', widget=forms.FileInput)
    description = forms.CharField(widget=TinyMCE())
    slug = forms.CharField(empty_value="course")

    def save(self, commit=True):
        course = super().save(commit=False)
        course.slug = slugify(course.name)
        if commit:
            course.save()
        return course

    class Meta:
        model = Course
        fields = [
            'name',
            'image',
            'description',
            'owner',
            'slug',
            'direction',
            ]


class DateInput(forms.DateInput):
    input_type = 'date'


class GroupAddForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'study_start': DateInput(format=('%Y-%m-%d')),
            'study_end': DateInput(format=('%Y-%m-%d')),
        }


class DisciplineAddForm(forms.ModelForm):
    name = forms.CharField(max_length=50, required=True,
                           label='Наименование Дисциплины')

    class Meta:
        model = Discipline
        fields = [
            'name',
            'teacher',
            'course'
            ]


class LessonAddForm(forms.ModelForm):

    class Meta:
        model = Lesson
        fields = '__all__'


class AnswerAddForm(forms.ModelForm):
    id = forms.IntegerField(required=False)
    text = forms.CharField(required=False)

    class Meta:
        model = Answer
        fields = [
            'text',
            'correct',
        ]


AnswerFormSet = formset_factory(AnswerAddForm, extra=4, can_delete=True)


class QuestionAddForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(), required=True, label='Вопрос')

    class Meta:
        model = Question
        fields = '__all__'


class TestAddForm(forms.ModelForm):

    class Meta:
        model = Test
        fields = '__all__'


class FileTaskAddForm(forms.ModelForm):

    class Meta:
        model = FileTask
        fields = '__all__'


class ResultFileAddForm(forms.ModelForm):
    accepted = forms.BooleanField(required=False)
    user = forms.IntegerField(required=False)
    filetask = forms.IntegerField(required=False)

    class Meta:
        model = ResultFile
        fields = '__all__'
