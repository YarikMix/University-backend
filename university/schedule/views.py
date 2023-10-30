from django.shortcuts import render

from schedule.utils.db import *


def index(request):
    query = request.GET.get("group")
    groups = searchGroups(query) if query else getGroups()

    context = {
        "username": "Админ",
        "groups": groups,
        "search_query": query if query else ""
    }

    return render(request, "home_page.html", context)


def groupSchedule(request, group_id):
    group = getGroupById(group_id)

    context = {
        "username": "Админ",
        "group_id": group_id,
        "group_name": group["group_name"],
        "schedule": group["schedule"],
        "students": group["students"]
    }

    return render(request, "group_info_page.html", context)

