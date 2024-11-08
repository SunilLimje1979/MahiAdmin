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
    path('reset_doctorpassword/',reset_doctorpassword,name='reset_doctorpassword'),
    path('extend_trial/',extend_trial,name='extend_trial'),
    path('paid_subscription/',paid_subscription,name='paid_subscription'),

    ###################CRM#################################
    path('allcrmuser/',allcrmuser,name='allcrmuser'),
    path('get_crmuser_details/<int:id>',get_crmuser_details,name='get_crmuser_details'),

    ###################Pharmacist#################################
    path('allpharmacist/',allpharmacist,name='allpharmacist'),
    path('get_pharmacy_details/<int:id>',get_pharmacy_details,name='get_pharmacy_details'),
    path('reset_pharmacistpassword/',reset_pharmacistpassword,name='reset_pharmacistpassword'),
    path('filter_pharamcist/',filter_pharamcist,name='filter_pharamcist'),

    ###################Pharmacist#################################
    path('allLaboratory/',allLaboratory,name='allLaboratory'),
    path('get_laboratory_details/<int:id>',get_laboratory_details,name='get_laboratory_details'),
    path('reset_laboratorypassword/',reset_laboratorypassword,name='reset_laboratorypassword'),
    path('filter_laboratory/',filter_laboratory,name='filter_laboratory'),


    #######################Deal########################
    path('AddDeals/',AddDeals,name='AddDeals'),
    path('ShowAllDeals/',ShowAllDeals,name='ShowAllDeals'),
    path('get_deal_details/<int:id>',get_deal_details,name='get_deal_details'),
    path('update_deal/',update_deal,name='update_deal'),
    path('republish_deal/',republish_deal,name='republish_deal'),
    path('filter_deal/',filter_deal,name='filter_deal'),
    

]
