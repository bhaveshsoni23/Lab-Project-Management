
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from login_status_client import views





urlpatterns = [
    path('',include('pages.urls')),
    path('Account/',include('Account.urls')),
    path('project_upload/',include('project_upload.urls')),
     path('login_status_client/',include('login_status_client.urls')),
    path('admin/', admin.site.urls),
 
]+static(settings.MEDIA_URL,document_root =settings.MEDIA_ROOT)
