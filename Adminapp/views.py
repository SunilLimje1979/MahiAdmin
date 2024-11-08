from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import json
import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import os
from time import time

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
    
    subscribe_res = requests.post("http://13.233.211.102/masters/api/subscription_history/", json={"doctor_id":id})
    #print(subscribe_res.text)

    if(subscribe_res.json().get('message_code')==1000 or subscribe_res.json().get('message_code')==1001):
        subscription = subscribe_res.json().get('message_data')
        print(subscription)
    
    else:
        subscription=0


        
    return render(request,'main/doctorDetails.html',{'doctor_data':doctor_data,'clinic_data':clinic_data,'stats':stats,'users':users,'subscription':subscription})


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

def extend_trial(request):
    # Get doctor_id from request (assuming it's passed as a GET or POST parameter)
    doctor_id = request.GET.get('doctor_id') or request.POST.get('doctor_id')
    print(doctor_id)

    sub_url="http://13.233.211.102/masters/api/extend_doctor_subscription/"
    api_data={
                "doctor_id": doctor_id,
                "master_subscription_id": 2, #for 30 days
                "subscription_price": 0,
                "subscription_tax1": 0,
                "subscription_tax2": 0,
                "subscription_amount": 0,
                "subscription_paid_amount": 0,
                "subscription_discount_amount": 0,
                "subscription_discount_type": 1,
                "subscription_promo_code": "PROMO345",
                "subscription_type": 3,
            }
    res=requests.post(sub_url,json=api_data)
    print(res.text)
    
    if (res.json().get('message_code')==1000):
        return JsonResponse({'success': True, 'message': 'Trial period successfully extended by 30 days.'})

    else:
        return JsonResponse({'success': False, 'message': 'Unable to Extend Try again or contact support'})
    

    #return JsonResponse({'success': True, 'message': 'Trial period successfully extended by 30 days.'})


@csrf_exempt
def paid_subscription(request):
    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        subscription_amount = request.POST.get("subscription_amount")
        subscription_billing_name = request.POST.get("subscription_billing_name")
        print(request.POST)
        response_data = {"success": False, "message": "An error occurred."}
        sub_url="http://13.233.211.102/masters/api/extend_doctor_subscription/"
        api_data={
                    "doctor_id": doctor_id,
                    "master_subscription_id": 5, #for 1 year 
                    "subscription_price": 0,
                    "subscription_tax1": 0,
                    "subscription_tax2": 0,
                    "subscription_amount": 0,
                    "subscription_paid_amount": subscription_amount,
                    "subscription_billing_name": subscription_billing_name,
                    "subscription_discount_amount": 0,
                    "subscription_discount_type": 1,
                    "subscription_promo_code": "PROMO345",
                    "subscription_type": 3,
                }
        res=requests.post(sub_url,json=api_data)
        print(res.text)
        
        if(res.json().get('message_code')==1000):
            response_data["success"] = True
            response_data["message"] = "Subscription extended successfully."
        
        else:
            response_data["success"] = False
            response_data["message"] = "Error Occured Please try again or contact support"


        return JsonResponse(response_data)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)



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


################## Deals ##########################
def AddDeals(request):
    if(request.user.is_authenticated):
        if(request.method=='GET'):
            category_res = requests.post('http://13.233.211.102/masters/api/get_deal_categories/')
            print(category_res.text)
            if(category_res.json().get('message_code')==1000):
                categories = category_res.json().get('message_data')
            else:
                categories=[]

            return render(request,'deals/Addandupdatedeals.html',{'categories':categories})
        
        else:
            print(request.POST)
            visible_to = request.POST.getlist('options[]')
            deal_category_ids = request.POST.getlist('categories[]')
            deal_mobile_image = request.FILES.get('DealContentImageMobile')
            deal_web_image = request.FILES.get('DealContentImageWeb')
            print(deal_mobile_image,deal_web_image)
            print(visible_to)
            print(deal_category_ids)

            deal_data = {
                    "CompanyName":request.POST.get('CompanyName'),
                    "DealOwnerMobileNo":request.POST.get('DealOwnerMobileNo'),
                    "DealOwnerPersonName":request.POST.get('DealOwnerPersonName'),
                    "DealMedicalNonMedical":int(request.POST.get('DealMedicalNonMedical')),
                    "DealTitle": request.POST.get('DealTitle'),
                    "DealKeywords":request.POST.get('DealKeywords'),
                    "DealWebsiteURL": request.POST.get('DealWebsiteURL'),
                }
            
            if('1' not in visible_to): #1 means doctor
                deal_data['Show_to_Doctor']= 0 #dont show to doctor app
            
            if('2' not in visible_to): #2 means pharmacy
                deal_data['Show_to_Pharmacy']= 0 #dont show to pharmacy app
            
            if('3' not in visible_to): #3 means laboratory
                deal_data['Show_to_Labs']= 0 #dont show to laboratory app
            
            if(deal_mobile_image):
                deal_data['DealContentURL_forMobile'] = deal_mobile_image.name
            
            if(deal_web_image):
                deal_data['DealContentURL_forWeb'] = deal_web_image.name
            
            print(deal_data)

            publish_data = {
                "PublishedOn": request.POST.get('PublishStartDate'),
                "ExpiryOn": request.POST.get('PublishEndDate')
            }

            print(publish_data)

            deal_res = requests.post('http://13.233.211.102/masters/api/insert_deal_and_publish_details/',json={'deal':deal_data,'publish':publish_data})
            print(deal_res.text)
            if(deal_res.json().get('message_code')==1000):
                response_data = deal_res.json().get('message_data')
                print(response_data)
            
                # Check which image was uploaded
                if deal_mobile_image:
                    print("Mobile URL image uploaded")
                    # Path to save the image (directly specifying the path)
                    img_directory = 'staticfiles/assets/Deal_images'
                    
                    # Ensure the directory exists
                    os.makedirs(img_directory, exist_ok=True)

                    # Rename the file with the user_id and keep the original extension
                    new_file_name = response_data.get('mobile_url')
                    print(new_file_name)
                    # Saving the image with its renamed name
                    img_path = os.path.join(img_directory, new_file_name)
                    with open(img_path, 'wb+') as destination:
                        for chunk in deal_mobile_image.chunks():
                            destination.write(chunk)

                    print('mobileimage uploaded successfully')
                    # Handle the mobile image upload here
                if deal_web_image:
                    print("Web URL image uploaded")
                    # Path to save the image (directly specifying the path)
                    img_directory = 'staticfiles/assets/Deal_images'
                    
                    # Ensure the directory exists
                    os.makedirs(img_directory, exist_ok=True)

                    # Rename the file with the user_id and keep the original extension
                    new_file_name = response_data.get('web_url')
                    print(new_file_name)
                    # Saving the image with its renamed name
                    img_path = os.path.join(img_directory, new_file_name)
                    with open(img_path, 'wb+') as destination:
                        for chunk in deal_web_image.chunks():
                            destination.write(chunk)

                    print('webimage uploaded successfully')
                    # Handle the web image upload here
                
                category_res = requests.post('http://13.233.211.102/masters/api/insert_deal_category_links/',json={"deal_id":response_data.get('deal_id'),"publish_id":response_data.get('publish_id'),"deal_category_ids":deal_category_ids})
                print(category_res.text)
                messages.success(request,"Deal Details Added successfully..")

            else:
                messages.error(request,"Deal Details Not Added Please try again or contact Support Team..")
            
            return redirect(AddDeals)
                
    else:
        return redirect(Login)
    


def ShowAllDeals(request):
    if(request.user.is_authenticated):
        res = requests.get('http://13.233.211.102/masters/api/get_active_deals/')
        print(res.text)
        if(res.json().get('message_code')==1000):
            allDeal = res.json().get('message_data')
            
        
        else:
            allDeal = []

        return render(request,'deals/alldeal.html',{'allDeal':allDeal})
    
    else:
        return redirect(Login)


def get_deal_details(request,id):
    if(request.user.is_authenticated):
        print(id)
        res = requests.post('http://13.233.211.102/masters/api/get_deal_details_by_deal_id/',json={ "deal_id":id})
        print(res.text)
        if(res.json().get('message_code')==1000):
            deal_data = res.json().get('message_data')
            category_res = requests.post('http://13.233.211.102/masters/api/get_deal_categories/')
            print(category_res.text)
            if(category_res.json().get('message_code')==1000):
                categories = category_res.json().get('message_data')
            else:
                categories=[]
        
        else:
            deal_data = []

        return render(request,'deals/deal_details.html',{'deal_data':deal_data,'categories':categories,"timestamp":int(time())})
    
    else:
        return redirect(Login)
    

@csrf_exempt
def update_deal(request):
    if request.method == 'POST':
        try:
            visible_to = request.POST.getlist('options[]')
            deal_category_ids = request.POST.getlist('categories[]')
            print(request.POST)
            deal_data = {
                "Deal_id" : request.POST.get('Deal_id'),
                "CompanyName":request.POST.get('CompanyName'),
                "DealOwnerMobileNo":request.POST.get('DealOwnerMobileNo'),
                "DealOwnerPersonName":request.POST.get('DealOwnerPersonName'),
                "DealMedicalNonMedical":int(request.POST.get('DealMedicalNonMedical')),
                "DealTitle": request.POST.get('DealTitle'),
                "DealKeywords":request.POST.get('DealKeywords'),
                "DealWebsiteURL": request.POST.get('DealWebsiteURL'),
                "Show_to_Doctor": 1 if '1' in visible_to else 0,
                "Show_to_Pharmacy": 1 if '2' in visible_to else 0,
                "Show_to_Labs": 1 if '3' in visible_to else 0,
            }
            # Path to save the image
            img_directory = 'staticfiles/assets/Deal_images' 
            os.makedirs(img_directory, exist_ok=True)  # Ensure the directory exists
            
            # Handle mobile image upload
            if 'DealContentImageMobile' in request.FILES:
                mobile_image = request.FILES['DealContentImageMobile']
                mobile_image_name = request.POST.get('mobileimagename')
                print(mobile_image_name)
                # Use existing image name if present, otherwise generate new name
                if mobile_image_name == None:
                    new_mobile_file_name = mobile_image_name
                    print("589",new_mobile_file_name)
                else:
                    deal_id = request.POST.get('Deal_id')  # Assuming deal_id is passed in POST data
                    extension = os.path.splitext(mobile_image.name)[1]
                    new_mobile_file_name = f"{deal_id}_M{extension}"
                    deal_data['DealContentURL_forMobile']=new_mobile_file_name
                    print("594",new_mobile_file_name)
                # Full path for the mobile image
                mobile_img_path = os.path.join(img_directory, new_mobile_file_name)
                
                # Save mobile image
                with open(mobile_img_path, 'wb+') as destination:
                    for chunk in mobile_image.chunks():
                        destination.write(chunk)
                
                print(f"Mobile image saved at: {mobile_img_path}")

            # Handle web image upload
            if 'DealContentImageWeb' in request.FILES:
                web_image = request.FILES['DealContentImageWeb']
                web_image_name = request.POST.get('webimagename')
                print("623",web_image_name)
                
                # Use existing image name if present, otherwise generate new name
                if web_image_name== None:
                    new_web_file_name = web_image_name
                else:
                    deal_id = request.POST.get('Deal_id')  # Assuming deal_id is passed in POST data
                    extension = os.path.splitext(web_image.name)[1]
                    new_web_file_name = f"{deal_id}_W{extension}"
                    deal_data['DealContentURL_forWeb']=new_web_file_name
                    print(new_web_file_name)
                
                # Full path for the web image
                web_img_path = os.path.join(img_directory, new_web_file_name)
                
                # Save web image
                with open(web_img_path, 'wb+') as destination:
                    for chunk in web_image.chunks():
                        destination.write(chunk)
                
                print(f"Web image saved at: {web_img_path}")
                
    
            
            print(deal_data)

            update_res = requests.post('http://13.233.211.102/masters/api/update_deal/',json=deal_data)
            print(update_res.text)
            # Return success response
            category_res = requests.post('http://13.233.211.102/masters/api/insert_deal_category_links/',json={"deal_id":request.POST.get('Deal_id'),"publish_id":request.POST.get('Publish_id'),"deal_category_ids":deal_category_ids})
            print(category_res.text)
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def republish_deal(request):
    if request.method == 'POST':
        deal_id = request.POST.get('deal_id')
        republish_on = request.POST.get('republish_on')
        republish_end_on = request.POST.get('republish_end_on')
        print(request.POST)
        # Parse dates
        republish_on_date = datetime.datetime.strptime(republish_on, '%Y-%m-%d').date()
        republish_end_on_date = datetime.datetime.strptime(republish_end_on, '%Y-%m-%d').date()
        publish_data ={
            'Deal_id':deal_id,
            'PublishedOn':republish_on,
            'ExpiryOn':republish_end_on
        }

        remaining_days = (republish_end_on_date - datetime.datetime.today().date()).days
        res = requests.post('http://13.233.211.102/masters/api/insert_publish_details/',json={'publish':publish_data})
        print(res.text)
        return JsonResponse({
            'success': True,
            'new_publish_date': republish_on,
            'new_expiry_date': republish_end_on,
            'remaining_days': remaining_days
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

    
def filter_deal(request):
    if request.method == 'GET':
        #city = request.GET.get('city')
        company_name = request.GET.get('companyname')
        #start_date = request.GET.get('start_date')
        #end_date = request.GET.get('end_date')
        visibleoptions = request.GET.get('visibleoptions')
        if visibleoptions:
            visible_options_str = ','.join(visibleoptions)  # Joins the list into "1,3"
        else:
            visible_options_str = ""
        status = request.GET.get('status')
        print(status,"692")
        print(visibleoptions,"693")
        print(company_name,"694")
        #print(start_date,'start_date')
        #print(end_date,'end_date')
        data=[]
        res=requests.post("http://13.233.211.102/masters/api/filter_deals/",json={"companyname": company_name,"status":status,"visibleoptions":visible_options_str})
        print(res.text)
        data=res.json().get('message_data',[])
        print(data)
        return JsonResponse({'deals': data})

    return JsonResponse({'error': 'Invalid request'}, status=400)