from django.urls import path

from . import views

urlpatterns = [
    path('', views.index,name='index'),
    path('about', views.about,name='about'),
    path('ContactUs', views.ContactUs,name='ContactUs'),
    path('Content', views.Content,name='Content'),
    path('ProjectShow', views.ProjectShow,name='ProjectShow')

]