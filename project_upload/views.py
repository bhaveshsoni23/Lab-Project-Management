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
import requests
from AptLibrary.Python.Script import AptExtractHostName
from MyProject.static import dev_setting
import requests


@api_view(['POST'])
def project_upload(request):
	if request.method == 'POST':
		return JsonResponse({'status':'False'}, safe=False)