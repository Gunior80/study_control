from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import Form, ModelForm
from django.utils.safestring import mark_safe
from pytils.translit import slugify

from control.models import Course, Profile


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['patronymic', 'about', 'birth_date']


class CourseForm(ModelForm):
    name = forms.CharField(max_length=50, required=True, help_text='Обязательно для заполнения',
                           label='Наименование курса')
    image = forms.ImageField(required=False, help_text='Превью курса',
                             label='Изображение')
    description = forms.TextInput()
    slug = forms.CharField(empty_value="course")

    def save(self, commit=True):
        course = super().save(commit=False)
        course.slug = slugify(course.name)
        #if course.image
        if commit:
            course.save()
        return course

    class Meta:
        model = Course
        fields = [
            'name',
            'image',
            'description',
            'slug'
            ]

