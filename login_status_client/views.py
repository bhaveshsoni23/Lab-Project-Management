from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json
import pickle
import mysql.connector
import time
import pickle
from django.shortcuts import render,redirect

@api_view(['POST'])
def login_status_client(request):
	if request.method == 'POST':
		try:
			data = request.POST
			# Database connection with mysql#
			conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
			#Creating a cursor object using the cursor() method
			connCursor = conn.cursor(buffered=True)

			EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'

			if(request.POST.get('LID') and request.POST.get('LID') and request.POST.get('LID')):
				LID = request.POST['LID']
				LAID = request.POST['LAID']
				BFP = request.POST['BFP']
			else:
				return JsonResponse({'status':'False'}, safe=False)

			sql = f"SELECT AES_DECRYPT(login_data,'{EPASS}'),AES_DECRYPT(fname,'{EPASS}'),AES_DECRYPT(lname,'{EPASS}'),AES_DECRYPT(email,'{EPASS}'),AES_DECRYPT(profile_id,'{EPASS}') FROM register_account WHERE account_id = AES_ENCRYPT(%s,'{EPASS}')"
			connCursor.execute(sql, (LAID,))
			conn.commit()

			if(connCursor.rowcount != 1):
				return JsonResponse({'status':'False'}, safe=False)

			result = connCursor.fetchall()

			if(len(result) > 0 and len(result[0]) > 0 and result[0][1] != None and len(result[0][1]) > 0):
				fname = result[0][1]
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if(len(result) > 0 and len(result[0]) > 0 and result[0][2] != None and len(result[0][2]) > 0):
				lname = result[0][2]
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if(len(result) > 0 and len(result[0]) > 0 and result[0][3] != None and len(result[0][3]) > 0):
				email = result[0][3]
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if(len(result) > 0 and len(result[0]) > 0 and result[0][4] != None and len(result[0][4]) > 0):
				profile_id = result[0][4]
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if(len(result) > 0 and len(result[0]) > 0 and result[0][0] != None and len(result[0][0]) > 0 and isinstance(result[0][0], bytearray)):
				try:
					login_data_fetch = pickle.loads(result[0][0])
				except:
					return JsonResponse({'status':'False'}, safe=False)
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if "login_id" in login_data_fetch and len(login_data_fetch['login_id']) > 0 and isinstance(login_data_fetch['login_id'], list):
				login_id_fetch = login_data_fetch['login_id']
			else:
				return JsonResponse({'status':'False'}, safe=False)

			IsLoginVerify = False
			if(len(login_id_fetch) > 0):
				for item in login_id_fetch:
					if(item['id'] == LID and item['bfp'] == BFP):
						IsLoginVerify = True
						break
			else:
				return JsonResponse({'status':'False'}, safe=False)

			if(IsLoginVerify == True):
				return JsonResponse({'status':'True','fname':fname,'lname':lname,'email':email,'profile_id':profile_id,'account_id':LAID}, safe=False)
			else:
				return JsonResponse({'status':'False'}, safe=False)
		except:
			return JsonResponse({'status':'False'}, safe=False)