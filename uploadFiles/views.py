from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

# Create your views here.
def UploadFiles(request):
    if request.method == "POST":
        for f in request.FILES.getlist('file'):
            print(f)
        return HttpResponse("Done Upload")
    else:
        return render(request,"uploadFiles/UploadFiles.html")


