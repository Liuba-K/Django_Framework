from django.http import HttpResponse
from django.shortcuts import render


def hello_view(request):
    return HttpResponse("Hello world")
