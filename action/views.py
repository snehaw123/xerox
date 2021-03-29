import shutil
from django.http import HttpResponsePermanentRedirect, FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Xpressxerox.settings import MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
from login.views import currentTime
from django.core import signing
from .XpressXeroxHelper import *
from PayTm import Checksum
from login.views import currentTime
from django.template.loader import render_to_string
from Xpressxerox.settings import EMAIL_HOST_USER
from django.core.mail import send_mail


MERCHANT_KEY = 'lQ5Ypdx5uSdqNsfS'

AmirFolder = Path.joinpath(MEDIA_ROOT, "amirkanai01@gmail.com")

"""
ALL BELOW TILL NEXT COMMENT FUNCTIONS RELATED TO USER
1. userDashboard
2. sendToPrint
3. handleRequest
4. DocxToPdf

"""

@login_required(login_url='/user/login/')
def userDashboard(request):

    if str(request.user) != "amirkanai01@gmail.com":
        if request.method == "POST":
            print("------Got POST request by USER-----")
            clearTrash(str(request.user))
            option = request.POST["printOption"]
            files = request.FILES.getlist("files")
            status = checkExtention(files)
            check_encrption = isEncrptedPdf(files)
            if option == "0":
                messages.error(request, "Choose Print option")
                return redirect("action:userDashboard")

            elif status != "Files Verified" :
                messages.error(request, status)
                return redirect("action:userDashboard")

            elif check_encrption != "Files are not encrypted" :
                messages.error(request, check_encrption)
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
                             'CALLBACK_URL': 'https://xpressxerox.pythonanywhere.com/action/handleRequest/'}
                data_dict["CHECKSUMHASH"] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
                return render(request,"Paytm/PayTm.html", {"data_dict":data_dict})
        else:
            fileList = getFileList(str(request.user))
            tableTitle = ["Per page B&W print",
                          "Per Page Double Side B&W",
                          "Per page Color print",]
            complex_Dict = dict()
            for i in range(len(fileList)):
                complex_Dict[tableTitle[i]] = fileList[i]

            if "tran" in request.GET and "OID" in request.GET:
                if request.GET["tran"] == "pending" and "OID" in request.GET:
                    pending = Path.joinpath(AmirFolder,"Pending", request.GET["OID"])
                    os.makedirs(pending)
                    for file in request.session["current_files"]:
                        print("Moving from ---->", file)
                        print("moved to ---->", pending)
                        shutil.move(src=file, dst=pending)

                    request.session.pop("current_bill", None)
                    request.session.pop("current_files", None)


                    return redirect("action:userDashboard")

            elif "tran" in request.GET:
                try:
                    tran = signing.loads(request.GET["tran"], key="secreat_key_for_url",
                                         salt="more_encryption_@9160", max_age=5)
                    print("------tran------", tran)
                    paymentStatus(request.session, act=1)
                    request.session.pop("current_bill", None)
                    request.session.pop("current_files", None)

                    return redirect("action:userDashboard")
                except:
                    paymentStatus(request.session, act=0)
                    request.session.pop("current_bill", None)
                    request.session.pop("current_files", None)

                    return redirect("action:userDashboard")

            elif ("current_bill" in request.session) and ("current_files" in request.session):
                paymentStatus(request.session, act=0)
                request.session.pop("current_bill", None)
                request.session.pop("current_files", None)

                return redirect("action:userDashboard")


            return render(request, "action/userDashboard.html" , {"complex_Dict":complex_Dict,  })
    else:
        return redirect('/user/logout/')

@login_required(login_url='/user/login/')
def sendToPrint(request):
    if str(request.user) != "amirkanai01@gmail.com":
        if request.method == "POST":
            option = request.POST["option"]
            file = request.POST["fileName"]
            user_folder =Path.joinpath(MEDIA_ROOT, str(request.user))
            if "Per page B&W print" == option:
                src = Path.joinpath(user_folder,"1",file)
                if isPdf(str(src)):
                    des = Path.joinpath(AmirFolder, "1", uniqueId(str(request.user))+".pdf")
                else:
                    extension = "."+file.split(".")[-1]
                    des = Path.joinpath(AmirFolder, "1", uniqueId(str(request.user)) + extension)
                print("---------Moving file from->",src,"\n-------Moved to ->", des)
                shutil.move(src,des)

            elif "Per Page Double Side B&W" == option:
                src = Path.joinpath(user_folder, "2", file)
                if isPdf(str(src)):
                    des = Path.joinpath(AmirFolder, "2", uniqueId(str(request.user)) + ".pdf")
                else:
                    extension = "."+file.split(".")[-1]
                    des = Path.joinpath(AmirFolder, "2", uniqueId(str(request.user)) + extension)
                print("---------Moving file from->", src, "\n-------Moved to ->", des)
                shutil.move(src,des)

            elif "Per page Color print" == option:
                src = Path.joinpath(user_folder, "3", file)
                if isPdf(str(src)):
                    des = Path.joinpath(AmirFolder, "3", uniqueId(str(request.user)) + ".pdf")
                else:
                    extension = "."+file.split(".")[-1]
                    des = Path.joinpath(AmirFolder, "3", uniqueId(str(request.user)) + extension)
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
    if verify:

        if response_dict["RESPCODE"] == "01":
            messages.success(request, "Payment Successful ")
            email = response_dict["ORDERID"][:-16]
            print("----email----", email)
            mail_dict = {'email': email, 'response_dict': response_dict, 'STATUS': response_dict["STATUS"]}
            print(mail_dict)
            subject = "XpressXerox:- Order Placed"
            html_message = render_to_string('action/Transaction_Mail.html', mail_dict)
            message = 'strip_tags(html_message)'
            sender = EMAIL_HOST_USER
            receiver = email
            send_mail(subject=subject, message=message, from_email=sender, recipient_list=[receiver],
                      html_message=html_message)
            print("transaction is completed and , Mail has been send")
            trans = response_dict["ORDERID"].replace("@", "-") + currentTime()
            print("------trans------", trans)
            trans = signing.dumps(trans, key="secreat_key_for_url", salt="more_encryption_@9160" )
            url = "https://xpressxerox.pythonanywhere.com/action/userDashboard/?tran=" + trans
            return HttpResponsePermanentRedirect(url)

        elif response_dict["RESPCODE"] == "400" or response_dict["RESPCODE"] == "402":
            messages.error(request, "Payment is Pending ")
            email = response_dict["ORDERID"][:-16]
            print("----email----", email)
            mail_dict = {'email': email, 'response_dict': response_dict, 'STATUS': response_dict["STATUS"]}
            print(mail_dict)
            subject = "XpressXerox:- Transaction is Pending"
            html_message = render_to_string('action/Transaction_Mail.html', mail_dict)
            message = 'strip_tags(html_message)'
            sender = EMAIL_HOST_USER
            receiver = email
            send_mail(subject=subject, message=message, from_email=sender, recipient_list=[receiver],
                      html_message=html_message)
            print("transaction is Pending and , Mail has been send")
            url = "https://xpressxerox.pythonanywhere.com/action/userDashboard/?tran=pending&OID={}".format(response_dict["ORDERID"])
            return HttpResponsePermanentRedirect(url)
        else:
            messages.error(request, response_dict['RESPMSG'])
            return HttpResponsePermanentRedirect("https://xpressxerox.pythonanywhere.com/action/userDashboard/?tran=fail")

    else:
        return redirect("action:userDashboard")


@login_required(login_url='/user/login/')
def docxToPdf(request):
    if str(request.user) != "amirkanai01@gmail.com":
        if request.method == "POST":
            files = request.FILES.getlist("files")
            status = checkDoc(files)
            if status == "Files Verified":
                current_doc_files, destination = saveDocx(files, str(request.user))
                current_pdf_files = convToPdf(current_doc_files, str(request.user))
                if len(current_pdf_files) == 1:
                    single_pdf = current_pdf_files[0]
                    file = open(single_pdf, 'rb').read()
                    path, file_name = os.path.split(single_pdf)
                    response = HttpResponse(file, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
                    return response
                else:
                    temp_zip  =  str(request.user) + "-Converted-" + currentTime() + ".zip"
                    temp_zip = Path.joinpath(destination, temp_zip)
                    createZip(zip_name= temp_zip, src = current_pdf_files)
                    zip_file = open(temp_zip, 'rb')
                    return FileResponse(zip_file)
            else:
                messages.error(request, status)
                clearTrash(str(request.user))
                return redirect("action:docxToPdf")
        else:
            clearTrash(str(request.user))
            return render(request, "action/DocxToPdf.html")
    else:
        return redirect("action:userDashboard")





"""
From here all admin related functions are available
1. adminDashboard
2. downloadAdmin
3. pendingOrder
4. deleteOldOrderID
"""


@login_required(login_url='/user/login/')
def adminDashboard(request):

    if str(request.user) == "amirkanai01@gmail.com":
        if request.method == "POST":
            option = request.POST["option"]
            admin_folder = Path.joinpath(MEDIA_ROOT, str(request.user))
            user_seq_list = list()
            user_bill_dict = dict()
            files_full_path = list()
            if "Per page B&W print" == option:
                src = Path.joinpath(admin_folder, "1")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if isPdf(file):
                        pages = pageCounter(Path.joinpath(src, file))
                    else:
                        pages = 1

                    if user not in user_seq_list:
                        user_seq_list.append(user)

                    if user in user_bill_dict:
                        user_bill_dict[user] += pages
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = pages
                        files_full_path.append(Path.joinpath(src, file))


                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill1--------.txt")
                # createBillExcel(bill)
                # updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                createBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                reformatBill(bill)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-1.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-1.zip', 'rb')
                return FileResponse(zip_file)

            elif "Per Page Double Side B&W" == option:
                src = Path.joinpath(admin_folder, "2")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if isPdf(file):
                        pages = (pageCounter(Path.joinpath(src, file))%2 + pageCounter(Path.joinpath(src, file))//2)
                    else:
                        pages = 1

                    if user not in user_seq_list:
                        user_seq_list.append(user)

                    if user in user_bill_dict:
                        user_bill_dict[user] += pages
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = pages
                        files_full_path.append(Path.joinpath(src, file))


                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill2--------.txt")
                # createBillExcel(bill)
                # updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                createBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                reformatBill(bill)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-2.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-2.zip', 'rb')
                return FileResponse(zip_file)

            elif "Per page Color print" == option:
                src = Path.joinpath(admin_folder, "3")
                for file in sorted(os.listdir(src)):
                    user = file.split("-")[0]
                    if isPdf(file):
                        pages = pageCounter(Path.joinpath(src, file))
                    else:
                        pages = 1

                    if user not in user_seq_list:
                        user_seq_list.append(user)

                    if user in user_bill_dict:
                        user_bill_dict[user] += pages
                        files_full_path.append(Path.joinpath(src, file))
                    else:
                        user_bill_dict[user] = pages
                        files_full_path.append(Path.joinpath(src, file))

                print("users in queue---->", user_seq_list)
                print("users bill---->", user_bill_dict)

                bill = Path.joinpath(src, "--------bill3--------.txt")
                # createBillExcel(bill)
                # updatedBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                createBill(bill=bill, users=user_seq_list, record=user_bill_dict)
                reformatBill(bill)
                files_full_path.append(bill)
                createZip(zip_name='zipFolder/Document-3.zip', src=files_full_path)
                deleteFiles(src=files_full_path)
                zip_file = open('zipFolder/Document-3.zip', 'rb')
                return FileResponse(zip_file)
        else:
            fileList = getFileList(str(request.user))
            tableTitle = ["Per page B&W print",
                          "Per Page Double Side B&W",
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

@login_required(login_url='/user/login/')
def pendingOrder(request):
    if str(request.user) == "amirkanai01@gmail.com":
        if request.method == "POST":
            orderId = request.POST["orderId"]
            files_full_path = list()
            src= Path.joinpath(AmirFolder, "Pending", orderId)
            for file in os.listdir(src):
                file = Path.joinpath(src, file)
                files_full_path.append(file)
            createZip(zip_name='zipFolder/{}.zip'.format(orderId), src=files_full_path)
            shutil.rmtree(src)
            zip_file = open('zipFolder/{}.zip'.format(orderId), 'rb')
            return FileResponse(zip_file)
        else:
            src = Path.joinpath(AmirFolder, "Pending")
            subfolders = [ f.name for f in os.scandir(src) if f.is_dir() ]
            if os.listdir('zipFolder'):
                delete_zip_list = list()
                for file in os.listdir('zipFolder'):
                    delete_zip_list.append(os.path.join('zipFolder', file))
                deleteFiles(delete_zip_list)
                print("-----zip files are -----", delete_zip_list)
            return render(request, "action/pendingOrder.html", {"subfolders":subfolders})
    else:
        messages.error(request, 'User can\'t access this feature')
        return redirect('/user/logout/')

@login_required(login_url='/user/login/')
def deleteOldOrderID(request):
    if str(request.user) == "amirkanai01@gmail.com":
        print("working on deleteOldOrderID")
        src = Path.joinpath(AmirFolder, "Pending")
        subfolders = [f.name for f in os.scandir(src) if f.is_dir()]
        TimeNow = int(currentTime().split("-")[0]) #changed currentTime format by -
        print("TimeNow--->",TimeNow)
        counter = 0
        for folder in subfolders:
            folder_date = int(folder.split("-")[1])
            if TimeNow-folder_date >=3:
                shutil.rmtree(Path.joinpath(src, folder))
                counter += 1
        messages.error(request, f'Deleted two Days older {counter} OrderIds')
        return redirect("action:pendingOrder")


    else:
        messages.error(request, 'User can\'t access this feature')
        return redirect('/user/logout/')

