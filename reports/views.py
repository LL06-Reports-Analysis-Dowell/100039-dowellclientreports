from django.shortcuts import render, redirect
from django.http import JsonResponse
import pymongo
from bson.objectid import ObjectId
from functools import wraps
from base64 import b64encode
from dateutil.parser import parse
import datetime
connect_string = 'mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/client_report'
client = pymongo.MongoClient(connect_string)
db = client["client_report"]
client_scans = db["client_scans"]
chunks = db["fs.chunks"]
files = db["fs.files"]

def custom_login_required(f):
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect("users:login")
        return f(request, *args, **kwargs)

    return wrap


@custom_login_required
def client_profile(request):
    user_qr = request.session["user_qr"]
    qr_image = chunks.find_one({"files_id": ObjectId(user_qr)})
    client_info = files.find_one({"_id": ObjectId(user_qr)})
    image = b64encode(qr_image["data"]).decode("utf-8")

    if request.is_ajax():
        client_report_filter = {"brand_aware":0,"purchase_choice":0,"brand_loyalty":0,"nps":0,"scan_no":0,"incomplete_responses":0,"completed_responses":0}

        dtr = request.POST.get("daterange", "")
        dtr = dtr.split("-")
        star_date = parse(dtr[0] + " 00:00:59")
        end_date = parse(dtr[1] + " 23:59:59")

        client_report_obj = client_scans.find({
            "qrcode_id": user_qr,
            "report_date": {"$gte": star_date, "$lte": end_date}
        })
        for row in client_report_obj:
            client_report_filter["brand_aware"] += int(row["brand_aware"])
            client_report_filter["purchase_choice"]+= int(row["purchase_choice"])
            client_report_filter["brand_loyalty"]+= int(row["brand_loyalty"])
            client_report_filter["nps"] += int(row["nps"])
            client_report_filter["scan_no"]+= int(row["scan_no"])
            client_report_filter["incomplete_responses"]+= int(row["incomplete_responses"])
            client_report_filter["completed_responses"]+= int(row["completed_responses"])
        context = {
            'brand_awareness': client_report_filter["brand_aware"],
            'purchase_choices': client_report_filter["purchase_choice"],
            'brand_loyalty': client_report_filter["brand_loyalty"],
            'net_promotor_score': client_report_filter["nps"],
            'qr_scans': client_report_filter["scan_no"],
            'incomplete_responses': client_report_filter["incomplete_responses"],
            'completed_responses': client_report_filter["completed_responses"],
        }
        return JsonResponse(context)

    else:
        client_report = {"brand_aware":0,"purchase_choice":0,"brand_loyalty":0,"nps":0,"scan_no":0,"incomplete_responses":0,"completed_responses":0}

        start_date = datetime.datetime.now() + datetime.timedelta(days=-7)
        end_date = datetime.datetime.now()
        client_report_obj = client_scans.find({
            "qrcode_id": user_qr,
            "report_date": {"$gte": start_date, "$lte": end_date}
        })
        for row in client_report_obj:
            client_report["brand_aware"] += int(row["brand_aware"])
            client_report["purchase_choice"] += int(row["purchase_choice"])
            client_report["brand_loyalty"] += int(row["brand_loyalty"])
            client_report["nps"] += int(row["nps"])
            client_report["scan_no"] += int(row["scan_no"])
            client_report["incomplete_responses"] += int(row["incomplete_responses"])
            client_report["completed_responses"] += int(row["completed_responses"])
        context = {
            'page_title': "Client Report",
            'qr_image': image,
            'client_name': client_info["client_name"],
            'plan_start_date': client_info["start_date"],
            'plan_type': client_info["plan_type"],
            'brand_awareness': client_report["brand_aware"],
            'purchase_choices': client_report["purchase_choice"],
            'brand_loyalty': client_report["brand_loyalty"],
            'net_promotor_score':client_report["nps"],
            'qr_scans': client_report["scan_no"],
            'incomplete_responses': client_report["incomplete_responses"],
            'completed_responses': client_report["completed_responses"],
            'week_startdate': start_date,
            'week_enddate': end_date
        }
    return render(request, "reports/client_profile.html", context)

@custom_login_required
def get_charts(request):
    report_date = []
    brand_aware = []
    purchase_choice = []
    brand_loyalty = []
    nps = []
    scan_no = []
    incomplete_responses =  []
    completed_responses = []

    user_qr = request.session["user_qr"]
    if request.is_ajax():
        sel_val =request.POST.get("sel_val", "")
        if not sel_val:
            sel_val =1;
        sel_val = int(sel_val)
        if sel_val == 1:
            start_date = datetime.datetime.now() + datetime.timedelta(days=-30)
            end_date = datetime.datetime.now()
            client_report_obj = client_scans.find({
                "qrcode_id": user_qr,
                "report_date": {"$gte": start_date, "$lte": end_date}
            }).sort('report_date', -1)
            for row in client_report_obj:
                report_date.append(str(row["report_date"].strftime("%d %b, %Y")))
                brand_aware.append(row["brand_aware"])
                purchase_choice.append(row["purchase_choice"])
                brand_loyalty.append(row["brand_loyalty"])
                nps.append(row["nps"])
                scan_no.append(row["scan_no"])
                incomplete_responses.append(row["incomplete_responses"])
                completed_responses.append(row["completed_responses"])

            context = {
                "report_date": report_date,
                'brand_awareness': brand_aware,
                'purchase_choices': purchase_choice,
                'brand_loyalty': brand_loyalty,
                'net_promotor_score': nps,
                'qr_scans': scan_no,
                'incomplete_responses': incomplete_responses,
                'completed_responses': completed_responses,
                'title': "Daily Analysis Report"

            }
            return JsonResponse(context)
        elif sel_val == 2:
            filter_obj = client_scans.aggregate([
                {"$project": {
                    "brand_aware": "$brand_aware",
                    "purchase_choice": "$purchase_choice",
                    "brand_loyalty": "$brand_loyalty",
                    "nps": "$nps",
                    "scan_no": "$scan_no",
                    "incomplete_responses": "$incomplete_responses",
                    "completed_responses": "$completed_responses",
                    "week": {"$week": "$report_date"},
                    "year": {"$year": "$report_date"},
                }},
                {"$group": {
                    "_id": {"week": "$week", "year": "$year"},
                    "brand_aware": {"$sum": "$brand_aware"},
                    "purchase_choice": {"$sum": "$purchase_choice"},
                    "brand_loyalty": {"$sum": "$brand_loyalty"},
                    "nps": {"$sum": "$nps"},
                    "scan_no": {"$sum": "$scan_no"},
                    "incomplete_responses": {"$sum": "$incomplete_responses"},
                    "completed_responses": {"$sum": "$completed_responses"},
                }},
                {"$sort": {"week": -1, "year": -1}}
            ])
            for row in filter_obj:
                report_date.append(str(row['_id']['week'])+ " week of "+str(row['_id']['year']))
                brand_aware.append(row["brand_aware"])
                purchase_choice.append(row["purchase_choice"])
                brand_loyalty.append(row["brand_loyalty"])
                nps.append(row["nps"])
                scan_no.append(row["scan_no"])
                incomplete_responses.append(row["incomplete_responses"])
                completed_responses.append(row["completed_responses"])
            context = {
                "report_date": report_date,
                'brand_awareness': brand_aware,
                'purchase_choices': purchase_choice,
                'brand_loyalty': brand_loyalty,
                'net_promotor_score': nps,
                'qr_scans': scan_no,
                'incomplete_responses': incomplete_responses,
                'completed_responses': completed_responses,
                'title': "Weekly Analysis Report"
            }
            return JsonResponse(context)
        elif sel_val == 3:
            filter_obj = client_scans.aggregate([
                { "$project": {
                    "brand_aware": "$brand_aware",
                    "purchase_choice": "$purchase_choice",
                    "brand_loyalty": "$brand_loyalty",
                    "nps": "$nps",
                    "scan_no": "$scan_no",
                    "incomplete_responses": "$incomplete_responses",
                    "completed_responses": "$completed_responses",
                    "month": { "$month": "$report_date" },
                    "year": { "$year": "$report_date" },
                }},
                { "$group": {
                    "_id": {"month" : "$month" ,"year" : "$year" },
                    "brand_aware": { "$sum": "$brand_aware" },
                    "purchase_choice": { "$sum": "$purchase_choice" },
                    "brand_loyalty": { "$sum": "$brand_loyalty" },
                    "nps": { "$sum": "$nps" },
                    "scan_no": { "$sum": "$scan_no" },
                    "incomplete_responses": { "$sum": "$incomplete_responses" },
                    "completed_responses": { "$sum": "$completed_responses" },
                }},
                {"$sort": {"month": -1, "year": -1}}
            ])
            for row in filter_obj:
                report_date.append(str(row['_id']['month'])+ " month of "+str(row['_id']['year']))
                brand_aware.append(row["brand_aware"])
                purchase_choice.append(row["purchase_choice"])
                brand_loyalty.append(row["brand_loyalty"])
                nps.append(row["nps"])
                scan_no.append(row["scan_no"])
                incomplete_responses.append(row["incomplete_responses"])
                completed_responses.append(row["completed_responses"])
            context = {
                "report_date": report_date,
                'brand_awareness': brand_aware,
                'purchase_choices': purchase_choice,
                'brand_loyalty': brand_loyalty,
                'net_promotor_score': nps,
                'qr_scans': scan_no,
                'incomplete_responses': incomplete_responses,
                'completed_responses': completed_responses,
                'title': "Monthly Analysis Report"

            }
            return JsonResponse(context)
        elif sel_val == 4:
            filter_obj = client_scans.aggregate([
                { "$project": {
                    "brand_aware": "$brand_aware",
                    "purchase_choice": "$purchase_choice",
                    "brand_loyalty": "$brand_loyalty",
                    "nps": "$nps",
                    "scan_no": "$scan_no",
                    "incomplete_responses": "$incomplete_responses",
                    "completed_responses": "$completed_responses",
                    "year": { "$year": "$report_date" },
                }},
                { "$group": {
                    "_id": "$year",
                    "brand_aware": { "$sum": "$brand_aware" },
                    "purchase_choice": { "$sum": "$purchase_choice" },
                    "brand_loyalty": { "$sum": "$brand_loyalty" },
                    "nps": { "$sum": "$nps" },
                    "scan_no": { "$sum": "$scan_no" },
                    "incomplete_responses": { "$sum": "$incomplete_responses" },
                    "completed_responses": { "$sum": "$completed_responses" },
                }},
                {"$sort": {"year":-1}}
            ])
            for row in filter_obj:
                report_date.append(str(row['_id']))
                brand_aware.append(row["brand_aware"])
                purchase_choice.append(row["purchase_choice"])
                brand_loyalty.append(row["brand_loyalty"])
                nps.append(row["nps"])
                scan_no.append(row["scan_no"])
                incomplete_responses.append(row["incomplete_responses"])
                completed_responses.append(row["completed_responses"])
            context = {
                "report_date": report_date,
                'brand_awareness': brand_aware,
                'purchase_choices': purchase_choice,
                'brand_loyalty': brand_loyalty,
                'net_promotor_score': nps,
                'qr_scans': scan_no,
                'incomplete_responses': incomplete_responses,
                'completed_responses': completed_responses,
                'title': "Yearly Analysis Report"

            }
            return JsonResponse(context)

    else:

        start_date = datetime.datetime.now() + datetime.timedelta(days=-30)
        end_date = datetime.datetime.now()
        client_report_obj = client_scans.find({
            "qrcode_id": user_qr,
            "report_date": {"$gte": start_date, "$lte": end_date}
        }).sort('report_date',-1)
        for row in client_report_obj:
            report_date.append(str(row["report_date"].strftime("%d %b, %Y")))
            brand_aware.append(row["brand_aware"])
            purchase_choice.append(row["purchase_choice"])
            brand_loyalty.append(row["brand_loyalty"])
            nps.append(row["nps"])
            scan_no.append(row["scan_no"])
            incomplete_responses.append(row["incomplete_responses"])
            completed_responses.append(row["completed_responses"])


        context = {
            "report_date": report_date,
            'brand_awareness': brand_aware,
            'purchase_choices': purchase_choice,
            'brand_loyalty': brand_loyalty,
            'net_promotor_score': nps,
            'qr_scans': scan_no,
            'incomplete_responses': incomplete_responses,
            'completed_responses': completed_responses,

        }
        return render(request, "reports/daily_charts.html", context)
