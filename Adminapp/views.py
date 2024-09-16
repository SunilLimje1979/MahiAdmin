from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import json
import datetime

# Create your views here.

def hello(request):
    return HttpResponse("Hello Admin...")


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass1']
        print(username, password)

        user = authenticate(request, username=username, password=password)
        print(user)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect(Login)

        else:
            login(request,user)
            # messages.success(request, "You have successfully signed in")
            return redirect(index)
        
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html', context={})
def base(request):
    return render(request, 'base.html', context={})

def Logout(request):
    logout(request)
    messages.success(request, "You have successfully signed out")
    return redirect(Login)



def allRegistered(request):
    url="http://13.233.211.102/doctor/api/fetch_doctors/"
    res=requests.post(url)
    # print(res.text)
    if(res.json().get('message_code')==1000):
        all_doctors=res.json().get('message_data')
        print(all_doctors)
        city_response = requests.post("http://13.233.211.102/masters/api/get_cities_by_state_id/",json={"state_id":22})
        cities = (city_response.json().get("message_data", [])).get('cities',[])
        print(cities)
        # return render(request,'main/allRegistered.html',{'all_doctors':all_doctors})
        return render(request,'main/demo.html',{'all_doctors':all_doctors,"cities": cities})

def get_doctor_details(request,id):
    print(id)

    api_url="http://13.233.211.102/doctor/api/get_doctor_by_id/"
    response=requests.post(api_url,json={'doctor_id':id})
    data=response.json().get("message_data",{})
    print(data)
    # Convert epoch timestamp to formatted date
    epoch_timestamp = data[0].get('doctor_dateofbirth', 0)
    formatted_date=datetime.datetime.fromtimestamp(epoch_timestamp).strftime( "%Y-%m-%d")
    created_on = data[0].get('createdon', 0)
    registered_date=datetime.datetime.fromtimestamp(created_on).strftime( "%d-%m-%Y")   
    print(registered_date)
    data[0]['doctor_dateofbirth'] = formatted_date
    data[0]['createdon'] = registered_date
    doctor_data=data[0]
    print(data)

    stat_res=requests.post("http://13.233.211.102/doctor/api/doctors_stats/",json={'doctor_id':id})
    print(stat_res.text)
    if(stat_res.json().get('message_code')==1000):
        stats=stat_res.json().get('message_data')
        print(stats)
        user_data = {"location_id":stats['location_id']}
        user_url = 'http://13.233.211.102/doctor/api/get_all_users_by_location/'
        user_response = requests.post(user_url,json=user_data)
        users=user_response.json().get('message_data', {})
        print(users)
        clinic_url="http://13.233.211.102/doctor/api/get_all_doctor_location/"
        response=requests.post(clinic_url,json={"doctor_location_id":stats['location_id']})
        clinic_data=(response.json().get("message_data",{}))[0]
        print(clinic_data)
    
    else:
        clinic_data=0
        users=0
        stats=0
        
    return render(request,'main/doctorDetails.html',{'doctor_data':doctor_data,'clinic_data':clinic_data,'stats':stats,'users':users})


def filter_doctors(request):
    if request.method == 'GET':
        city = request.GET.get('city')
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        print(city)
        print(start_date,'start_date')
        print(end_date,'end_date')
        data=[]
        res=requests.post("http://13.233.211.102/doctor/api/fillter_doctors/",json={"city_id": city,"start_date":start_date,"end_date":end_date})
        data=res.json().get('message_data',[])
        print(data)
        return JsonResponse({'doctors': data})

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
