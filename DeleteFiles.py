import os, datetime
from action.XpressXeroxHelper import clearTrash

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

upload_folder = r"/home/xpressxerox/DjangoXpressXerox/media"
all_user = [f.name for f in os.scandir(upload_folder ) if f.is_dir()]
print("-----printing all users------\n", all_user)

run_time = str(datetime.datetime.now()).split(" ")[0].replace("-","")
run_time = int(run_time)
print("-----Script running date------", run_time)

for user in all_user:
    if user != "amirkanai01@gmail.com":

        for sub_folder in ["1","2","3","trash"]:

            sub_folder = os.path.join(upload_folder,user,sub_folder)
            print(sub_folder)
            files_in_subfolder = sorted(os.listdir(sub_folder))

            if "trash" in sub_folder:
                clearTrash(user)

            else:

                for file in files_in_subfolder:
                    file = os.path.join(sub_folder,file)
                    date = str(modification_date(file)).split(" ")[0].replace("-","")
                    date = int(date)
                    if run_time-date >= 3:
                        print("file removed :-", file)
                        os.remove(file)



//We are converting this web into app for both android and IOS . 
