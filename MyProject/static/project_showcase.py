from django.shortcuts import render,redirect
from django.contrib import messages
from MyProject import settings
from MyProject.static import login_status_server
import mysql.connector
import time
from django.conf import settings
import pickle
import mysql.connector
import time
import pickle
from django.shortcuts import render,redirect
from AptLibrary.Python.Script import ConvertSecToTime

def project_showcase(request,cname,data=list()):
	#try:
		# Database connection with mysql#
		conn = mysql.connector.connect(host='localhost',user='root',password='',database='main_database')
		#Creating a cursor object using the cursor() method
		connCursor = conn.cursor(buffered=True)

		EPASS='GFtCtuL7JdCJqmE3CgHBsN3GhPMwAV8pgu8bqKkR8Pg85L8XKJ4Mv2XtwkBvtLtr'

		sqlval = list()
		if(isinstance(cname, list)):
			strsql = ""
			i=0
			for item_cname in cname:
				if(i==0):
					strsql += f"CONVERT(AES_DECRYPT(project_category, '{EPASS}') USING latin1) LIKE %s"
				elif(i >  0):
					strsql += f" and CONVERT(AES_DECRYPT(project_category, '{EPASS}') USING latin1) LIKE %s"

				sqlval.append('%'+item_cname+'%')
				i += 1
		else:
			return {'status':'False','v':0.1}

		try:
			if(isinstance(data, dict)):
				if 'limit' in data.keys():
					if(data['limit'] > 0):
						limit = data['limit']
					else:
						limit = 6
				else:
					limit = 6
			else:
				limit = 6
		except:
			limit = 6


		sql = f"SELECT AES_DECRYPT(project_id,'{EPASS}'),AES_DECRYPT(account_id,'{EPASS}'),AES_DECRYPT(title,'{EPASS}'),AES_DECRYPT(description,'{EPASS}'),AES_DECRYPT(project_category,'{EPASS}'),AES_DECRYPT(project_image,'{EPASS}'),AES_DECRYPT(last_upd_time,'{EPASS}') FROM project_upload WHERE {strsql} and (status = AES_ENCRYPT(%s,'{EPASS}') or status = AES_ENCRYPT(%s,'{EPASS}')) ORDER BY AES_DECRYPT(last_upd_time, '{EPASS}') DESC LIMIT {limit}"
		sqlval.append('tmpactive')
		sqlval.append('active')
		sqlval = tuple(sqlval)
		connCursor.execute(sql, (sqlval))
		conn.commit()
		if(connCursor.rowcount < 1):
			return {'status':'False','v':1}

		results = connCursor.fetchall()
		if(len(results) < 1):
			return {'status':'False','v':2}

		result_array = list()
		for result in results:
			if(result[0] != None and len(result[0]) > 0):
			    project_id = result[0]
			else:
			   return {'status':'False','v':3}

			if(result[1] != None and len(result[1]) > 0):
			    account_id = result[1]
			else:
			    return {'status':'False','v':4}

			if(result[2] != None and len(result[2]) > 0):
			    title = result[2]
			else:
			   return {'status':'False','v':5}

			if(result[3] != None and len(result[3]) > 0):
			    description = result[3]
			else:
			   return {'status':'False','v':6}

			if(result[4] != None and len(result[4]) > 0):
			    project_category = result[4]
			else:
			   return {'status':'False','v':7}

			if(result[5] != None and len(result[5]) > 0):
			    project_image = result[5]
			else:
				return {'status':'False','v':8}
			if(result[6] != None and len(result[6]) > 0):
			    last_upd_time = result[6]
			else:
			   return {'status':'False','v':9}

			if(isinstance(project_image, bytearray)):
			    try:
			        project_image_array = pickle.loads(project_image)
			    except:
			        return {'status':'False','v':10}
			else:
				return {'status':'False','v':11}

			if(len(project_image_array) < 1):
				return {'status':'False','v':12}
			
			result_array.append({'project_id':project_id,'account_id':account_id,'title':title,'description':description,'project_category':project_category,'project_image':project_image_array,'last_upd_time':last_upd_time,'last_upd_sort_time':ConvertSecToTime.ConvertSecToSortTime(time.time() - float(last_upd_time))})
		return {'status':'True','result':result_array}
	# except:
	# 	return {'status':'False','v':0}