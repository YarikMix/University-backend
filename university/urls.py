from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from schedule.views import index
from university import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("schedule.urls")),
    path("__reload__/", include("django_browser_reload.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
