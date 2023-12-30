from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="home"),
    path('group/<int:group_id>', groupSchedule, name="group"),
    path('delete-group/<int:group_id>', groupDelete, name="delete-group")
]