from django.urls import path
from schedule.views import *

urlpatterns = [
    # Набор методов для услуг (Учебных групп)
    path('api/groups/', get_groups),  # GET
    path('api/groups/search/', search_groups),  # GET
    path('api/groups/<int:group_id>/', get_group_by_id),  # GET
    path('api/groups/<int:group_id>/lessons/', get_group_lessons),  # GET
    path('api/groups/<int:group_id>/update/', update_group),  # PUT
    path('api/groups/<int:group_id>/delete/', delete_group),  # DELETE
    path('api/groups/create/', create_group),  # POST
    path('api/groups/<int:group_id>/add_to_lesson/', add_group_to_lesson),  # POST

    # Набор методов для заявок (Занятий)
    path('api/lessons/', get_lessons),  # GET
    path('api/lessons/<int:lesson_id>/', get_lesson_by_id),  # GET
    path('api/lessons/<int:lesson_id>/update/', update_lesson),  # PUT
    path('api/lessons/<int:lesson_id>/update_status_user/', update_lesson_user),  # PUT
    path('api/lessons/<int:lesson_id>/update_status_admin/', update_lesson_admin),  # PUT
    path('api/lessons/<int:lesson_id>/delete/', delete_lesson),  # DELETE (?)
    path('api/lessons/<int:lesson_id>/delete_group/<int:group_id>/', delete_group_from_lesson),  # DELETE

    # Набор методов для факультетов
    path('api/facults/', get_facults),  # GET
    path('api/facults/<int:faculty_id>/', get_faculty_by_id),  # GET
    path('api/facults/<int:faculty_id>/icon', get_faculty_icon),  # GET
]
