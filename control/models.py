import datetime

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from pytils.translit import slugify
from tinymce import models as tinymce_models

# Create your models here.
from study_control.settings import MEDIA_URL


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество", )
    birth_date = models.DateField(null=True, blank=True)
    about = tinymce_models.HTMLField(blank=True, default='', verbose_name="О себе", )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def upload_course(instance, filename):
    return 'uploads/{0}/{1}'.format(instance, filename)


class Direction(models.Model):
    name = models.CharField(max_length=256, verbose_name="Направление", )

    class Meta:
        verbose_name = _("Направление обучения")
        verbose_name_plural = _("Направления обучения")

    def __str__(self):
        return self.name


class Course(models.Model):
    direction = models.ForeignKey(Direction, verbose_name="Направление", null=True, default=None,
                              related_name='course', on_delete=models.SET_NULL)

    name = models.CharField(max_length=256, verbose_name="Наименование курса", )
    image = models.ImageField(verbose_name="Превью курса", upload_to=upload_course, blank=True)
    description = tinymce_models.HTMLField(blank=True, default='',
                                           verbose_name="Описание курса", )
    slug = models.SlugField(default='', unique=True)
    owner = models.ForeignKey(User, verbose_name="Заведующий курсом", null=True, default=None,
                              related_name='owner', on_delete=models.SET_NULL,
                              limit_choices_to={'is_staff': True})

    class Meta:
        verbose_name = _("Курс")
        verbose_name_plural = _("Курсы")

    def get_absolute_url(self):
        return reverse('course', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.pk is not None:
            old_self = Course.objects.get(pk=self.pk)
            if old_self.image and self.image != old_self.image:
                old_self.image.delete(False)
        return super().save(*args, **kwargs)

    def is_student(self, user):
        return 1

@receiver(pre_delete, sender=Course)
def image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)


class Discipline(models.Model):
    name = models.CharField(verbose_name="Наименование дисциплины", max_length=256)
    description = tinymce_models.HTMLField(blank=True, default='',
                                           verbose_name="Описание дисциплины", )
    course = models.ForeignKey(Course, verbose_name="Курс", related_name='discipline', on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, verbose_name="Преподаватель", related_name='discipline',
                                null=True, default=None, on_delete=models.SET_DEFAULT,
                                limit_choices_to={'is_staff': True})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Дисциплина")
        verbose_name_plural = _("Дисциплины")


class Lesson(models.Model):
    name = models.CharField(max_length=256, verbose_name="Наименование занятия",)
    description = tinymce_models.HTMLField(blank=True, default='', verbose_name="Описание занятия", )
    discipline = models.ForeignKey(Discipline, verbose_name="Дисциплина", related_name='lesson',
                                   on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('lesson', kwargs={'slug': self.discipline.course.slug, 'pk': self.pk})

    def __str__(self):
        return '{0} - {1}'.format(self.discipline, self.name)

    class Meta:
        verbose_name = _("Занятие")
        verbose_name_plural = _("Занятия")


class Group(models.Model):
    name = models.CharField(max_length=256, verbose_name="Наименование группы", )
    course = models.ForeignKey(Course, verbose_name="Курс", related_name='group', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, verbose_name="Учащиеся", related_name='stud_user', blank=True)
    requests = models.ManyToManyField(User, verbose_name="Заявки на зачисление", related_name='request_user', blank=True)
    max_users = models.PositiveIntegerField(default=30, verbose_name="Максимальное количество учащихся", )
    study_start = models.DateField(verbose_name="Дата начала обучения")
    study_end = models.DateField(verbose_name="Дата конца обучения")

    def get_status(self):
        now = datetime.date.today()
        if self.study_start < now and now < self.study_end:
            return "Ведется обучение"
        elif now < self.study_start:
            return "Ведется набор"
        elif self.study_end < now:
            return "Обучение завершено"

    def add_students(self, querydict):
        for key, value in querydict.items():
            if int(value) == True:
                self.students.add(User.objects.get(pk=int(key)))
            self.requests.remove(User.objects.get(pk=int(key)))

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.course)

    class Meta:
        verbose_name = _("Группа")
        verbose_name_plural = _("Группы")


class Test(models.Model):
    lesson = models.ForeignKey(Lesson, default=1, related_name='task', on_delete=models.CASCADE, verbose_name="Занятие", )
    name = models.CharField(max_length=256, default="1", verbose_name="Наименование задания", )
    tryes = models.PositiveIntegerField(default=3, verbose_name="Количество попыток")
    pass_percent = models.PositiveIntegerField(default=60, validators=[MinValueValidator(10),MaxValueValidator(100)],
                                               verbose_name="Мин. процент")
    time = models.PositiveIntegerField(default="5", verbose_name="Время на тест", )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тест")
        verbose_name_plural = _("Тесты")


class Question(models.Model):
    text = tinymce_models.HTMLField(blank=True, default='', verbose_name="Вопрос", )
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")

    def get_absolute_url(self):
        return reverse('question', kwargs={'pk': self.id})

    def get_answers(self):
        answers = self.answer.all().filter(correct=True)
        if answers.count() == 0:
            return False
        return answers



class Answer(models.Model):
    text = models.CharField(max_length=256, verbose_name="Ответ")
    question = models.ForeignKey(Question, related_name='answer', on_delete=models.CASCADE,
                                 verbose_name="Название вопроса",)
    correct = models.BooleanField(default=False, verbose_name="Верный ответ",)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")




class ResultTest(models.Model):
    test = models.ForeignKey(Test, related_name='resulttest',
                             on_delete=models.CASCADE, verbose_name="Тест", )
    user = models.ForeignKey(User, related_name='resulttest',
                             on_delete=models.CASCADE, verbose_name="Учащийся", )
    time = models.TimeField(verbose_name="Затраченное время", null=True, blank=True, )
    start_time = models.DateTimeField(verbose_name="Время начала контроля", default=datetime.datetime.now())

    def __str__(self):
        return "{0} - {1} {2} {3}".format(self.test.name, self.user.first_name,
                                          self.user.last_name, self.user.profile.patronymic,)

    class Meta:
        verbose_name = _("Результат теста")
        verbose_name_plural = _("Результаты тестов")

    def get_percent(self):
        questions_count = self.resultquestion.all().count()
        points = 0
        for question in self.resultquestion.all():
            flag = True
            for answer in question.resultanswer.all():
                if answer.correct != answer.given:
                    flag = False
                    break
            if flag:
                points+=1
        return round((points / questions_count) * 100, 1)

    def get_user_group(self):
        if self.user.is_staff:
            return "Администратор"
        intercept = self.user.stud_user.all() & self.test.lesson.discipline.course.group.all()
        return intercept.first().name




class ResultQuestion(models.Model):
    text = tinymce_models.HTMLField(blank=True, default='', verbose_name="Вопрос", )
    test = models.ForeignKey(ResultTest, related_name='resultquestion',on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Результат вопроса")
        verbose_name_plural = _("Результаты вопросов")


class ResultAnswer(models.Model):
    text = models.CharField(max_length=256, verbose_name="Ответ")
    question = models.ForeignKey(ResultQuestion, related_name='resultanswer', on_delete=models.CASCADE,
                                 verbose_name="Название вопроса",)
    correct = models.BooleanField(default=False, verbose_name="Верный ответ",)
    given = models.BooleanField(default=False, verbose_name="Дан ответ",)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Результат ответа")
        verbose_name_plural = _("Результат ответов")


class GroupLesson(models.Model):
    lesson = models.ForeignKey(Test, verbose_name="Занятие", related_name='grouplesson', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name="Группа", related_name='grouplesson', on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name="Время начала занятия", default=datetime.datetime.now())


class GroupTest(models.Model):
    test = models.ForeignKey(Test, verbose_name="Тест", related_name='grouptest', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name="Группа", related_name='grouptest', on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name="Время начала контроля", default=datetime.datetime.now())
    end = models.DateTimeField(verbose_name="Время конца контроля")



'''
class GroupTask(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    group = models.ForeignKey(Group, verbose_name="Группа", related_name='group', on_delete=models.CASCADE)
    start = models.DateTimeField(verbose_name="Время начала контроля", default=datetime.datetime.now())
    end = models.DateTimeField(verbose_name="Время конца контроля")
'''