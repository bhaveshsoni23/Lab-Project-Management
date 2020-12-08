from django.urls import path
from django.conf import settings
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.login_status_client),
    
]