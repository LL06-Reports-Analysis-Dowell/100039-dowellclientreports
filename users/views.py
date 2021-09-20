from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import pymongo


connect_string = 'mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/client_report?retryWrites=true&w=majority'
client = pymongo.MongoClient(connect_string)
db = client["client_report"]
collection = db["client_login"]



def login(request):
    return render(request, "login/login.html")

def validate(request):
    username = request.POST["username"]
    password = request.POST["password"]
    coll = db.list_collection_names()
    user_credentials = collection.find_one({"client_id": username, "password":password})

    if user_credentials is None:

        messages.error(request, "Invalid details")
        return redirect("users:login")
    else:
        request.session['user'] = username
        request.session['user_qr'] = user_credentials["qrcode_id"]
        return redirect("reports:client_profile")

def logout(request):
    try:
        del request.session['user']
        del request.session['user_qr']
    except:
        return redirect('users:login')
    return redirect('users:login')


