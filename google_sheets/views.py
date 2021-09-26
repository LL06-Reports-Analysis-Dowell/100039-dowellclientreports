from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST)
from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.conf import settings
import os.path, json, pymongo
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import base64, os
from PIL import Image
from google_drive_downloader import GoogleDriveDownloader as gdd
class ReadSheet(APIView):
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'sheet_id': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'sheet_name': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'key_range': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'value_range': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'convert_logo': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    def post(self, request):
        try:

            sheet_id = request.data.get("sheet_id")
            sheet_name = request.data.get("sheet_name")
            key_range = request.data.get("key_range")
            value_range = request.data.get("value_range")
            convert_logo = request.data.get("convert_logo")

            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'keys.json')
            credentials = None
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

            # The ID and range of a sample spreadsheet.
            SAMPLE_SPREADSHEET_ID = sheet_id  # '1RHMPYyHhoi_4j9rdn-XMKFMAE6CLEfn0GE9Jc__7mhQ'
            VALUE_RANGE = sheet_name + '!' + value_range  # FormResponses1!A53:AE103'
            KEY_RANGE = sheet_name + '!' + key_range  # 'FormResponses1!A1:AE1'

            service = build('sheets', 'v4', credentials=credentials)
            # Call the Sheets API
            sheet = service.spreadsheets()
            keys = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                      range=KEY_RANGE).execute()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=VALUE_RANGE).execute()
            keys = keys.get('values', [])
            values = result.get('values', [])
            data = []
            for value in values:
                row = {}
                for i in range(len(keys[0])):
                    row[keys[0][i]] = value[i]
                data.append(row)

            if convert_logo == "Yes" or convert_logo == "yes":
                for data_row in data:
                    data_row['Logo'] = get_as_base64( data_row['Logo'])


            connect_string = 'mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/'
            client = pymongo.MongoClient(connect_string)
            db = client.sheet_data
            coll = db.records
            return Response({"Congrats. Records inserted successfully!"}, status=HTTP_200_OK)
        except Exception as e:
            return Response({"Failure! Please provide valid sheet_id, name or range."}, status=HTTP_400_BAD_REQUEST)

def get_as_base64(url):
    file_id = url.split("id=")
    file_id = file_id[1]
    dest_path = './data/image.jpg'
    dest_path1 = './data/image1.jpg'
    gdd.download_file_from_google_drive(file_id=file_id, dest_path= dest_path)
    im = Image.open(dest_path)
    im.save(dest_path1)
    with open(dest_path1, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    if os.path.isfile(dest_path):
        os.remove(dest_path)
        if os.path.isfile(dest_path1):
            os.remove(dest_path1)

    return encoded_string
