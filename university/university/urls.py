from django.contrib import admin
from django.urls import path, include

from schedule.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('schedule.urls')),
]