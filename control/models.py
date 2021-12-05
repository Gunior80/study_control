from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from pytils.translit import slugify

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество", )
    birth_date = models.DateField(null=True, blank=True)
    about = models.TextField(blank=True, default='', verbose_name="О себе", )

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
    return '{0}/{1}'.format(instance, filename)


class Course(models.Model):
    name = models.CharField(max_length=256, verbose_name="Наименование курса", )
    image = models.ImageField(verbose_name="Превью курса", upload_to=upload_course)
    description = models.TextField(blank=True, default='', verbose_name="Описание курса", )
    slug = models.SlugField(default='',)
    owner = models.ForeignKey(User, verbose_name="Заведующий курсом", null=True, default=None, related_name='owner', on_delete=models.SET_DEFAULT)

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
        return super(Course, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Course)
def image_delete(sender, instance, **kwargs):
    if instance.image.name:
        instance.image.delete(False)


class Discipline(models.Model):
    name = models.CharField(verbose_name="Наименование дисциплины", max_length=256)
    description = models.TextField(blank=True, default='',
                                   verbose_name="Описание дисциплины", )
    course = models.ForeignKey(Course, verbose_name="Курс", related_name='disciplines', on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, verbose_name="Преподаватель", related_name='teacher', null=True, default=None, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Дисциплина")
        verbose_name_plural = _("Дисциплины")


class Lesson(models.Model):
    name = models.CharField(max_length=256, verbose_name="Наименование занятия",)
    description = models.TextField(blank=True, default='',
                                   verbose_name="Описание занятия", )
    discipline = models.ForeignKey(Discipline, verbose_name="Дисциплина", related_name='lessons',
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Занятие")
        verbose_name_plural = _("Занятия")


class Group(models.Model):
    name = models.CharField(max_length=256, verbose_name="Наименование группы", )
    course = models.ForeignKey(Course, verbose_name="Курс", related_name='course', on_delete=models.CASCADE)
    user = models.ManyToManyField(User, verbose_name="Учащиеся", related_name='user')
    request = models.ManyToManyField(User, verbose_name="Заявки на зачисление", related_name='request')
    study_start = models.DateField(verbose_name="Дата начала обучения")
    study_end = models.DateField(verbose_name="Дата конца обучения")

    class Meta:
        verbose_name = _("Группа")
        verbose_name_plural = _("Группы")


