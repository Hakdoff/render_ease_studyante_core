from django.shortcuts import render, redirect


def chatPage(request, *args, **kwargs):
    context = {}
    return render(request, "chat/chatPage.html", context)
