from django.contrib import admin
from .models import Pedido, DetallePedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo_entrega', 'total', 'estado', 'fecha_pedido')
    list_filter = ('estado', 'tipo_entrega', 'fecha_pedido')
    search_fields = ('usuario__username', 'usuario__email', 'telefono_contacto')
    readonly_fields = ('fecha_pedido', 'resultado_dado', 'recompensa_dado')
    actions = ['eliminar_pedidos']
    
    def eliminar_pedidos(self, request, queryset):
        for pedido in queryset:
            pedido.delete()
        self.message_user(request, f'{queryset.count()} pedidos eliminados correctamente.')
    eliminar_pedidos.short_description = 'Eliminar pedidos seleccionados'
    
    def has_delete_permission(self, request, obj=None):
        return True
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('usuario', 'telefono_contacto')
        }),
        ('Tipo de Entrega', {
            'fields': ('tipo_entrega', 'direccion_entrega')
        }),
        ('Pedido', {
            'fields': ('total', 'estado', 'observaciones', 'fecha_pedido')
        }),
        ('Fidelización', {
            'fields': ('resultado_dado', 'recompensa_dado', 'aplica_papa_cumpleañera', 'aplica_papa_oclock', 'aplica_4x3', 'descuento_aplicado', 'costo_envio')
        }),
    )


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('producto_nombre', 'pedido__id')
