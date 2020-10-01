import os
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from pathlib import Path
from Xpressxerox.settings import MEDIA_ROOT
from Xpressxerox.settings import EMAIL_HOST_USER


# Create your views here.
def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        if password == confirm:
            print("condition password == confirm: ", password == confirm)
            if User.objects.filter(username = email).exists():
                print("User already exists")
                messages.error(request, "Username is taken")
                return redirect('/user/register')
            else:
                user = User.objects.create_user(email = email, password = password, username = email)
                user.save()
                print(user)
                createUserFolders(user)
                messages.success(request, "Welcome to XpressXerox")
                subject = "Thanks for connecting with XpressXerox"
                message = "We care for your privacy. Dont worry about your details. We do not share with anyone." \
                          "This will use for only 2 reason login and forget password."
                sender = EMAIL_HOST_USER
                receiver = email
                send_mail(subject, message, sender, [receiver])
                return redirect("/user/login/")
        else:
            print("Password is not matching ")
            messages.error(request, "Password is not matching")
            return redirect('/user/register')

    else:
        return render(request, "login/Register.html")

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(request, username = email, password = password)
        if user is not None:
            auth.login(request, user)
            print("is_admin ", email == "amirkanai01@gmail.com")
            if email == "amirkanai01@gmail.com":
                return redirect("/action/adminDashboard/")
            else:
                return redirect("/action/userDashboard/")
        else:
            messages.error(request, "Wrong credentials")
            return redirect("/user/login/")


    else:
        return render(request, "login/Login.html")

def Logout(request):
        auth.logout(request)
        messages.error(request, "Logged Out Successfully")
        return redirect("/user/login/")


def createUserFolders(user):
    """
    code 1 stands for per page Black and White print
    code 2 stands for per page Front and Back, Black and White print
    code 3 stands for per page color print

    """
    print(user)
    destination = Path.joinpath(MEDIA_ROOT, str(user).split("@")[0])
    perPage = Path.joinpath(destination, "1")
    back2back = Path.joinpath(destination, "2")
    color = Path.joinpath(destination, "3")

    os.mkdir(destination)
    os.mkdir(perPage)
    os.mkdir(back2back)
    os.mkdir(color)


