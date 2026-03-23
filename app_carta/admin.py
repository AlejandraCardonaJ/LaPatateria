from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración del panel administrativo para Categoría.
    """
    list_display = ['nombre', 'orden', 'activa', 'fecha_creacion']
    list_editable = ['orden', 'activa']
    search_fields = ['nombre', 'descripcion']
    ordering = ['orden', 'nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración del panel administrativo para Producto.
    """
    list_display = ['nombre', 'categoria', 'precio', 'disponible', 'es_recomendado']
    list_filter = ['categoria', 'disponible', 'es_recomendado']
    list_editable = ['disponible', 'es_recomendado']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']
    
    # Campos que se muestran en el detalle del producto
    fieldsets = (
        ('Información básica', {
            'fields': ('categoria', 'nombre', 'descripcion', 'precio')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Estado', {
            'fields': ('disponible', 'es_recomendado')
        }),
    )
