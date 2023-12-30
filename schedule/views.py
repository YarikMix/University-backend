from django.shortcuts import render, redirect

from schedule.models import *


def index(request):
    query = request.GET.get("query")
    groups = Group.objects.filter(name__icontains=query).filter(status='Enabled') if query else Group.objects.filter(status='Enabled')

    context = {
        "username": "Админ",
        "search_query": query if query else "",
        "groups": groups
    }

    return render(request, "home_page.html", context)


def groupSchedule(request, group_id):

    context = {
        "username": "Админ",
        "group": Group.objects.get(id=group_id)
    }

    return render(request, "group_info_page.html", context)


def groupDelete(request, group_id):

    Group.objects.get(id=group_id).delete()

    return redirect("/")