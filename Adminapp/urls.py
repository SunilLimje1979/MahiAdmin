from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('hello/',hello,name='hello'),
    path('login/',Login,name='login'),
    path('base/',base,name='base'),
    path('index/',index,name='index'),
    path('Logout/',Logout,name='Logout'),
    path('allRegistered/',allRegistered,name='allRegistered'),
    path('get_doctor_details/<int:id>',get_doctor_details,name='get_doctor_details'),
    path('filter_doctors/',filter_doctors, name='filter_doctors'),

    ###################CRM#################################
    path('allcrmuser/',allcrmuser,name='allcrmuser'),
    path('get_crmuser_details/<int:id>',get_crmuser_details,name='get_crmuser_details'),
    
]
