from rest_framework import serializers

from .models import *


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True, many=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = "__all__"

