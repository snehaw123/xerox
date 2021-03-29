import os
from django.core.mail import send_mail
from django.utils import timezone
from django.core import signing
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from pathlib import Path
from Xpressxerox.settings import MEDIA_ROOT
from Xpressxerox.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string




# Create your views here.
def register(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        if password == confirm:
            # print("condition password == confirm: ", password == confirm)
            if User.objects.filter(username = email).exists():
                # print("User already exists")
                messages.error(request, "Username is taken")
                return redirect('/user/register')
            else:
                #messages.success(request, "Welcome to XpressXerox")
                subject = "Thanks for connecting with XpressXerox"
                html_message = render_to_string('login/Welcome_Mail.html', {'email': email})
                message = 'strip_tags(html_message)'
                print(message)
                sender = EMAIL_HOST_USER
                receiver = email
                send_mail(subject=subject, message=message, from_email=sender, recipient_list=[receiver],
                          html_message=html_message)
                user = User.objects.create_user(email=email, password=password, username=email)
                user.save()
                print(user)
                createUserFolders(user)
                return redirect("/user/login/")
        else:
            print("Password is not matching ")
            messages.error(request, "Password is not matching")
            return redirect('/user/register')

    else:
        return render(request, "login/Register.html")

def login(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
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

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"].lower()
        if User.objects.filter(username=email).exists():
            temp_url = email.replace("@", "-")+currentTime()
            url = signing.dumps(temp_url, key= "secreat_key_for_url", salt= "more_encryption_@9160",)
            messages.success(request,"We have send mail to your email address")
            subject = "XpressXerox: FORGOT PASSWORD"
            link = "https://xpressxerox.pythonanywhere.com//user/resetPassword/"+ url
            html_message = render_to_string('login/ResetPassword_Mail.html', {'email': email, 'link':link})
            message = 'strip_tags(html_message)'
            sender = EMAIL_HOST_USER
            receiver = email
            send_mail(subject = subject,message = message, from_email=sender, recipient_list= [receiver], html_message=html_message)
            print(message)
            return redirect("/")
        else:
            messages.error(request, "Entered email is not registered")
            return render(request, "login/forgotPassword.html")
    else:
        return render(request, "login/forgotPassword.html")

def resetPassword(request, url):
    try:
        url = signing.loads(url, key= "secreat_key_for_url", salt= "more_encryption_@9160", max_age= 1800)
        email = url[:-15]
        email = email.replace("-", "@").lower()
        print("---------",email,"---------")
        messages.success(request, "You can reset your password")
        return render(request, "login/ResetPassword.html", {"email": email})
    except signing.BadSignature:
        messages.error(request, "Link modification detected or Link is expired")
        return redirect('/')
    except:
        messages.error(request, "Try after some time")
        return redirect('/')

def changedPassword(request):
    email = request.POST["email"].lower()
    password = request.POST["password"]
    print("-----",email, "----", password)
    u = User.objects.get(username= email)
    u.set_password(password)
    u.save()
    messages.success(request, "Password changed successfully")
    return redirect('user:login')
    # except:
    #     messages.error(request, "Try after some time")
    #     return redirect('user:register')



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
    destination = Path.joinpath(MEDIA_ROOT, str(user))
    os.mkdir(destination)
    trash = Path.joinpath(destination, "trash")
    os.mkdir(trash)

    for i in  [trash, destination]:
        for j in "123":
            os.mkdir(Path.joinpath(i,j))

# def sendMail(recevier, reason):
#     if res

def currentTime():
    return str(timezone.now().strftime('%Y%m%d-%H%M%S'))


