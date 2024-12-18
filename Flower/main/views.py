from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<h1>Тестовый ответ функции index приложения main, проекта Flower "
                        "возврат фразы через HTTPResponse</h1>")

def new(request):
    return HttpResponse("<h1>Это вторая страница проекта Django</h1>")