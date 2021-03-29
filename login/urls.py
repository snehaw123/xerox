from django.urls import path
from . import views

# Template tagging
app_name = "user"

urlpatterns = [
    path("register/", views.register, name = "register"),
    path("login/", views.login, name="login"),
    path("logout/", views.Logout, name="Logout"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path("resetPassword/<str:url>", views.resetPassword, name = "resetPassword"),
    path("changedPassword/", views.changedPassword, name="changedPassword"),

]