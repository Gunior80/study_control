from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from pytils.translit import slugify
from tinymce.widgets import TinyMCE
from control.models import Course, Profile, Group


class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Логин')
    first_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Фамилия')
    email = forms.EmailField(max_length=100, help_text='Введите ваш email адрес')
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
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
        ]


class ProfileForm(forms.ModelForm):
    patronymic = forms.CharField(max_length=30, required=False,
                                 help_text='Обязательно для заполнения', label='Отчество')
    birth_date = forms.DateTimeField(required=False, label='День рождения')
    about = forms.CharField(widget=TinyMCE(), required=False, label='О себе')

    class Meta:
        model = Profile
        fields = ['patronymic', 'about', 'birth_date']


class CourseForm(forms.ModelForm):
    name = forms.CharField(max_length=50, required=True,
                           label='Наименование курса')
    image = forms.ImageField(required=False, help_text='Превью курса',
                             label='Изображение', widget=forms.FileInput)
    description = forms.CharField(widget=TinyMCE())
    disciplines = forms.BooleanField(label='Дисциплины курса')
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
            'disciplines',
            'slug'
            ]


class DateInput(forms.DateInput):
    input_type = 'date'


class GroupAddForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'study_start': DateInput(),
            'study_end': DateInput(),
        }
