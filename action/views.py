import shutil
from django.http import HttpResponsePermanentRedirect, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Xpressxerox.settings import MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
from .XpressXeroxHelper import *
# Create your views here.
from PayTm import Checksum
MERCHANT_KEY = 'lQ5Ypdx5uSdqNsfS'

AmirFolder = Path.joinpath(MEDIA_ROOT, "amirkanai01")

"""
ALL BELOW TILL NEXT COMMENT FUNCTIONS RELATED TO USER
1. userDashboard
2. sendToPrint
3. handleRequest
"""

@login_required(login_url='/user/login/')
def userDashboard(request):

    if str(request.user) != "amirkanai01@gmail.com":
        if request.method == "POST":
            print("------Got POST request by USER-----")
            option = request.POST["printOption"]
            files = request.FILES.getlist("files")
            status = checkExtention(files)
            if option == "0":
                messages.error(request, "Choose Print option")
                return redirect("action:userDashboard")

            elif status != "Files Verified" :
                messages.error(request, status)
                return redirect("action:userDashboard")

            else:
                request.session["current_bill"] = 0
                request.session["current_files"] = "Null"
                request.session["current_files"], request.session["current_bill"] = uploadFiles(files, str(request.user), option)
                data_dict = {'MID': 'VeMuWi85833969814381',
                             'TXN_AMOUNT': str(request.session["current_bill"]),
                             'ORDER_ID': uniqueId(str(request.user)),
                             'CUST_ID': str(request.user),
                             'INDUSTRY_TYPE_ID': 'Retail',
                             'WEBSITE': 'worldpressplg',
                             'CHANNEL_ID': 'WEB',
                             'CALLBACK_URL': 'http://127.0.0.1:8000/action/handleRequest/'}
                data_dict["CHECKSUMHASH"] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
                return render(request,"Paytm/Paytm.html", {"data_dict":data_dict})
        else:
            fileList = getFileList(str(request.user))
            tableTitle = ["Per page B&W print",
                          "Per page front and back B&W print",
                          "Per page Color print",]
            complex_Dict = dict()
            for i in range(len(fileList)):
                complex_Dict[tableTitle[i]] = fileList[i]

            paymentStatus(request.get_full_path(), request.session)
            if ("current_bill" in request.session) and ("current_files" in request.session):
                request.session.pop("current_bill", None)
                request.session.pop("current_files", None)
                return redirect("action:userDashboard")

            print("----Getting Session inside userDashboard----")
            for key, value in request.session.items():
                print(key, "--> ", value)
            print("----Getting Session inside userDashboard----")

            return render(request, "action/userDashboard.html" , {"complex_Dict":complex_Dict,  })
    else:
        return redirect('/user/logout/')

@login_required(login_url='/user/login/')
def sendToPrint(request):
    if str(request.user) != "amirkanai01@gmail.com":
        if request.method == "POST":
            option = request.POST["option"]
            file = request.POST["fileName"]
            user_folder =Path.joinpath(MEDIA_ROOT, str(request.user).split("@")[0])
            if "Per page B&W print" == option:
                src = Path.joinpath(user_folder,"1",file)
                des = Path.joinpath(AmirFolder, "1", uniqueId(str(request.user))+".pdf")
                print("---------Moving file from->",src,"\n-------Moved to ->", des)
                shutil.move(src, des)


            elif "Per page front and back B&W print" == option:
                src = Path.joinpath(user_folder, "2", file)
                des = Path.joinpath(AmirFolder, "2", uniqueId(str(request.user)) + ".pdf")
                print("---------Moving file from->", src, "\n-------Moved to ->", des)
                shutil.move(src, des)

            elif "Per page Color print" == option:
                src = Path.joinpath(user_folder, "3", file)
                des = Path.joinpath(AmirFolder, "3", uniqueId(str(request.user)) + ".pdf")
                print("---------Moving file from->", src, "\n-------Moved to ->", des)
                shutil.move(src, des)
            messages.success(request, "Document send to print")
            return redirect('action:userDashboard')
        else:
            messages.error(request, "Please Try again")
            return redirect(request, 'action/userDashboard')
    else:
        messages.error(request, 'Admin can\'t access this feature')
        return redirect('/user/logout/')

@csrf_exempt
def handleRequest(request):
    form = request.POST
    response_dict = dict()
    checksum = ""
    for i in form.keys():
        response_dict[i] = form[i]
        if i == "CHECKSUMHASH":
            checksum = form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if response_dict["RESPCODE"] == "01":
        messages.success(request, "Payment Successful ")
        return HttpResponsePermanentRedirect("http://127.0.0.1:8000/action/userDashboard/?tran=succesful")
    else:
        messages.error(request, response_dict['RESPMSG'])
        return HttpResponsePermanentRedirect("http://127.0.0.1:8000/action/userDashboard/?tran=fail")



"""
From here all admin related functions are available
1. adminDashboard
2. downloadAdmin
"""


@login_required(login_url='/user/login/')
def adminDashboard(request):

    if str(request.user) == "amirkanai01@gmail.com":
        if request.method == "POST":
            option = request.POST["option"]
            admin_folder = Path.joinpath(MEDIA_ROOT, str(request.user).split("@")[0])
            user_seq_list = list()
            user_bill_dict = dict()
            files_full_path = list()
            if "Per page B&W print" == option:
                src = Path.joinpath(admin_folder, "1")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if user not in user_seq_list:
                        user_seq_list.append(user)
                    if user in user_bill_dict:
                        user_bill_dict[user] += pageCounter(Path.joinpath(src, file))
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = pageCounter(Path.joinpath(src, file))
                        files_full_path.append(Path.joinpath(src, file))

                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill1--------.xlsx")
                createBillExcel(bill)
                updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-1.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-1.zip', 'rb')
                return FileResponse(zip_file)

            elif "Per page front and back B&W print" == option:
                src = Path.joinpath(admin_folder, "2")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if user not in user_seq_list:
                        user_seq_list.append(user)
                    if user in user_bill_dict:
                        user_bill_dict[user] += (pageCounter(Path.joinpath(src, file))%2 + pageCounter(Path.joinpath(src, file))//2)
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = (pageCounter(Path.joinpath(src, file))%2 + pageCounter(Path.joinpath(src, file))//2)
                        files_full_path.append(Path.joinpath(src, file))

                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill2--------.xlsx")
                createBillExcel(bill)
                updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-2.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-2.zip', 'rb')
                return FileResponse(zip_file)

            elif "Per page Color print" == option:
                src = Path.joinpath(admin_folder, "3")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if user not in user_seq_list:
                        user_seq_list.append(user)
                    if user in user_bill_dict:
                        user_bill_dict[user] += pageCounter(Path.joinpath(src, file))
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = pageCounter(Path.joinpath(src, file))
                        files_full_path.append(Path.joinpath(src, file))

                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill3--------.xlsx")
                createBillExcel(bill)
                updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-3.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-3.zip', 'rb')
                return FileResponse(zip_file)
        else:
            fileList = getFileList(str(request.user))
            tableTitle = ["Per page B&W print",
                          "Per page front and back B&W print",
                          "Per page Color print", ]
            complex_Dict = dict()
            for i in range(len(fileList)):
                complex_Dict[tableTitle[i]] = fileList[i]

            delete_zip_list = list()
            if os.listdir('zipFolder'):
                for file in os.listdir('zipFolder'):
                    delete_zip_list.append(os.path.join('zipFolder', file))
                deleteFiles(delete_zip_list)
            print("-----zip files are -----", delete_zip_list)
            return render(request, "action/adminDashboard.html", {"complex_Dict":complex_Dict})
    else:
        return redirect('/user/logout/')

