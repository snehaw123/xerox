from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.

def homePage(request):
   Total_user = len(User.objects.all())
   return render(request, "login/Home.html",{"Total_user": Total_user})

def About(request):
   return render(request, "login/About.html")

def FAQ(request):
   return render(request, "login/FAQ.html")