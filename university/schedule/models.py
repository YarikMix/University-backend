from datetime import datetime

from django.contrib.auth.models import User, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone

from schedule.utils.utils import format_time

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class Faculty(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    image = models.ImageField(upload_to="facults", verbose_name="Картинка")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"


class Group(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    EDUCATION_TYPE_CHOICES = (
        (1, 'Бакалавриат'),
        (2, 'Специалитет'),
        (3, 'Магистратура'),
        (4, 'Аспирантура')
    )

    COURSE_CHOICES = (
        (1, 'Первый'),
        (2, 'Второй'),
        (3, 'Третий'),
        (4, 'Четвертый'),
        (5, 'Пятый'),
        (6, 'Шестой')
    )

    name = models.CharField(max_length=100, default="Название группы", verbose_name="Название")
    status = models.IntegerField(max_length=100, choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name="Факультет", null=True)
    course = models.IntegerField(default=1, choices=COURSE_CHOICES, verbose_name="Курс")
    education_type = models.IntegerField(default=1, choices=EDUCATION_TYPE_CHOICES, verbose_name="Вариант обучения")
    year_begin = models.IntegerField(default=2023, verbose_name="Год начала обучения")
    year_end = models.IntegerField(default=2027, verbose_name="Год конца обучения")

    def __str__(self):
        return self.name

    def get_schedule(self):
        return Lesson.objects.filter(groups=self)

    def get_absolute_url(self):
        return reverse("group", kwargs={"group_id": self.id})

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"
        ordering = ('id', )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Custom fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=30)
    is_moderator = models.BooleanField(default=False)

    # Necessary fields for django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Lesson(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален'),
    )

    TERMS_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
    )

    DAY_OF_WEEK_CHOICES = (
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота')
    )

    LESSON_TIME_CHOICES = (
        (1, '8:30'),
        (2, '10:15'),
        (3, '12:00'),
        (4, '13:50'),
        (5, '15:40'),
        (6, '17:25'),
        (7, '19:10')
    )

    discipline = models.CharField(default="Дисциплина", verbose_name="Дисциплина")
    audience = models.CharField(default="Аудитория", verbose_name="Аудитория")
    teacher = models.CharField(default="Преподаватель", verbose_name="Преподаватель")
    groups = models.ManyToManyField(Group, verbose_name="Группа", null=False)
    time = models.IntegerField(default=1, choices=LESSON_TIME_CHOICES, verbose_name="Время начала")
    day_of_week = models.IntegerField(default=datetime.isoweekday(datetime.now()), choices=DAY_OF_WEEK_CHOICES, verbose_name="День недели")
    term = models.IntegerField(default=1, choices=TERMS_CHOICES, verbose_name="Семестр")

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата создания")
    date_of_formation = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата формирования")
    date_complete = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата завершения")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь", null=True)

    def __str__(self):
        return "Занятие №" + str(self.pk)

    def get_start_time(self):
        return format_time(self.time)

    def get_day_of_week(self):
        days = {1: u"Понедельник", 2: u"Вторник", 3: u"Среда", 4: u"Четверг", 5: u"Пятница", 6: u"Суббота", 7: u"Воскресенье"}
        return days[self.day_of_week]

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ('id', )
