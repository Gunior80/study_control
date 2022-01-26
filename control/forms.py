from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import inlineformset_factory, BaseInlineFormSet
from pytils.translit import slugify
from tinymce.widgets import TinyMCE
from control.models import Course, Profile, Group, Discipline, Lesson, Test, Question, Answer, Direction, GroupTest


class RegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Логин')
    first_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Имя')
    last_name = forms.CharField(max_length=30, required=True, help_text='Обязательно для заполнения', label='Фамилия')
    email = forms.EmailField(max_length=100, help_text='Введите ваш email адрес')
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
        fields = ['patronymic', 'about', 'birth_date',]


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
    description = forms.CharField(widget=TinyMCE(), required=False)

    class Meta:
        model = Discipline
        fields = [
            'name',
            'description',
            'teacher',
            'course'
            ]


class LessonAddForm(forms.ModelForm):

    class Meta:
        model = Lesson
        fields = '__all__'


class AnswerAddForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionAddForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(), required=True, label='Вопрос')

    class Meta:
        model = Question
        fields = '__all__'



class TestAddForm(forms.ModelForm):

    class Meta:
        model = Test
        fields = '__all__'












CONTENT_TYPE_CHOICES = (
  Q(app_label='control', model='test') |
  Q(app_label='control', model='Имя')
)

class XDSoftDateTimePickerInput(forms.DateTimeInput):
    template_name = 'widgets/xdsoft_datetimepicker.html'


class FieldsetWidget(forms.widgets.Widget):
    # Виджет для вывода формы
    def render(self, name, value, attrs=None):
        return self.attrs['form_html']


class FieldsetField(forms.Field):
    # Поле формы, содержащее другую форму
    def __init__(self, fieldset, *args, **kwargs):
        # Html формы передается параметром этого виджета
        widget = FieldsetWidget(attrs={
            'form_html': '<table>%s</table>' % fieldset.as_table()
        })
        kwargs.update({
            'widget': widget,
            'required': False
        })
        super(FieldsetField, self).__init__(*args, **kwargs)


class GroupTestAddForm(forms.ModelForm):
    start = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%i'],
        widget=XDSoftDateTimePickerInput()
    )
    end = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%i'],
        widget=XDSoftDateTimePickerInput()
    )

    class Meta:
        model = GroupTest
        fields = '__all__'

'''
class GroupTaskAddForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(ContentType.objects.all(), limit_choices_to = CONTENT_TYPE_CHOICES,
                                          label='Тип задания')
    object_id = forms.IntegerField(show_hidden_initial=True)
    start = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%i'],
        widget=XDSoftDateTimePickerInput()
    )
    end = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%i'],
        widget=XDSoftDateTimePickerInput()
    )

    class Meta:
        model = GroupTask
        fields = [
            'content_type', # Таблица
            'group',
            'object_id',    # ID задания (автозаполняется при сохранинии)
            'start',
            'end',
        ]
'''
