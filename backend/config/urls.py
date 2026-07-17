from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/trips/', include('trips.urls')),
    path('admin/', admin.site.urls),
]
