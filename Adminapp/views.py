from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import json
import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def hello(request):
    return HttpResponse("Hello Admin...")


def Login(request):
    if( not request.user.is_authenticated):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            print(username, password)

            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.error(request, "Invalid username or password")
                return redirect(Login)

            else:
                login(request,user)
                return redirect(index)
            
        else:
            return render(request ,'login.html')
            
    else:     
        return redirect(index)


def index(request):
    if(request.user.is_authenticated):
        return render(request, 'index.html', context={})
    
    else:
        return redirect(Login)



def base(request):
    if(request.user.is_authenticated):
        return render(request, 'base.html', context={})
    
    else:
        return redirect(Login)

def Logout(request):
    logout(request)
    messages.success(request, "You have successfully signed out")
    return redirect(Login)



def allRegistered(request):
    if(request.user.is_authenticated):
        url="http://13.233.211.102/doctor/api/fetch_doctors/"
        res=requests.post(url)
        # print(res.text)
        if(res.json().get('message_code')==1000):
            all_doctors=res.json().get('message_data')
            print(all_doctors)
            city_response = requests.post("http://13.233.211.102/masters/api/get_cities_by_state_id/",json={"state_id":22})
            cities = (city_response.json().get("message_data", [])).get('cities',[])
            #print(cities)
            # return render(request,'main/allRegistered.html',{'all_doctors':all_doctors})
            return render(request,'main/demo.html',{'all_doctors':all_doctors,"cities": cities})
    
    else:
        return redirect(Login)

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

@csrf_exempt
def reset_doctorpassword(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.'
    }
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doctor_id = data.get('doctor_id')
            new_password = data.get('new_password')
            print(doctor_id,new_password)
            
            #Call the external API to reset the password
            api_response = requests.post('http://13.233.211.102/medicalrecord/api/reset_doctor_password/', json={
                'doctor_id': doctor_id,
                'new_password': new_password
            })

            print(api_response.text)
            #Parse the API response
            api_data = api_response.json()
            
            if api_data['message_code'] == 1000:
                response_data['message_code'] = 1000
                response_data['message_text'] = 'Password reset successfully.'
            else:
                response_data['message_text'] = api_data.get('message_text', 'Unknown error.')
        
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)



def allcrmuser(request):
    if(request.user.is_authenticated):
        api_url_users = "http://13.233.211.102/masters/api/get_all_Authusers/"
        allusers = []
        response_users = requests.post(api_url_users)
        response_data_users = response_users.json()
        allusers = response_data_users.get('message_data', [])
        print(allusers)
        return render(request,'crm/crmusers.html',{'allusers':allusers})
    
    else:
        return redirect(Login)


def get_crmuser_details(request,id):
    print(id)
    res = requests.post('http://13.233.211.102/masters/api/get_crmuser_details/',json={'lead_by_id':id})
    if(res.json().get('message_code')==1000):
        data = res.json().get('message_data')
        print(data)
    else:
        data=res.json().get('message_data')
        print(data)
    return render(request,'crm/crmuserdetail.html',{'data':data})


##########################Pharmacist############################

def allpharmacist(request):
    if(request.user.is_authenticated):
        res=requests.get('http://13.233.211.102/medicalrecord/api/allPharmacist/')
        print(res.text)
        if(res.json().get('message_code')==1000):
            all_pharmacies = res.json().get('message_data')
        
        else:
            all_pharmacies = []

        return render(request,'pharmacy/allPharmacist.html',{'all_pharmacies':all_pharmacies})
 
    else:
        return redirect(Login)
    

def get_pharmacy_details(request,id):
    print(id)
    pharmacy_res = requests.post('http://13.233.211.102/medicalrecord/api/get_pharmacist_by_id/',json={'pharmacist_id':id})
    print(pharmacy_res.text)
    if(pharmacy_res.json().get('message_code')==1000):
        pharmacy_data = pharmacy_res.json().get('message_data')
    
    else:
        pharmacy_data=[]

    stats_res = requests.post('http://13.233.211.102/medicalrecord/api/get_pharmacist_stats/',json={'pharmacist_id':id})
    #print(stats_res.text)

    if(stats_res.json().get('message_code')==1000):
        stats = stats_res.json().get('message_data')
    
    else:
        stats=[]

    doctor_res = requests.post('http://13.233.211.102/medicalrecord/api/get_pharmacist_doctor_bypharmacistid/',json={'pharmacist_id':id})
    print(doctor_res.text)

    if(doctor_res.json().get('message_code')==1000):
        doctors = doctor_res.json().get('message_data')
    
    else:
        doctors=[]

    return render(request,'pharmacy/pharmacy.html',{'pharmacy_data':pharmacy_data,'stats':stats,'doctors':doctors})


@csrf_exempt
def reset_pharmacistpassword(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.'
    }
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pharmacist_id = data.get('pharmacist_id')
            new_password = data.get('new_password')
            print(pharmacist_id,new_password)
            
            #Call the external API to reset the password
            api_response = requests.post('http://13.233.211.102/medicalrecord/api/reset_pharmacist_password/', json={
                'pharmacist_id': pharmacist_id,
                'new_password': new_password
            })

            print(api_response.text)
            #Parse the API response
            api_data = api_response.json()
            
            if api_data['message_code'] == 1000:
                response_data['message_code'] = 1000
                response_data['message_text'] = 'Password reset successfully.'
            else:
                response_data['message_text'] = api_data.get('message_text', 'Unknown error.')
        
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)


def filter_pharamcist(request):
    if request.method == 'GET':
        #city = request.GET.get('city')
        doctor_name = request.GET.get('doctorname')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(doctor_name)
        print(start_date,'start_date')
        print(end_date,'end_date')
        data=[]
        res=requests.post("http://13.233.211.102/medicalrecord/api/fillter_pharmacists/",json={"doctor_name": doctor_name,"start_date":start_date,"end_date":end_date})
        print(res.text)
        data=res.json().get('message_data',[])
        print(data)
        return JsonResponse({'pharmacies': data})

    return JsonResponse({'error': 'Invalid request'}, status=400)

    



##########################Laboratory############################

def allLaboratory(request):
    if(request.user.is_authenticated):
        res=requests.get('http://13.233.211.102/medicalrecord/api/allLaboratory/')
        print(res.text)
        if(res.json().get('message_code')==1000):
            all_laboratory = res.json().get('message_data')
        
        else:
            all_laboratory = []

        return render(request,'laboratory/allLaboratory.html',{'all_laboratory':all_laboratory})
 
    else:
        return redirect(Login)
    

def get_laboratory_details(request,id):
    print(id)
    laboratory_res = requests.post('http://13.233.211.102/medicalrecord/api/get_laboratory_by_id/',json={'laboratory_id':id})
    print(laboratory_res.text)
    if(laboratory_res.json().get('message_code')==1000):
        laboratory_data = laboratory_res.json().get('message_data')
    
    else:
        laboratory_data=[]

    stats_res = requests.post('http://13.233.211.102/medicalrecord/api/get_laboratory_stats/',json={'laboratory_id':id})
    #print(stats_res.text)

    if(stats_res.json().get('message_code')==1000):
        stats = stats_res.json().get('message_data')
    
    else:
        stats=[]

    doctor_res = requests.post('http://13.233.211.102/medicalrecord/api/get_laboratory_doctor_bylaboratoryid/',json={'laboratory_id':id})
    print(doctor_res.text)

    if(doctor_res.json().get('message_code')==1000):
        doctors = doctor_res.json().get('message_data')
    
    else:
        doctors=[]

    return render(request,'laboratory/laboratory.html',{'laboratory_data':laboratory_data,'stats':stats,'doctors':doctors})


@csrf_exempt
def reset_laboratorypassword(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.'
    }
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            laboratory_id = data.get('laboratory_id')
            new_password = data.get('new_password')
            print(laboratory_id,new_password)
            
            #Call the external API to reset the password
            api_response = requests.post('http://13.233.211.102/medicalrecord/api/reset_laboratory_password/', json={
                'laboratory_id': laboratory_id,
                'new_password': new_password
            })

            print(api_response.text)
            #Parse the API response
            api_data = api_response.json()
            
            if api_data['message_code'] == 1000:
                response_data['message_code'] = 1000
                response_data['message_text'] = 'Password reset successfully.'
            else:
                response_data['message_text'] = api_data.get('message_text', 'Unknown error.')
        
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)



def filter_laboratory(request):
    if request.method == 'GET':
        #city = request.GET.get('city')
        doctor_name = request.GET.get('doctorname')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print(doctor_name)
        print(start_date,'start_date')
        print(end_date,'end_date')
        data=[]
        res=requests.post("http://13.233.211.102/medicalrecord/api/fillter_laboratories/",json={"doctor_name": doctor_name,"start_date":start_date,"end_date":end_date})
        data=res.json().get('message_data',[])
        print(data)
        return JsonResponse({'labs': data})

    return JsonResponse({'error': 'Invalid request'}, status=400)
    