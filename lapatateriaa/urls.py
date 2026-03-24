from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app_carta.views import test_s3

urlpatterns = [
    path('test-s3/', test_s3, name='test_s3'),
    path('admin/', admin.site.urls), # Tu panel técnico
    path('', include('app_carta.urls')), # La Landing Page interactiva (Punto de entrada)
    path('usuarios/', include('app_usuarios.urls')), # Login y Registro
    path('pedidos/', include('app_pedidos.urls')), # Carrito y Pedidos
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)