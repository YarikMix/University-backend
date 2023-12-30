import ast
from operator import itemgetter

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializer import *


@api_view(["GET"])
def get_groups(request):
    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_group_lessons(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует!")

    group = Group.objects.get(pk=group_id)
    lessons = group.lesson_set

    serializer = LessonSerializer(lessons, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def search_groups(request):

    course_id, education_type_id, query, faculties = itemgetter("course", "education_type", "query", "faculties")(request.GET.dict())

    groups = Group.objects.filter(name__icontains=query).filter(status=1)

    if int(course_id) > 0:
        groups = groups.filter(course=course_id)

    if int(education_type_id) > 0:
        groups = groups.filter(education_type=education_type_id)

    if -1 not in ast.literal_eval(faculties):
        groups = groups.filter(faculty__in=ast.literal_eval(faculties))

    serializer = GroupSerializer(groups, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_group_by_id(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует!")

    group = Group.objects.get(pk=group_id)
    serializer = GroupSerializer(group, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_group(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует!")

    group = Group.objects.get(pk=group_id)
    serializer = GroupSerializer(group, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_group(request):
    Group.objects.create()

    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_group(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует!")

    group = Group.objects.get(pk=group_id)
    group.status = 2
    group.save()

    groups = Group.objects.filter(status=1)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def add_group_to_lesson(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует!")

    group = Group.objects.get(pk=group_id)

    lesson = Lesson.objects.filter(status=1).last()

    if lesson is None:
        lesson = Lesson.objects.create()

    lesson.groups.add(group)
    lesson.save()

    serializer = GroupSerializer(lesson.groups, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_lessons(request):
    lessons = Lesson.objects.all()
    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_lesson_by_id(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует!")

    lesson = Lesson.objects.get(pk=lesson_id)
    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
def update_lesson(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует!")

    lesson = Lesson.objects.get(pk=lesson_id)
    serializer = LessonSerializer(lesson, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    lesson.status = 1
    lesson.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_lesson_user(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует!")

    request_status = request.data["status"]

    if request_status not in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson = Lesson.objects.get(pk=lesson_id)
    lesson_status = lesson.status

    if lesson_status == 5:
        return Response("Статус изменить нельзя")

    lesson.status = request_status
    lesson.save()

    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
def update_lesson_admin(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует!")

    request_status = request.data["status"]

    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson = Lesson.objects.get(pk=lesson_id)

    lesson_status = lesson.status

    if lesson_status in [3, 4, 5]:
        return Response("Статус изменить нельзя")

    lesson.status = request_status
    lesson.save()

    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_lesson(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует!")

    lesson = Lesson.objects.get(pk=lesson_id)
    lesson.status = 5
    lesson.save()

    lessons = Lesson.objects.all()
    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_group_from_lesson(request, lesson_id, group_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(f"Занятия с таким id не существует")

    if not Group.objects.filter(pk=group_id).exists():
        return Response(f"Группы с таким id не существует")

    lesson = Lesson.objects.get(pk=lesson_id)
    lesson.groups.remove(Group.objects.get(pk=group_id))
    lesson.save()

    serializer = GroupSerializer(lesson.groups, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_facults(request):
    facults = Faculty.objects.all()
    serializer = FacultySerializer(facults, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_faculty_by_id(request, faculty_id):
    if not Faculty.objects.filter(pk=faculty_id).exists():
        return Response(f"Факультета с таким id не существует!")

    faculty = Faculty.objects.get(pk=faculty_id)
    serializer = FacultySerializer(faculty, many=False)

    return Response(serializer.data)


@api_view(["GET"])
def get_faculty_icon(request, faculty_id):
    if not Faculty.objects.filter(pk=faculty_id).exists():
        return Response(f"Факультета с таким id не существует!")

    faculty = Faculty.objects.get(pk=faculty_id)

    return HttpResponse(faculty.image, content_type="image/png")

