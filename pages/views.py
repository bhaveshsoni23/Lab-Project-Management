from django.shortcuts import render,redirect
from django.contrib import messages, auth
from django.http import HttpResponse
import bfa
from MyProject.static import login_status_server
from MyProject.static import dev_setting
from MyProject.static import project_showcase
import mysql.connector
import pickle
from AptLibrary.Python.Script import ConvertSecToTime
import time

def index(request):
    login_status_server_response = login_status_server.login_status_server(request)
    domain_name = dev_setting.dev_domain_name_with_protocol
    project_showcase_response = project_showcase.project_showcase(request,[','],{'limit':3})
    try:
        project = project_showcase_response['result']
    except:
        project = list()
    context = {
        'login_status_server_response': login_status_server_response,
        'is_login_status_server':login_status_server.is_login_status_server,
        'domain_name':domain_name,
        'project':project,
    }
    
    return render(request,'pages/index.html',context)

def about(request):
    login_status_server_response = login_status_server.login_status_server(request)
    domain_name = dev_setting.dev_domain_name_with_protocol
    context = {
        'login_status_server_response': login_status_server_response,
        'is_login_status_server':login_status_server.is_login_status_server,
        'domain_name':domain_name
    }

    return render(request,'pages/about.html',context)

def ContactUs(request):
    login_status_server_response = login_status_server.login_status_server(request)
    domain_name = dev_setting.dev_domain_name_with_protocol
    context = {
        'login_status_server_response': login_status_server_response,
        'is_login_status_server':login_status_server.is_login_status_server,
        'domain_name':domain_name
    }
    return render(request,'pages/ContactUs.html',context) 

def Content(request):
    if(request.GET.get('cat')):
        cat = request.GET['cat']
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    breadcrumb = ''
    cat_list = list()
    i = 0
    for item in cat.split("-"):
        cat_list.append(','+item+',')

        if len(item) > 0:
            tmp_breadcrumb = item.split("_")
            if(len(tmp_breadcrumb) > 1):
                if(i == 0):
                    breadcrumb += tmp_breadcrumb[1]
                else:
                    breadcrumb += ' / '+tmp_breadcrumb[1]
                i = i+1
    login_status_server_response = login_status_server.login_status_server(request)
    domain_name = dev_setting.dev_domain_name_with_protocol
    project_showcase_response = project_showcase.project_showcase(request,cat_list)
    try:
        project = project_showcase_response['result']
    except:
        project = list()
    context = {
        'login_status_server_response': login_status_server_response,
        'is_login_status_server':login_status_server.is_login_status_server,
        'domain_name':domain_name,
        'project':project,
        'breadcrumb':breadcrumb
    }
    return render(request,'pages/Content.html',context)

def ProjectShow(request):
    login_status_server_response = login_status_server.login_status_server(request)
    domain_name = dev_setting.dev_domain_name_with_protocol

    if(request.GET.get('pid')):
        pid = request.GET['pid']
    else:
        return redirect('index')

    # Database connection with mysql#
    conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
    #Creating a cursor object using the cursor() method
    connCursor = conn.cursor(buffered=True)

    EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'

    sql = f"SELECT AES_DECRYPT(project_id,'{EPASS}'),AES_DECRYPT(account_id,'{EPASS}'),AES_DECRYPT(title,'{EPASS}'),AES_DECRYPT(description,'{EPASS}'),AES_DECRYPT(project_category,'{EPASS}'),AES_DECRYPT(project_image,'{EPASS}'),AES_DECRYPT(last_upd_time,'{EPASS}') FROM project_upload WHERE project_id = AES_ENCRYPT(%s,'{EPASS}') and (status = AES_ENCRYPT(%s,'{EPASS}') or status = AES_ENCRYPT(%s,'{EPASS}'))"
    connCursor.execute(sql, (pid,'tmpactive','active'))
    conn.commit()

    if(connCursor.rowcount < 1):
        messages.error(request,"Something going wrong")
        return redirect('index')

    results = connCursor.fetchall()
    if(len(results) < 1):
        messages.error(request,"Something going wrong")
        return redirect('index')

    result = results[0]

    if(result[0] != None and len(result[0]) > 0):
        project_id = result[0]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(result[1] != None and len(result[1]) > 0):
        account_id = result[1]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(result[2] != None and len(result[2]) > 0):
        title = result[2]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(result[3] != None and len(result[3]) > 0):
        description = result[3]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(result[4] != None and len(result[4]) > 0):
        project_category = result[4]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(result[5] != None and len(result[5]) > 0):
        project_image = result[5]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')
    if(result[6] != None and len(result[6]) > 0):
        last_upd_time = result[6]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(isinstance(project_image, bytearray)):
        try:
            project_image_array = pickle.loads(project_image)
        except:
            messages.error(request,"Something going wrong")
            return redirect('index')
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(len(project_image_array) < 1):
        messages.error(request,"Something going wrong")
        return redirect('index')

    sql = f"SELECT AES_DECRYPT(fname,'{EPASS}'),AES_DECRYPT(lname,'{EPASS}'),AES_DECRYPT(profile_id,'{EPASS}') FROM register_account WHERE account_id = AES_ENCRYPT(%s,'{EPASS}') and (status = AES_ENCRYPT(%s,'{EPASS}') or status = AES_ENCRYPT(%s,'{EPASS}'))"
    connCursor.execute(sql, (account_id,'tmpactive','active'))
    conn.commit()

    if(connCursor.rowcount < 1):
        messages.error(request,"Something going wrong")
        return redirect('index')

    author_results = connCursor.fetchall()
    if(len(author_results) < 1):
        messages.error(request,"Something going wrong")
        return redirect('index')

    author_result = author_results[0]

    if(author_result[0] != None and len(author_result[0]) > 0):
        fname = author_result[0]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(author_result[1] != None and len(author_result[1]) > 0):
        lname = author_result[1]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    if(author_result[2] != None and len(author_result[2]) > 0):
        profile_id = author_result[2]
    else:
        messages.error(request,"Something going wrong")
        return redirect('index')

    last_upd_local_time = time.asctime( time.localtime(float(last_upd_time)))
    project = {'project_id':project_id,'account_id':account_id,'title':title,'description':description,'project_category':project_category,'project_image':project_image_array,'last_upd_time':last_upd_time,'last_upd_local_time':last_upd_local_time,'last_upd_sort_time':ConvertSecToTime.ConvertSecToSortTime(time.time() - float(last_upd_time)),'fname':fname,'lname':lname,'profile_id':profile_id}
    context = {
        'login_status_server_response': login_status_server_response,
        'is_login_status_server':login_status_server.is_login_status_server,
        'domain_name':domain_name,
        'project':project
    }
    return render(request,'pages/ProjectShow.html',context) 
