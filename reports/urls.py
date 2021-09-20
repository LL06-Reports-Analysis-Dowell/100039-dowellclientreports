from django.urls import path
from . import views
app_name = 'reports'

urlpatterns = [
    path("reports/client_profile", views.client_profile, name="client_profile"),
    path("reports/daily_charts", views.get_charts, name="daily_charts"),

]