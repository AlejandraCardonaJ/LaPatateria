from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/actualizar/', views.actualizar_perfil_view, name='actualizar_perfil'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/clientes/', views.admin_clientes_view, name='admin_clientes'),
    path('admin-panel/clientes/<int:cliente_id>/', views.admin_cliente_detalle_view, name='admin_cliente_detalle'),
    path('admin-panel/clientes/<int:cliente_id>/editar/', views.admin_cliente_editar_view, name='admin_cliente_editar'),
    path('admin-panel/clientes/<int:cliente_id>/toggle/', views.admin_cliente_toggle_view, name='admin_cliente_toggle'),
    path('admin-panel/pedidos/', views.admin_pedidos_view, name='admin_pedidos'),
    path('admin-panel/pedidos/<int:pedido_id>/', views.admin_pedido_detalle_view, name='admin_pedido_detalle'),
    path('admin-panel/pedidos/<int:pedido_id>/estado/', views.admin_pedido_estado_view, name='admin_pedido_estado'),
    path('admin-panel/pedidos/<int:pedido_id>/cancelar/', views.admin_pedido_cancelar_view, name='admin_pedido_cancelar'),
    path('admin-panel/fidelizacion/', views.admin_fidelizacion_view, name='admin_fidelizacion'),
    path('admin-panel/fidelizacion/<int:programa_id>/toggle/', views.admin_fidelizacion_toggle_view, name='admin_fidelizacion_toggle'),
    # CRUD Productos
    path('admin-panel/productos/', views.admin_productos_view, name='admin_productos'),
    path('admin-panel/productos/crear/', views.admin_producto_crear_view, name='admin_producto_crear'),
    path('admin-panel/productos/<int:producto_id>/editar/', views.admin_producto_editar_view, name='admin_producto_editar'),
    path('admin-panel/productos/<int:producto_id>/eliminar/', views.admin_producto_eliminar_view, name='admin_producto_eliminar'),
    # CRUD Categorías
    path('admin-panel/categorias/', views.admin_categorias_view, name='admin_categorias'),
    path('admin-panel/categorias/crear/', views.admin_categoria_crear_view, name='admin_categoria_crear'),
    path('admin-panel/categorias/<int:categoria_id>/editar/', views.admin_categoria_editar_view, name='admin_categoria_editar'),
    path('admin-panel/categorias/<int:categoria_id>/eliminar/', views.admin_categoria_eliminar_view, name='admin_categoria_eliminar'),
]
