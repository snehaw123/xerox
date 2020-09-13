from django.shortcuts import render
from .forms import FileFieldForm
from django.http import HttpResponse

# Create your views here.
def UploadFiles(request):
    if request.method == "POST":
        for f in request.FILES.getlist('file'):
            print(f)
        return HttpResponse("Done Upload")
    else:
        return render(request,"uploadFiles/UploadFiles.html")


