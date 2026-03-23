from django.db import models
from django.contrib.auth.models import AbstractUser

# Heredamos de AbstractUser para mantener todas las funciones de Django (login, contraseña, etc.)
# pero agregándole lo que necesita "La Patatería".
class Usuario(AbstractUser):
    
    # Definimos las opciones de roles para el sistema
    ROLES_CHOICES = (
        ('CLIENTE', 'Cliente'),
        ('DUENO', 'Dueño / Administrador'),
    )

    # --- CAMPOS PERSONALIZADOS ---
    
    # Campo para identificar el rol (Por defecto todos son Clientes)
    rol = models.CharField(
        max_length=10, 
        choices=ROLES_CHOICES, 
        default='CLIENTE',
        verbose_name="Rol del Usuario"
    )

    # Teléfono para contacto en domicilios
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name="Teléfono de contacto"
    )

    # Fecha de nacimiento necesaria para la estrategia "Papa Cumpleañera"
    fecha_nacimiento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Fecha de Nacimiento"
    )

    # Sistema de puntos acumulados para fidelización
    puntos = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntos acumulados"
    )
    
    # Contador de domicilios del mes para "Toma tu 4x3"
    domicilios_mes = models.PositiveIntegerField(
        default=0,
        verbose_name="Domicilios realizados este mes"
    )
    
    # Último mes que se contabilizó (para resetear el contador mensual)
    mes_ultimo_domicilio = models.PositiveIntegerField(
        default=0,
        verbose_name="Mes del último domicilio"
    )

    # Dirección para la simulación de pedidos a domicilio
    direccion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Dirección de domicilio"
    )

    # Representación del objeto (Cómo se verá en el panel de Jazzmin)
    def __str__(self):
        return f"{self.username} ({self.rol})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

# Create your models here.
