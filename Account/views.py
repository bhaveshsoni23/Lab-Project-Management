from django.shortcuts import render,redirect
from django.contrib import messages, auth
from MyProject import settings
from MyProject.static import login_status_server
import mysql.connector
import time
import uuid
import random
import string
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import sys
from PIL import Image
import shutil
import mimetypes
import bfa
from django.shortcuts import render
import pickle
from AptLibrary.Python.Script import AptExtractHostName
from AptLibrary.Python.Script import AptListToString
from MyProject.static import dev_setting
import requests
import json
import re

def register(request):
    try:
        login_status_server_response = login_status_server.login_status_server(request)
        context = {
            'is_login_status_server':login_status_server.is_login_status_server  
        }
        if(login_status_server_response == 'False'):
            if request.method == 'POST' and request.FILES['ProfileImage']:
                # Database connection with mysql#
                conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
                #Creating a cursor object using the cursor() method
                connCursor = conn.cursor(buffered=True)
                
                EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'
                key = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10)) 
                account_id = 'g'+str(time.time()).replace('.','')+key
                AccountUrl = f'Media/register_account/{account_id}'
                try:
                    first_name = request.POST['first_name']
                    last_name = request.POST['last_name']
                    email = request.POST['email']
                    password = request.POST['password']
                    password2 = request.POST['password2']
                    ProfileImage = request.FILES['ProfileImage']

                    if password == password2:
                        if(len(first_name) < 2 or len(first_name) > 15):
                            messages.error(request, 'first name length must be between 2 to 15')
                            return redirect('register')
                        if(len(last_name) < 2 or len(last_name) > 15):
                            messages.error(request, 'last name length must be between 2 to 15')
                            return redirect('register')
                        if(len(email) < 10 or len(email) > 50):
                            messages.error(request, 'invalid email id detect')
                            return redirect('register')
                        if(len(password) < 8 or len(password) > 32):
                            messages.error(request, 'password length must be between 8 to 32')
                            return redirect('register')
                        

                        file_name, file_extension = os.path.splitext(ProfileImage.name)
                        if(file_extension.lower() != '.jpeg' and file_extension.lower() != '.jpg' and file_extension.lower() != '.png'):
                            messages.error(request, 'only jpeg and png type is supported for profile image')
                            return redirect('register')
                    
                        profile_id = 'gp'+account_id+str(time.time()).replace('.','')+key
                        tmp_id = 'tmp'+key+str(time.time())+key

                        current_time = time.time()
                        
                        if not os.path.exists(AccountUrl):
                            os.makedirs(AccountUrl)

                        MediaUrlTmp = f'{AccountUrl}/tmp_profile/{tmp_id}'
                        settings.MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),MediaUrlTmp)
                        fs = FileSystemStorage()
                        filename = fs.save(ProfileImage.name, ProfileImage)
                        uploaded_file_url = f'''{settings.MEDIA_ROOT}/{filename}'''
                        uploaded_file_url = uploaded_file_url.replace('\\','/');
                        filemime = mimetypes.MimeTypes().guess_type(uploaded_file_url)
                        if(filemime[0].lower() != 'image/jpeg' and filemime[0].lower() != 'image/png' and filemime[0].lower() != 'image/jpg'):
                            if os.path.exists(AccountUrl):
                                shutil.rmtree(AccountUrl)
                            messages.error(request, 'only jpeg and png type is supported for profile image')
                            return redirect('register')
                        file_size_mb = (os.path.getsize(uploaded_file_url)/1024)/1024
                        if(file_size_mb > 2):
                            if os.path.exists(AccountUrl):
                                shutil.rmtree(AccountUrl)
                            messages.error(request, 'profile image size must be under 2mb')
                            return redirect('register')
                        picture = Image.open(uploaded_file_url)
                        pictureRGB = picture.convert('RGB')
                        pictureRGB.save(f"{MediaUrlTmp}/{filename}")

                        file_name, file_extension = os.path.splitext(f"{MediaUrlTmp}/{filename}")
                        profile_id = profile_id+file_extension;

                        oldsize = os.stat(f"{MediaUrlTmp}/{filename}").st_size
                        picture = Image.open(f"{MediaUrlTmp}/{filename}")
                        dim = picture.size
                        MediaUrl = f'{AccountUrl}/profile_image'
                        settings.MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),MediaUrl)
                        if not os.path.exists(MediaUrl):
                            os.makedirs(MediaUrl)
                        #set quality= to the preferred quality. 
                        #I found that 85 has no difference in my 6-10mb files and that 65 is the lowest reasonable number
                        picture.save(f'''{MediaUrl}/{profile_id}''',"JPEG",optimize=True,quality=50)
                        
                        newsize = os.stat(os.path.join(request.path,f'''{MediaUrl}/{profile_id}''')).st_size
                        percent = (oldsize-newsize)/float(oldsize)*100

                        if os.path.exists(MediaUrlTmp):
                            shutil.rmtree(MediaUrlTmp)


                        sql = f"SELECT * FROM register_account WHERE email = (AES_ENCRYPT(%s,'{EPASS}'))"
                        connCursor.execute(sql, (email,))
                        conn.commit()
                        if(connCursor.rowcount >= 1):
                            if os.path.exists(AccountUrl):
                                shutil.rmtree(AccountUrl)
                            messages.error(request, 'email aleady exists')
                            return redirect('register')
                    
                        else:

                            sql = f"INSERT INTO register_account (status, account_id, fname, lname, email, position, profile_id, password, register_time, lst_upd_time, last_activity_time, pass_upd_time) VALUES (AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(SHA2(DES_ENCRYPT(SHA2(%s,256),'{EPASS}Password{EPASS}'),512),'{EPASS}Password{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'))"
                            val = ('tmpactive',account_id,first_name,last_name,email,'user',profile_id,password,current_time,current_time,current_time,current_time)
                            connCursor.execute(sql, val)
                            conn.commit()
                            if(connCursor.rowcount >= 1):
                                messages.success(request, 'account successfully created')
                                return redirect('login')
                            else:
                                if os.path.exists(AccountUrl):
                                    shutil.rmtree(AccountUrl)
                                messages.error(request, 'account creation failed')
                                return redirect('register')
                    else:
                        if os.path.exists(AccountUrl):
                            shutil.rmtree(AccountUrl)
                        messages.error(request, 'Passwords do not match')
                        return redirect('register')

                except:
                    if os.path.exists(AccountUrl):
                        shutil.rmtree(AccountUrl)
                    messages.error(request, 'somthing went wrong')
                    return redirect('register')

            else:
                return render(request, 'accounts/register.html',context)
        else:
            messages.info(request,f"Yor are already login as {login_status_server_response['email']}")
            return redirect('index')
    except:
        return render(request, 'accounts/register.html',context)

def login(request):
    try:
        login_status_server_response = login_status_server.login_status_server(request)
        context = {
            'is_login_status_server':login_status_server.is_login_status_server  
        }
        if(login_status_server_response == 'False'):
            if request.method == 'POST' and len(request.POST['email']) > 0 and len(request.POST['password']) > 0:
                # Database connection with mysql#
                conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
                #Creating a cursor object using the cursor() method
                connCursor = conn.cursor(buffered=True)

                EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'
                if(request.POST.get('email') and request.POST.get('password')):
                    email = request.POST['email']
                    password = request.POST['password']
                else:
                    messages.error(request,"invalid email or password")
                    return redirect('login')

                key = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10)) 
                try:
                    fp = bfa.fingerprint.get(request)
                except (ConnectionError, ValueError):
                   messages.error(request,"Login failed")
                   return redirect('login')

                login_id = 'lg'+key+str(time.time()).replace('.','')+key
                login_id_with_fp = {'id':login_id,'bfp':fp}

                sql = f"SELECT AES_DECRYPT(login_data,'{EPASS}'),AES_DECRYPT(account_id,'{EPASS}') FROM register_account WHERE email = AES_ENCRYPT(%s,'{EPASS}') and password = AES_ENCRYPT(SHA2(DES_ENCRYPT(SHA2(%s,256),'{EPASS}Password{EPASS}'),512),'{EPASS}Password{EPASS}')"
                connCursor.execute(sql, (email,password,))
                conn.commit()
                if(connCursor.rowcount != 1):
                    messages.error(request, 'invalid email or password')
                    return redirect('login')

                result = connCursor.fetchall()

                if(len(result) > 0 and len(result[0]) > 0 and result[0][1] != None and len(result[0][1]) > 0):
                    account_id = result[0][1]
                else:
                    messages.error(request,'login falied')
                    return redirect('login')

                if(len(result) > 0 and len(result[0]) > 0 and result[0][0] != None and len(result[0][0]) > 0 and isinstance(result[0][0], bytearray)):
                    try:
                        login_data_fetch = pickle.loads(result[0][0])
                    except:
                        login_data_fetch = dict()
                else:
                    login_data_fetch = dict()


                if "login_id" in login_data_fetch and len(login_data_fetch['login_id']) > 0 and isinstance(login_data_fetch['login_id'], list):
                    login_id_fetch = login_data_fetch['login_id']
                else:
                    login_id_fetch = list()

                login_new_id = list()
                if(len(login_id_fetch) > 0):
                    i=0
                    for item in login_id_fetch:
                        i=i+1
                        if(i>4):
                            break
                        login_new_id.append(item)
                login_new_id.insert(0,login_id_with_fp)

                login_data_fetch['login_id'] = login_new_id
                login_data = pickle.dumps(login_data_fetch)
                sql = f"UPDATE register_account SET login_data = AES_ENCRYPT(%s,'{EPASS}') WHERE account_id = AES_ENCRYPT(%s,'{EPASS}')"
                connCursor.execute(sql, (login_data,account_id,))
                conn.commit()

                if(connCursor.rowcount == 1):
                    responce =  redirect('index')
                    responce.set_cookie('LID',login_id)
                    responce.set_cookie('LAID',account_id)
                    messages.success(request,"logined successfully")
                    return responce
                else:
                    messages.error(request,"login falied")
                    return redirect('login')
            else:
                return render(request,'accounts/login.html',context)
        else:
            messages.info(request,f"Yor are already login as {login_status_server_response['email']}")
            return redirect('index')
    except:
        return render(request,'accounts/login.html',context)


def logout(request):
    if request.method == 'POST':
        try:
            login_status_server_response = login_status_server.login_status_server(request)
            if(login_status_server_response == 'False'):
                return redirect('login') 
            else:
                # Database connection with mysql#
                conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
                #Creating a cursor object using the cursor() method
                connCursor = conn.cursor(buffered=True)

                EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'

                sql = f"SELECT AES_DECRYPT(login_data,'{EPASS}') FROM register_account WHERE account_id = AES_ENCRYPT(%s,'{EPASS}')"
                connCursor.execute(sql, (login_status_server_response['account_id'],))
                conn.commit()
                if(connCursor.rowcount != 1):
                    messages.error(request, 'Logout falied')
                    return redirect('dashboard')
                else:
                    result = connCursor.fetchall()

                    if(len(result) < 1 or len(result[0]) < 1):
                        messages.error(request, 'Logout falied')
                        return redirect('dashboard')

                    if(result[0][0] == None or len(result[0][0]) < 1):
                        messages.error(request, 'Logout falied')
                        return redirect('dashboard')
                    else:
                        login_data_fetch = pickle.loads(result[0][0])
                        if "login_id" in login_data_fetch and len(login_data_fetch['login_id']) > 0 and isinstance(login_data_fetch['login_id'], list):
                            login_id_fetch = login_data_fetch['login_id']

                            login_new_id = list()
                            is_logout = False
                            if(len(login_id_fetch) > 0):
                                for item in login_id_fetch:
                                    if(item['id'] != login_status_server_response['LID']):
                                        login_new_id.append(item)
                                    else:
                                        is_logout = True

                            if(is_logout != True):
                                messages.error(request, 'Logout falied')
                                return redirect('dashboard')
                            else:
                                login_data_fetch['login_id'] = login_new_id
                                login_data = pickle.dumps(login_data_fetch)
                                sql = f"UPDATE register_account SET login_data = AES_ENCRYPT(%s,'{EPASS}') WHERE account_id = AES_ENCRYPT(%s,'{EPASS}')"
                                connCursor.execute(sql, (login_data,login_status_server_response['account_id'],))
                                conn.commit()

                                if(connCursor.rowcount == 1):
                                    responce =  redirect('login')
                                    responce.set_cookie('LID',False)
                                    responce.set_cookie('LAID',False)
                                    messages.success(request,"Logout successfully")
                                    return responce
                                else:
                                    messages.error(request, 'Logout falied')
                                    return redirect('dashboard')
                        else:
                            messages.error(request, 'Logout falied')
                            return redirect('dashboard')
        except:
            messages.error(request, 'Logout falied1')
            return redirect('dashboard')

def dashboard(request):
    login_status_server_response = login_status_server.login_status_server(request)
    if(login_status_server_response != 'False'):
        if(request.POST.get('form_type')):
            try:
                LID = request.COOKIES['LID']
                LAID = request.COOKIES['LAID']
                BFP = bfa.fingerprint.get(request)
                AccountUrl = f'Media/register_account/{LAID}'
                key = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 10)) 
                project_id = 'pui'+str(time.time()).replace('.','')+key
                project_full_path = AccountUrl+'/project_upload/'+project_id
                project_full_path_media = project_full_path+'/media'
                ProjectImage_id = 'puimg'+str(time.time()).replace('.','')+key
                project_tmp_media = project_full_path+'/tmpMedia'
                project_image_array = list()
                current_time = time.time()
            except:
                messages.error(request,'Client not logined')
                return redirect('dashboard')

            try:
                payload = dict(LID = LID, LAID = LAID, BFP = BFP)
                url = dev_setting.dev_domain_name_with_protocol+"/login_status_client/"
                headers = {
                    'accept-encoding': "application/gzip",
                    'content-type': "application/x-www-form-urlencoded"
                }
                response = requests.request("POST", url, data=payload)
                responce_text = json.loads(response.text)
                if(responce_text['status'] == 'False'):
                    messages.error(request,'Client not logined')
                    return redirect('dashboard')

                try:
                    Title = request.POST['Title']
                    Description = request.POST['Description']
                    ProjectMainCategory = request.POST['ProjectMainCategory']
                    MainCategoryOptionTextarea = request.POST['MainCategoryOptionTextarea']
                    ProjectImage = request.FILES['ProjectImage']
                except:
                    messages.error(request,'Invalid data sent')
                    return redirect('dashboard')

                ProjectMainCategory = ProjectMainCategory.lower()
                MainCategoryOptionTextarea = MainCategoryOptionTextarea.lower()

                if(len(Title) < 10 or len(Title) > 150):
                    messages.error(request,'Title length must be between 10 to 150 character')
                    return redirect('dashboard')

                if(len(Description) < 50 or len(Description) > 30000):
                    messages.error(request,'Description length must be between 50 to 30K character')
                    return redirect('dashboard')

                if(ProjectMainCategory != ',cat_iot,' and ProjectMainCategory != ',cat_software,'):
                    messages.error(request,'Invalid Category select')
                    return redirect('dashboard')

                MainCategoryOptionTextarea = re.sub(re.compile(r'(,\s){2,}'), ',', MainCategoryOptionTextarea)
                MainCategoryOptionTextarea = re.sub('[^a-z_,]+', '', MainCategoryOptionTextarea)
                if(len(MainCategoryOptionTextarea) < 1):
                    messages.error(request,'Invalid Sub Category detect v.0.1')
                    return redirect('dashboard')

                if(ProjectMainCategory == ',cat_iot,'):
                    AllowedCategoryOption = [[',platform_arduino,',',platform_respberrypi,']]
                    if(isinstance(AllowedCategoryOption, list) !=True):
                        messages.error(request,'Something going wrong')
                        return redirect('dashboard')
                    else:
                        for WorlList in AllowedCategoryOption:
                            if(isinstance(WorlList, list) !=True):
                                messages.error(request,'Something going wrong')
                                return redirect('dashboard')

                    MainCategoryOptionTextareaAfterFilter = MainCategoryOptionTextarea
                    for WorlList in AllowedCategoryOption:
                        for word in WorlList:
                            if(word in MainCategoryOptionTextareaAfterFilter):
                                if(len(MainCategoryOptionTextareaAfterFilter) > len(word)):
                                    MainCategoryOptionTextareaAfterFilter =  MainCategoryOptionTextareaAfterFilter.replace(word,',')
                                else:
                                    MainCategoryOptionTextareaAfterFilter =  MainCategoryOptionTextareaAfterFilter.replace(word,'')

                    if(len(MainCategoryOptionTextareaAfterFilter) != 0):
                        messages.error(request,'Invalid Sub Category detect v.0.2')
                        return redirect('dashboard')

                    for WorlList in AllowedCategoryOption:
                        if(any(word in MainCategoryOptionTextarea for word in WorlList) != True):
                            messages.error(request,'Invalid Sub Category detect v.0.3')
                            return redirect('dashboard')
                elif(ProjectMainCategory == ',cat_software,'):
                    AllowedCategoryOption = [[',platform_arduino,',',platform_respberrypi,',',platform_android,',',platform_web,'],[',language_python,',',language_php,']]
                    if(isinstance(AllowedCategoryOption, list) !=True):
                        messages.error(request,'Something going wrong')
                        return redirect('dashboard')
                    else:
                        for WorlList in AllowedCategoryOption:
                            if(isinstance(WorlList, list) !=True):
                                messages.error(request,'Something going wrong')
                                return redirect('dashboard')

                    MainCategoryOptionTextareaAfterFilter = MainCategoryOptionTextarea
                    for WorlList in AllowedCategoryOption:
                        for word in WorlList:
                            if(word in MainCategoryOptionTextareaAfterFilter):
                                if(len(MainCategoryOptionTextareaAfterFilter) > len(word)):
                                    MainCategoryOptionTextareaAfterFilter =  MainCategoryOptionTextareaAfterFilter.replace(word,',')
                                else:
                                    MainCategoryOptionTextareaAfterFilter =  MainCategoryOptionTextareaAfterFilter.replace(word,'')
                    if(len(MainCategoryOptionTextareaAfterFilter) != 0):
                        messages.error(request,'Invalid Sub Category detect v.0.4')
                        return redirect('dashboard')

                    for WorlList in AllowedCategoryOption:
                        if(any(word in MainCategoryOptionTextarea for word in WorlList) != True):
                            messages.error(request,'Invalid Sub Category detect v.0.5')
                            return redirect('dashboard')
                else:
                    messages.error(request,'Invalid Category select')
                    return redirect('dashboard')

                project_category = ProjectMainCategory+MainCategoryOptionTextarea
                project_category = re.sub('[^a-z_,]+', '', project_category)
                project_category = project_category.split(',')
                project_category = AptListToString.AptListToString([item for item in project_category if item != ''],',',',')

                file_name, file_extension = os.path.splitext(ProjectImage.name)
                if(file_extension.lower() != '.jpeg' and file_extension.lower() != '.jpg' and file_extension.lower() != '.png'):
                    messages.error(request, 'only jpeg and png type is supported for profile image')
                    return redirect('dashboard')

                if not os.path.exists(AccountUrl):
                    messages.error(request, 'Somthing going wrong')
                    return redirect('dashboard')

                if os.path.exists(project_full_path):
                    messages.error(request, 'Somthing going wrong')
                    return redirect('dashboard')
                else:
                    os.makedirs(project_full_path)

                for i in range(0,1):
                    settings.MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),project_tmp_media)
                    fs = FileSystemStorage()
                    filename = fs.save(ProjectImage.name, ProjectImage)
                    uploaded_file_url = f'''{settings.MEDIA_ROOT}/{filename}'''
                    uploaded_file_url = uploaded_file_url.replace('\\','/');
                    filemime = mimetypes.MimeTypes().guess_type(uploaded_file_url)
                    if(filemime[0].lower() != 'image/jpeg' and filemime[0].lower() != 'image/png' and filemime[0].lower() != 'image/jpg'):
                        if os.path.exists(project_full_path):
                            shutil.rmtree(project_full_path)
                        messages.error(request, 'only jpeg and png type is supported for profile image')
                        return redirect('dashboard')
                    file_size_mb = (os.path.getsize(uploaded_file_url)/1024)/1024
                    if(file_size_mb > 3):
                        if os.path.exists(project_full_path):
                            shutil.rmtree(project_full_path)
                        messages.error(request, 'Project image size must be under 3mb')
                        return redirect('dashboard')
                    picture = Image.open(uploaded_file_url)
                    pictureRGB = picture.convert('RGB')
                    pictureRGB.save(f"{project_tmp_media}/{filename}")

                    file_name, file_extension = os.path.splitext(f"{project_tmp_media}/{filename}")
                    ProjectImage_id = ProjectImage_id+file_extension;

                    oldsize = os.stat(f"{project_tmp_media}/{filename}").st_size
                    picture = Image.open(f"{project_tmp_media}/{filename}")
                    dim = picture.size
                    ProjectImagePath = f'{project_full_path}/media/project_image/'
                    settings.MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),ProjectImagePath)
                    if not os.path.exists(ProjectImagePath):
                        os.makedirs(ProjectImagePath)
                    #set quality= to the preferred quality. 
                    #I found that 85 has no difference in my 6-10mb files and that 65 is the lowest reasonable number
                    picture.save(f'''{ProjectImagePath}/{ProjectImage_id}''',"JPEG",optimize=True,quality=70)
                    
                    newsize = os.stat(f"{ProjectImagePath}/{ProjectImage_id}").st_size
                    percent = (oldsize-newsize)/float(oldsize)*100

                    if os.path.exists(project_tmp_media):
                        shutil.rmtree(project_tmp_media)

                    project_image_array.append(ProjectImage_id)


                #Covert ProjectImage array to bytes to store in mysql
                project_image_bytes = pickle.dumps(project_image_array)

                # Database connection with mysql#
                conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
                #Creating a cursor object using the cursor() method
                connCursor = conn.cursor(buffered=True)
                
                EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'

                sql = f"SELECT * FROM project_upload WHERE project_id = (AES_ENCRYPT(%s,'{EPASS}'))"
                connCursor.execute(sql, (project_id,))
                conn.commit()
                if(connCursor.rowcount > 0):
                    if os.path.exists(project_full_path):
                        shutil.rmtree(project_full_path)
                    messages.error(request, 'Something going wrong')
                    return redirect('dashboard')
            
                else:
                    sql = f"INSERT INTO project_upload (status, project_id, account_id, title, description,project_category, project_image, create_time, last_upd_time) VALUES (AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'), AES_ENCRYPT(%s,'{EPASS}'))"
                    val = ('tmpactive',project_id,LAID,Title,Description,project_category,project_image_bytes,current_time,current_time)
                    connCursor.execute(sql, val)
                    conn.commit()
                    if(connCursor.rowcount >= 1):
                        messages.success(request, 'Project submited successfully')
                        return redirect('dashboard')
                    else:
                        if os.path.exists(project_full_path):
                            shutil.rmtree(project_full_path)
                        messages.error(request, 'Something going wrong')
                        return redirect('dashboard')
            except:
                if os.path.exists(project_full_path):
                    shutil.rmtree(project_full_path)
                messages.error(request, 'Something going wrong')
                return redirect('dashboard')
        else:
            domain_name = dev_setting.dev_domain_name_with_protocol
            context = {
                'login_status_server_response': login_status_server_response,
                'is_login_status_server':login_status_server.is_login_status_server,
                'domain_name':domain_name
            }
            return render(request,'accounts/dashboard.html',context)
    else:
        messages.info(request, 'Client not login')
        return redirect('dashboard')