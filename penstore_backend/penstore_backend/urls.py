from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('loja.urls')), 
    
    path('api/fabrica/', include('fabrica.urls')), 
]