from django.shortcuts import render
from datetime import datetime


# Create your views here.
def index(request):
    return render(request, 'main/index.html', {'current_year': datetime.now().year})


def user(request):
    return render(request, 'main/user.html')
