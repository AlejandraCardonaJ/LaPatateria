from django.urls import path
from . import views

app_name = 'carta'

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # Carta pública
    path('carta/', views.carta, name='carta'),
    
    # Descargar carta en PDF
    path('carta/pdf/', views.carta_pdf, name='carta_pdf'),
]
