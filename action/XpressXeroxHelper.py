import os
from pathlib import Path
from Xpressxerox.settings import MEDIA_ROOT
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from PyPDF2 import PdfFileReader
from openpyxl import Workbook, load_workbook
import zipfile

""""
BELOW FUNCTIONS ARE FOR HELPING PURPOSE . 
LIST OF ALL FUNCTIONS

1. getFileList
2. checkExtention
3. uploadFiles
"""

def getFileList(user):
    """
    user has 3 sub folder B&w , back2back and color.
    this will tell sequential files in each folder

    """
    fileList = []
    for i in "123":
        destination = Path.joinpath(MEDIA_ROOT, user.split("@")[0])
        destination = Path.joinpath(destination, i)
        files = sorted(os.listdir(destination))
        #print(destination,"\n",files)
        fileList.append(files)
    return fileList

def checkExtention(files):
    """
    This function will check extention of each file.

    """
    for file in files:
        if file.name.lower().split(".")[-1] != 'pdf':
            return file.name + " is not PDF"
    return "Files Verified"

def uploadFiles(files, user, option):
    """
    This function work on option argument option will tell where to stor file
    if option is 1 file will store in sub folder 1 of user which is for Print per page B&W.
    option 2 tell sub folder 2 of user which for Print BacktoBack on page with B&W.
    option 3 for sub folder 3 of user which tells print per page is color.

    """

    destination = Path.joinpath(MEDIA_ROOT, user.split("@")[0])
    current_files =[]
    current_bill = 0
    if option == "1":
        destination = Path.joinpath(destination, "1")
    elif option == "2":
        destination = Path.joinpath(destination, "2")
    elif option == "3":
        destination = Path.joinpath(destination, "3")

    for file in files:
        fs = FileSystemStorage(location=destination)
        filename = fs.save(file.name, file)
        filename = os.path.join(destination, filename)
        current_files.append(filename)
        pages = pageCounter(filename)

        if option == "1":
            current_bill += pages

        elif option == "2":
            if pages > 40:
                current_bill = current_bill + ((pages%2 + pages//2)*1.5)
            else:
                current_bill = current_bill + ((pages%2 + pages//2)*2)

        elif option == "3":
            current_bill += (pages * 8)
    print("current_files:- ", current_files, "\ncurrent_bill:- ", current_bill)
    return current_files, current_bill

def paymentStatus(url, session):
    """
    check the keys current_bill n current_files are present
    """
    if ("current_bill" in session) and ("current_files" in session):
        if "tran=fail" in url:
            for file in session["current_files"]:
                os.remove(file)





def uniqueId(username):
    """
    Using username and timezone will return UniqueId username+ now
    """
    username = username.split("@")[0]
    now = timezone.now()
    now = now.strftime('-%Y%m%d-%H%M%S')
    return str(username+now)

def pageCounter(file):
    """
        parameters:- file - path of file
        count number of pages in file
    """
    temp = open(file, "rb")
    pdf = PdfFileReader(temp)
    pages = pdf.getNumPages()
    temp.close()
    print("document ", file, "pages ", pages)

    return int(pages)

def createBillExcel(bill):
    """
        parameters:- bill - path of bill xcel files
        create empty document
    """
    wb = Workbook()
    wb.save(bill)
    wb.close()
    print("--------Bill file created--------")
    return None

def updatedBill(bill, users, record):
    """
        parameters:- bill - path of bill xcel files, users :- sorted list of user send doc to print,
        record dict has record of users and how many pages they want to print
    """
    wb = load_workbook(bill)
    sheet = wb["Sheet"]
    sheet.cell(row=1, column=1).value = "UserName"
    sheet.cell(row=1, column=2).value = "Pages"
    r = 2
    for entry in users:
        sheet.cell(row=r, column=1).value = entry
        sheet.cell(row=r, column=2).value = record[entry]
        r += 1

    wb.save(bill)
    wb.close()
    print("--------Bill file Updated--------")
    return None

def createZip(zip_name, src):
    """
        parameter:- zip file name , folder path
        This will create zip file
    """
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for file in src:
        zipf.write(file)
    zipf.close()
    print("--------zip file created --------")
    return None


def deleteFiles(src):
    """
        parameter:- folder path with files
        This will delete files from folder
    """
    for file in src:
        os.remove(file)
    print("--------deleted files-------")
    return None


