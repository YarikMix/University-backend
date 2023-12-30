from django.contrib import admin

from schedule.models import *

admin.site.register(Group)
admin.site.register(Lesson)
admin.site.register(Teacher)
admin.site.register(Faculty)