import requests
import magic
import getpass
import os
import pathlib
import tkinter as tk
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder
from pynput import keyboard


def submit_work(submission_path,file_path,name,password):
    loginData = { 'anchor':"", 'username': name,'password': password, 'logintoken':""}
    cookiesx = {}
    userTestSession = ""
    myHeaders = {
        "Host": "muele.mak.ac.ug",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Gpc": "1",
        "Te": "trailers"
    }

    try:
        s = requests.Session()
        s.headers.update(myHeaders)
        r = s.get('https://muele.mak.ac.ug/login/index.php')
        for cookie in r.cookies:
            s.cookies.set_cookie(cookie)
        if("Forgotten your username or password?" in r.text):
            soup = BeautifulSoup(r.text,'html.parser')
            logintoken = soup.find_all('input')[1]['value']
            loginData['logintoken'] = logintoken

            loginHeaders = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://muele.mak.ac.ug",
                "Referer": "https://muele.mak.ac.ug/login/index.php",
                "Sec-Fetch-Site": "same-origin"
            } 
            print("Logging in ...")
            r = s.post('https://muele.mak.ac.ug/login/index.php',data=loginData, headers = loginHeaders,allow_redirects=False)

            for cookie in r.cookies:
                s.cookies.set_cookie(cookie)

            if "testsession" in r.headers['Location']:
                print("Login in successfull")
                d = s.get(submission_path)
                
                soup = BeautifulSoup(d.text,'html.parser')
                #get the ctx_id
                ctx_data = soup.body.find('object')['data'].split('&')
                itemId = ctx_data[2].split("=")[1]
                ctx_id = ctx_data[7].split("=")[1]
                sessKey = ctx_data[9].split("=")[1]

                #get user name
                user_name = soup.body.find(class_='usertext mr-1').string
                #get client id
                client_id =  soup.body.find(class_="filemanager w-100 fm-loading")['id'].split("-")[1]
                
                save_submit_param = {}

                for x in soup.body.find_all('input'):
                    if(x['type'] == "hidden"):
                        save_submit_param[x['name']] = x['value']                
                save_submit_param["submitbutton"] = "Save changes"

                file_name = file_path.split("/")[-1]
                mime_type = magic.from_file(file_path, mime=True)
                multipart_data = MultipartEncoder(
                    fields={
                        'repo_upload_file':(file_name, open(file_path,'rb'),mime_type),
                        'sesskey':sessKey,
                        'repo_id': '3',
                        'itemid': itemId,
                        'author': user_name,
                        'savepath':'/',
                        'title': file_name,
                        'ctx_id': ctx_id
                    }
                )
                uploadHeaders = {
                    "Origin": "https://muele.mak.ac.ug",
                    "Referer": submission_path,
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Accept": "*/*",
                    "Sec-Fetch-Site": "same-origin",
                }

                
                file_upload_url = "https://muele.mak.ac.ug/repository/repository_ajax.php?action=upload"
                file_submission_url = "https://muele.mak.ac.ug/mod/assign/view.php"

                #clear off previous submission
                uploadHeaders['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
                file_delete_url = "https://muele.mak.ac.ug/repository/repository_ajax.php?action=delete"
                r = s.post(file_delete_url, data = {'sesskey': sessKey,'itemId': itemId,'filepath':'/','filename':file_name,'client_id': client_id}, headers = uploadHeaders.update({"X-Requested-With": "XMLHttpRequest"}))
                # print(r.request.body)
                # print(r.text)
                # loginHeaders['Referer'] = submission_path.replace('editsubmission', 'removesubmissionconfirm')
                # deleteSubData = {'id': save_submit_param['id'], 'action':'removesubmission', 'userid': save_submit_param['userid'], 'sesskey': save_submit_param['sesskey']}

                #fake visit to removesubmissionconfirm
                # r = s.get(loginHeaders['Referer'], headers= {'Referer': submission_path.replace('editsubmission','view'),'Sec-Fetch-Site':'same-origin'})
                # print(r.request.headers)
                # print(r.headers)
                # r = s.post(file_submission_url, data= deleteSubData , headers= loginHeaders, allow_redirects=False)
                print("Removed Old version............\nSubmitting new version")

                uploadHeaders['Content-Type'] = multipart_data.content_type
                r = s.post(file_upload_url, data = multipart_data, headers=uploadHeaders)
           
                loginHeaders['Referer'] = submission_path
                if("draftfile" in r.text):
                    print("Submission Successful...\nSAVING FILES...")
                    r = s.post(file_submission_url,data = save_submit_param, headers=loginHeaders)
                    
                    if("Submission status" in r.text):
                        print("WORK SUBMITTED SUCCESSFULLY")
                
                print('Listening...')
         
            else:
                print("Wrong Credentials")


    except requests.exceptions.ConnectionError as e:
        print(e)

def on_activate_upload():
    submit_work(submission_path, filepath, username, password)

def on_activate_quit():
    print("Exiting Program...")
    exit(0)

username = ""
password = ""
submission_path = ""
filepath = ""

if __name__ ==  "__main__":
    print("Welcome To Muele Automation Tool (MAT)  by HIX")
    username = input("Enter Username: ")
    password = getpass.getpass("Enter Password: ")
    while(True):
        submission_path = input("Enter Submission Path: ")
        if (submission_path.endswith("editsubmission") and submission_path.startswith("https://muele.mak.ac.ug/mod/assign/view.php?id")):
            break
        else:
            print("Wrong link Try again!")
    print("Choose File to Track & Upload")
    root = tk.Tk()
    root.withdraw()
    filepath = askopenfilename()
    print("Filepath:    ",filepath)
    print("\n*********STARTED LISTENING**********\n  Use Ctrl + Shift + m to Upload File\n    Ctrl + Shift + q to quit")

    try:
        #keybard listener
        with keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+m': on_activate_upload,
            '<ctrl>+<shift>+q': on_activate_quit}) as h:
            h.join()
    except:
        pass
