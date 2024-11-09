from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse


urlpatterns = [
    path('', include('exchange.urls')),  # Handles requests to the root URL
    path('api/v1/', include('exchange.urls')),
    path('admin/', admin.site.urls),
]
