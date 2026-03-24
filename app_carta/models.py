from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class Categoria(models.Model):
    """
    Modelo para las categorías de productos en la carta.
    Ejemplos: Entradas, Pizzas, Bebidas, Postres, etc.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la categoría"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden de aparición"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="¿Categoría activa?"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo para los productos de la carta.
    Cada producto pertenece a una categoría y tiene nombre, descripción, precio e imagen.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name="Categoría"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del producto"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Precio ($)"
    )
    imagen = models.ImageField(
        upload_to='img/carta/productos/',
        storage=S3Boto3Storage(),
        blank=True,
        null=True,
        verbose_name="Imagen del producto"
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name="¿Disponible?"
    )
    es_recomendado = models.BooleanField(
        default=False,
        verbose_name="¿Es recomendado?"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.precio_formateado}"

    @property
    def precio_formateado(self):
        """Retorna el precio formateado con separador de miles"""
        return f"{self.precio:,.0f}".replace(",", ".")
