from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class Pedido(models.Model):
    """
    Modelo para los pedidos de los clientes.
    Maneja opciones de recogida en tienda o domicilio.
    """
    
    TIPO_ENTREGA_CHOICES = [
        ('TIENDA', 'Recoger en tienda'),
        ('DOMICILIO', 'Entrega a domicilio'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('PREPARANDO', 'Preparando'),
        ('EN_CAMINO', 'En camino'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name="Cliente"
    )
    
    tipo_entrega = models.CharField(
        max_length=10,
        choices=TIPO_ENTREGA_CHOICES,
        default='TIENDA',
        verbose_name="Tipo de entrega"
    )
    
    direccion_entrega = models.TextField(
        blank=True,
        null=True,
        verbose_name="Dirección de entrega (solo para domicilio)"
    )
    
    telefono_contacto = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Teléfono de contacto"
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Total del pedido"
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name="Estado del pedido"
    )
    
    # Resultados del Dado Dinámico (solo aplica para domicilio)
    resultado_dado = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Resultado del dado dinámico"
    )
    recompensa_dado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Recompensa del dado"
    )
    
    # Fidelización
    aplica_papa_cumpleañera = models.BooleanField(
        default=False,
        verbose_name="Aplica Papa Cumpleañera (pedido gratis)"
    )
    aplica_papa_oclock = models.BooleanField(
        default=False,
        verbose_name="Aplica Papa O'clock (envío gratis)"
    )
    aplica_4x3 = models.BooleanField(
        default=False,
        verbose_name="Aplica 4x3 (domicilio gratis)"
    )
    
    descuento_aplicado = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Descuento aplicado"
    )
    
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Costo de envío"
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    fecha_pedido = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del pedido"
    )
    
    fecha_entrega = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de entrega estimada"
    )
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - {self.estado}"


class DetallePedido(models.Model):
    """
    Detalles de cada producto en el pedido.
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Pedido"
    )
    
    producto_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del producto"
    )
    
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Precio unitario"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Subtotal"
    )
    
    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"
    
    def __str__(self):
        return f"{self.producto_nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
