from django.urls import path
from .views import *
app_name = 'google_sheets'

urlpatterns = [
    path("read/sheet", ReadSheet.as_view(), name="read_sheet"),
]