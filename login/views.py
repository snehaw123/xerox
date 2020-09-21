from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def register(request):
    if request.method == "POST":
        return HttpResponse("Working on database for register")
    else:
        return render(request, "login/Register.html")

def login(request):
    if request.method == "POST":
        return HttpResponse("Working on database for login")
    else:
        return render(request, "login/Login.html")