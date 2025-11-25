# penstore_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # APIs da nossa Loja (E-commerce):
    path('api/', include('loja.urls')), 
    
    # APIs do novo sistema de Fábrica (ERP):
    path('api/fabrica/', include('fabrica.urls')), 
]

# Adiciona as rotas de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)