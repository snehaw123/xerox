from django.urls import path
from . import views

urlpatterns = [
    path("", views.UploadFiles, name = "UploadFiles")
]