from django.urls import path

from .views import TripHistoryView, TripPlanView

urlpatterns = [
    path('plan/', TripPlanView.as_view(), name='trip-plan'),
    path('history/', TripHistoryView.as_view(), name='trip-history'),
]