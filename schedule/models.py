from datetime import datetime, timedelta

from django.db import models, connection
from django.urls import reverse
from django.utils import timezone

from schedule.utils.utils import format_time


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
        ('Enabled', 'Действует'),
        ('Deleted', 'Удалена'),
    )

    EDUCATION_TYPE_CHOICES = (
        ('Бакалавриат', 'Бакалавриат'),
        ('Специалитет', 'Специалитет'),
        ('Магистратура', 'Магистратура'),
        ('Аспирантура', 'Аспирантура')
    )

    COURSE_CHOICES = (
        (1, 'Первый'),
        (2, 'Второй'),
        (3, 'Третий'),
        (4, 'Четвертый'),
        (5, 'Пятый'),
        (6, 'Шестой')
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Enabled', verbose_name="Статус")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, verbose_name="Факультет", null=True)
    course = models.IntegerField(choices=COURSE_CHOICES, default=1, verbose_name="Курс")
    education_type = models.CharField(choices=EDUCATION_TYPE_CHOICES, default="Бакалавриат", verbose_name="Вариант обучения")
    year_begin = models.IntegerField(default=2023, verbose_name="Год начала обучения")
    year_end = models.IntegerField(default=2027, verbose_name="Год конца обучения")

    def __str__(self):
        return self.name

    def get_schedule(self):
        return Lesson.objects.filter(groups=self)

    def get_icon(self):
        return self.faculty.image

    class Meta:
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"

    def get_absolute_url(self):
        return reverse("group", kwargs={"group_id": self.id})

    def delete(self):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE schedule_group SET status = 'Deleted' WHERE id = %s", [self.pk])


class Teacher(models.Model):
    first_name = models.CharField(verbose_name="Имя")
    middle_name = models.CharField(verbose_name="Фамилия")
    last_name = models.CharField(verbose_name="Отчество")

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.middle_name + ' ' + self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


class Lesson(models.Model):
    STATUS_CHOICES = (
        ('Injected', 'Введён'),
        ('At work', 'В работе'),
        ('Сompleted', 'Завершён'),
        ('Cancelled', 'Отменён'),
        ('Deleted', 'Удалён'),
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
        (6, 'Суббота'),
        (7, 'Воскресенье')
    )

    discipline = models.CharField(verbose_name="Дисциплина", default="")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Преподаватель", null=True)
    groups = models.ManyToManyField(Group, verbose_name="Группа", null=False)
    time = models.TimeField(default=datetime.now(tz=timezone.utc), verbose_name="Время")
    day_of_week = models.IntegerField(default=datetime.isoweekday(datetime.now()), choices=DAY_OF_WEEK_CHOICES, verbose_name="День недели")
    term = models.IntegerField(default=1, choices=TERMS_CHOICES, verbose_name="Семестр")

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Введён', verbose_name="Статус")
    date_created = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата создания")
    date_of_formation = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата формирования")
    date_complete = models.DateTimeField(default=datetime.now(tz=timezone.utc), verbose_name="Дата завершения")

    def __str__(self):
        return "Занятие №" + str(self.pk)

    def get_start_time(self):
        return format_time(self.time)

    def get_end_time(self):
        end_time = (datetime.combine(datetime(1, 1, 1), self.time) + timedelta(hours=1.5)).time()
        return format_time(end_time)

    def get_day_of_week(self):
        days = {1: u"Понедельник", 2: u"Вторник", 3: u"Среда", 4: u"Четверг", 5: u"Пятница", 6: u"Суббота", 7: u"Воскресенье"}
        return days[self.day_of_week]

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"

