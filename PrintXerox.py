import shutil
import os
from datetime import datetime
import zipfile
import win32print
import win32event
import win32ui
from win32comext.shell import shell
from PIL import Image
from PIL import ImageWin

"""
Part 1 :-   Getting which zip files are present in Download Folder
"""

download_folder = r"C:\Users\mkcl6\Downloads"
admin_folder = r"C:\Users\mkcl6\Desktop\XpressXerox\admin"
print_option = ""
path_of_zip = list()
path_of_sub_folder = list()
files_in_download_folder = sorted(os.listdir(download_folder))
server_path = os.path.join("home", "xpressxerox", "DjangoXpressXerox", "media", "amirkanai01@gmail.com")

if "Document-1.zip" in files_in_download_folder:
    print_option += "1"
    path_of_zip.append(os.path.join(download_folder, "Document-1.zip"))
    path_of_sub_folder.append(os.path.join(admin_folder, "1"))

if "Document-2.zip" in files_in_download_folder:
    print_option += "2"
    path_of_zip.append(os.path.join(download_folder, "Document-2.zip"))
    path_of_sub_folder.append(os.path.join(admin_folder, "2"))

if "Document-3.zip" in files_in_download_folder:
    print_option += "3"
    path_of_zip.append(os.path.join(download_folder, "Document-3.zip"))
    path_of_sub_folder.append(os.path.join(admin_folder, "3"))

print("----Detected Zip files are----")
for zip in path_of_zip:
    print(zip)
# print(path_of_sub_folder)
print("-----Phase 1 completed----")

"""
Part 2 :-   Removing current admin folder and creating new with latest sub folder according to zip
"""
print("---- folders are created ----")
shutil.rmtree(admin_folder)

os.mkdir(admin_folder)

for folder in path_of_sub_folder:
    os.mkdir(folder)
    print(folder)

print("-----Phase 2 completed----")

"""
Part 3 :-   Extracting zip to respective sub folder of admin then
            Moving zip from download to zip Backup folder with current time stamp 
"""

print("---- Zip Extraction started and Moving zip to Backup ----")
for index, zip_path in enumerate(path_of_zip):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path_of_sub_folder[index])

time_stamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
time_stamp = os.path.join("Zip Backup", time_stamp)
os.mkdir(time_stamp)

for zip_path in path_of_zip:
    shutil.move(zip_path, time_stamp)

print("---- Phase 3 completed -----")
"""
 part4 :-    Printing documents in sequence
"""
printers = ["iR3300", "iR5050"]
opt = int(input("----Choose printer----\n0. iR3300\n1. i5050\n"))
printer = printers[opt]
print("Selected option is--->", printer)


def send_pdf(file, duplex):
    """
    duplex state double side or not
    """
    if duplex == 1:
        cmd = f'PDFtoPrinter {file} "{printer} duplex1"'
    elif duplex == 2:
        cmd = f'PDFtoPrinter {file} "{printer} duplex2"'
    elif duplex == 3:
        cmd = f'PDFtoPrinter {file} "colour printer"'

    cmd = f"start /wait cmd /c {cmd}"
    rtn = os.system(cmd)


def getExtention(file):
    return file.lower().split(".")[-1]


def send_txt(file_path, printer_name):
    default_printer = win32print.GetDefaultPrinter()
    print("---current default printer-----", default_printer)
    win32print.SetDefaultPrinter(printer_name)
    handle = win32print.OpenPrinter(printer_name, {"DesiredAccess": win32print.PRINTER_ALL_ACCESS})
    print("---changed default printer-----", win32print.GetDefaultPrinter())
    dict = shell.ShellExecuteEx(fMask=256 + 64, lpVerb='print', lpFile=file_path, lpParameters=printer_name)
    wait = dict["hProcess"]
    win32event.WaitForSingleObject(wait, -1)
    win32print.ClosePrinter(handle)
    win32print.SetDefaultPrinter(default_printer)
    print("---current default printer-----", win32print.GetDefaultPrinter())



def send_img(file_path, printer_name):
    PHYSICALWIDTH = 110
    PHYSICALHEIGHT = 111
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(printer_name)
    printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)

    bmp = Image.open(file_path)
    if bmp.size[0] < bmp.size[1]:
        bmp = bmp.rotate(90)

    hDC.StartDoc(file_path)
    hDC.StartPage()

    dib = ImageWin.Dib(bmp)
    dib.draw(hDC.GetHandleOutput(), (0, 0, printer_size[0], printer_size[1]))

    hDC.EndPage()
    hDC.EndDoc()
    hDC.DeleteDC()


for index, folder in enumerate(path_of_sub_folder):
    src = os.path.join(folder, server_path, print_option[index])
    print(src)
    for file in sorted(os.listdir(src)):
        file_path = os.path.join(src, file)
        print(file)

        if getExtention(file) == "pdf":

            if print_option[index] == "1":
                send_pdf(file_path, duplex=1)
            elif print_option[index] == '2':
                send_pdf(file_path, duplex=2)
            elif print_option[index] == "3":
                send_pdf(file_path, duplex=3)

        elif getExtention(file) == "txt":

            if print_option[index] == "1":
                send_txt(file_path, f'{printer} duplex1')

            elif print_option[index] == '2':
                send_txt(file_path, f'{printer} duplex2')

            elif print_option[index] == "3":
                send_txt(file_path, 'colour printer')

        elif getExtention(file):

            if print_option[index] == "1":
                send_img(file_path, f'{printer} duplex1')

            elif print_option[index] == '2':
                send_img(file_path, f'{printer} duplex2')

            elif print_option[index] == "3":
                send_img(file_path, 'colour printer')

    print("-----------DONE FOLDER-------------")

print("--------DONE PRINTNG-------")
