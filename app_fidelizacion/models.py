from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class ProgramaFidelizacion(models.Model):
    """
    Modelo para los programas de fidelización.
    """
    TIPO_CHOICES = [
        ('DADO_DINAMICO', 'Dado Dinámico'),
        ('PAPA_CUMPLEANERA', 'Papa Cumpleañera'),
        ('PAPA_OCLOCK', 'Papa Oclock'),
        ('PAPA_LOVERS_4X3', 'Papa Lovers 4x3'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, unique=True)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, default='🎁')
    activo = models.BooleanField(default=True)
    
    # Configuración específica
    valor_descuento = models.DecimalField(max_digits=5, decimal_places=0, default=0, help_text="Porcentaje de descuento")
    monto_maximo = models.DecimalField(max_digits=10, decimal_places=0, default=0, help_text="Monto máximo del beneficio")
    
    # Campos adicionales que existen en la base de datos
    cantidad_minima_pedidos = models.PositiveIntegerField(default=0)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Programa de Fidelización"
        verbose_name_plural = "Programas de Fidelización"
    
    def __str__(self):
        return self.nombre


class ResultadoFidelizacion(models.Model):
    """
    Registro de resultados de fidelización por usuario.
    """
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='resultados_fidelizacion'
    )
    programa = models.ForeignKey(
        ProgramaFidelizacion, 
        on_delete=models.CASCADE,
        related_name='resultados'
    )
    resultado = models.CharField(max_length=100)
    recompensa = models.CharField(max_length=200)
    pedido = models.ForeignKey(
        'app_pedidos.Pedido',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultados_fidelizacion'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Resultado de Fidelización"
        verbose_name_plural = "Resultados de Fidelización"
    
    def __str__(self):
        return f"{self.usuario.username} - {self.programa.nombre} - {self.resultado}"
