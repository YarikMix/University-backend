import ast
import time

from operator import itemgetter
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt import authentication

from .jwt_helper import create_access_token, create_refresh_token, get_jwt_payload, get_access_token, get_refresh_token
from .permissions import *
from .serializer import *


access_token_lifetime = settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()


@api_view(["GET"])
def get_groups(request):
    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_group_lessons(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

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
        return Response(status=status.HTTP_404_NOT_FOUND)

    group = Group.objects.get(pk=group_id)
    serializer = GroupSerializer(group, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsModerator])
def update_group(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    group = Group.objects.get(pk=group_id)
    serializer = GroupSerializer(group, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_group(request):
    Group.objects.create()

    groups = Group.objects.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_group(request, group_id):
    if not Group.objects.filter(pk=group_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    group = Group.objects.get(pk=group_id)
    group.status = 2
    group.save()

    groups = Group.objects.filter(status=1)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_group_to_lesson(request, group_id):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    group = Group.objects.get(pk=group_id)

    lesson = Lesson.objects.filter(status=1).filter(user_id=user_id).last()

    if lesson is None:
        lesson = Lesson.objects.create()

    if lesson.groups.contains(group):
        return Response(status=status.HTTP_409_CONFLICT)

    lesson.groups.add(group)
    lesson.user = CustomUser.objects.get(pk=payload["user_id"])
    lesson.save()

    serializer = GroupSerializer(lesson)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lessons(request):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    lessons = Lesson.objects.filter(user_id=user_id).exclude(status__in=[5])
    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_lesson_by_id(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lesson = Lesson.objects.get(pk=lesson_id)
    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_lesson(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lesson = Lesson.objects.get(pk=lesson_id)
    serializer = LessonSerializer(lesson, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    lesson.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_lesson_user(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson = Lesson.objects.get(pk=lesson_id)
    lesson_status = lesson.status

    if lesson_status == 5:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson.status = request_status
    lesson.save()

    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_lesson_admin(request, lesson_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["status"]   # Статус, на который мы хотим поменять

    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson = Lesson.objects.get(pk=lesson_id)

    lesson_status = lesson.status    # Текущий статус заявки

    if lesson_status in [3, 4, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson.status = request_status
    lesson.save()

    serializer = LessonSerializer(lesson, many=False)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_lesson(request, lesson_id):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lesson = Lesson.objects.get(pk=lesson_id)

    lesson_status = lesson.status

    if lesson_status not in [1]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    lesson.status = 5
    lesson.save()

    lessons = Lesson.objects.filter(user_id=user_id).exclude(status__in=[5])
    serializer = LessonSerializer(lessons, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_group_from_lesson(request, lesson_id, group_id):
    if not Lesson.objects.filter(pk=lesson_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not Group.objects.filter(pk=group_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    lesson = Lesson.objects.get(pk=lesson_id)
    lesson.groups.remove(Group.objects.get(pk=group_id))
    lesson.save()

    serializer = LessonSerializer(lesson)
    return Response(serializer.data)


@api_view(["GET"])
def get_faculties(request):
    facults = Faculty.objects.all()
    serializer = FacultySerializer(facults, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_faculty_by_id(request, faculty_id):
    if not Faculty.objects.filter(pk=faculty_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    faculty = Faculty.objects.get(pk=faculty_id)
    serializer = FacultySerializer(faculty, many=False)

    return Response(serializer.data)


@api_view(["GET"])
def get_faculty_icon(request, faculty_id):
    if not Faculty.objects.filter(pk=faculty_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    faculty = Faculty.objects.get(pk=faculty_id)

    return HttpResponse(faculty.image, content_type="image/png")


@api_view(["PUT"])
def set_faculty_icon(request, faculty_id):
    if not Faculty.objects.filter(pk=faculty_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    faculty = Faculty.objects.get(pk=faculty_id)
    serializer = FacultySerializer(faculty, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def login(request):
    # Ensure email and passwords are posted properly
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Check credentials
    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Create new access and refresh token
    access_token = create_access_token(user.id)

    # Add access token to redis for validating by other services
    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }
    cache.set(access_token, user_data, access_token_lifetime)

    # Create response object
    response = Response(user_data, status=status.HTTP_201_CREATED)
    # Set access token in cookie
    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime, samesite="Lax")

    return response


@api_view(["POST"])
def register(request):
    # Ensure username and passwords are posted is properly
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = serializer.save()
    message = {
        'message': 'User registered successfully',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    access_token = get_access_token(request)

    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Check is token in Redis
    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)

    return Response(user_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def logout(request):
    access_token = request.COOKIES.get('access_token')

    # Check access token is in cookie
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    #  Check access token is in Redis
    if cache.has_key(access_token):
        # Delete access token from Redis
        cache.delete(access_token)

    # Create response object
    message = {"message": "Logged out successfully!"}
    response = Response(message, status=status.HTTP_200_OK)
    # Delete access token from cookie
    response.delete_cookie('access_token')

    return response