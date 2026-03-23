from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Usuario
from .forms import RegistroForm
from app_pedidos.models import Pedido
from app_fidelizacion.views import verificar_fidelizacion


def login_view(request):
    """Vista para el login unificado de clientes y administradores"""
    if request.user.is_authenticated:
        # Si ya está logueado, redirigir según su rol
        if request.user.rol == 'DUENO':
            return redirect('usuarios:admin_panel')
        else:
            return redirect('usuarios:perfil')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirección según el rol
                if user.rol == 'DUENO':
                    messages.success(request, f"Bienvenido, {user.username}!")
                    return redirect('usuarios:admin_panel')
                else:
                    messages.success(request, f"Bienvenido, {user.username}!")
                    return redirect('usuarios:perfil')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('carta:home')


def registro_view(request):
    """Vista para el registro de nuevos clientes"""
    if request.user.is_authenticated:
        if request.user.rol == 'DUENO':
            return redirect('usuarios:admin_panel')
        else:
            return redirect('usuarios:perfil')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Cuenta creada para {username}. Ahora puedes iniciar sesión.")
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista del perfil del cliente - solo accesible para clientes"""
    if request.user.rol == 'DUENO':
        return redirect('usuarios:admin_panel')
    
    # Obtener pedidos del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    pedidos_mes = Pedido.objects.filter(
        usuario=request.user,
        fecha_pedido__month=mes_actual,
        fecha_pedido__year=anio_actual
    ).count()
    
    # Obtener pedidos del mes actual (para el historial)
    pedidos_mes_lista = Pedido.objects.filter(
        usuario=request.user,
        fecha_pedido__month=mes_actual,
        fecha_pedido__year=anio_actual
    ).prefetch_related('detalles').order_by('-fecha_pedido')
    
    # Obtener fidelizaciones disponibles
    fidelizacion = verificar_fidelizacion(request.user)
    
    # Obtener programas disponibles
    from app_fidelizacion.views import programas_disponibles
    programas = programas_disponibles(request.user)
    
    context = {
        'usuario': request.user,
        'pedidos_mes': pedidos_mes,
        'todos_pedidos': pedidos_mes_lista,
        'fidelizacion': fidelizacion,
        'programas': programas,
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def actualizar_perfil_view(request):
    """Vista para actualizar el perfil del cliente"""
    if request.user.rol == 'DUENO':
        return redirect('usuarios:admin_panel')
    
    if request.method == 'POST':
        usuario = request.user
        
        # Actualizar campos permitidos
        if request.POST.get('telefono'):
            usuario.telefono = request.POST.get('telefono')
        if request.POST.get('direccion'):
            usuario.direccion = request.POST.get('direccion')
        if request.POST.get('email'):
            usuario.email = request.POST.get('email')
        
        usuario.save()
        messages.success(request, 'Perfil actualizado correctamente')
    
    return redirect('usuarios:perfil')


@login_required
def admin_panel_view(request):
    """Vista del panel de administración - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from datetime import datetime
    from django.db.models import Count, Sum
    from app_carta.models import Producto, Categoria
    
    # Obtener estadísticas
    total_clientes = Usuario.objects.filter(rol='CLIENTE').count()
    total_usuarios = Usuario.objects.count()
    
    # Pedidos de hoy
    hoy = datetime.now().date()
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    
    # Ingresos de hoy - Solo contar pedidos entregados (no cancelados)
    ingresos_hoy = Pedido.objects.filter(
        fecha_pedido__date=hoy,
        estado='ENTREGADO'  # El estado correcto es ENTREGADO, no COMPLETADO
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Productos y categorías
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    
    context = {
        'usuario': request.user,
        'total_clientes': total_clientes,
        'total_usuarios': total_usuarios,
        'pedidos_hoy': pedidos_hoy,
        'ingresos_hoy': ingresos_hoy,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
    }
    
    return render(request, 'usuarios/admin_panel.html', context)


@login_required
def admin_clientes_view(request):
    """Vista para gestionar clientes - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    # Obtener todos los clientes
    clientes = Usuario.objects.filter(rol='CLIENTE').order_by('-date_joined')
    
    # Obtener pedidos por cliente
    for cliente in clientes:
        cliente.total_pedidos = Pedido.objects.filter(usuario=cliente).count()
        cliente.ultimo_pedido = Pedido.objects.filter(usuario=cliente).order_by('-fecha_pedido').first()
    
    context = {
        'clientes': clientes,
    }
    
    return render(request, 'usuarios/admin_clientes.html', context)


@login_required
def admin_cliente_detalle_view(request, cliente_id):
    """Vista para ver detalle de un cliente - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_fidelizacion.views import verificar_fidelizacion
    
    cliente = get_object_or_404(Usuario, id=cliente_id)
    
    # Obtener pedidos del cliente
    pedidos = Pedido.objects.filter(usuario=cliente).order_by('-fecha_pedido')[:20]
    
    # Obtener fidelización del cliente
    fidelizacion = verificar_fidelizacion(cliente)
    
    # Obtener resultados de fidelización
    from app_fidelizacion.models import ResultadoFidelizacion
    resultados = ResultadoFidelizacion.objects.filter(usuario=cliente).order_by('-fecha')[:10]
    
    context = {
        'cliente': cliente,
        'pedidos': pedidos,
        'fidelizacion': fidelizacion,
        'resultados': resultados,
    }
    
    return render(request, 'usuarios/admin_cliente_detalle.html', context)


@login_required
def admin_cliente_editar_view(request, cliente_id):
    """Vista para editar un cliente - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    cliente = get_object_or_404(Usuario, id=cliente_id)
    
    if request.method == 'POST':
        cliente.first_name = request.POST.get('first_name', '')
        cliente.last_name = request.POST.get('last_name', '')
        cliente.email = request.POST.get('email', '')
        cliente.telefono = request.POST.get('telefono', '')
        cliente.direccion = request.POST.get('direccion', '')
        cliente.save()
        messages.success(request, f'Cliente "{cliente.username}" actualizado correctamente')
        return redirect('usuarios:admin_cliente_detalle', cliente_id=cliente.id)
    
    return render(request, 'usuarios/admin_cliente_form.html', {'cliente': cliente})


@login_required
def admin_cliente_toggle_view(request, cliente_id):
    """Vista para activar/desactivar un cliente"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    cliente = get_object_or_404(Usuario, id=cliente_id)
    cliente.is_active = not cliente.is_active
    cliente.save()
    
    estado = "activado" if cliente.is_active else "desactivado"
    messages.success(request, f'Cliente "{cliente.username}" {estado} correctamente')
    return redirect('usuarios:admin_cliente_detalle', cliente_id=cliente.id)


@login_required
def admin_pedidos_view(request):
    """Vista para gestionar pedidos - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    # Obtener todos los pedidos
    pedidos = Pedido.objects.select_related('usuario').order_by('-fecha_pedido')[:50]
    
    context = {
        'pedidos': pedidos,
    }
    
    return render(request, 'usuarios/admin_pedidos.html', context)


@login_required
def admin_pedido_detalle_view(request, pedido_id):
    """Vista para ver detalle de un pedido - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_pedidos.models import DetallePedido
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Usar el related manager es más confiable
    detalles = pedido.detalles.all()
    
    # Calcular subtotal desde los detalles
    subtotal_detalles = sum(d.subtotal for d in detalles)
    
    # El pedido.total ya incluye el descuento, calcular el subtotal original
    subtotal_original = subtotal_detalles if subtotal_detalles > 0 else pedido.total + pedido.descuento_aplicado
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'subtotal_original': subtotal_original,
    }
    
    return render(request, 'usuarios/admin_pedido_detalle.html', context)


@login_required
def admin_pedido_estado_view(request, pedido_id):
    """Vista para cambiar el estado de un pedido"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Validar que el estado sea válido
        estados_validos = ['PENDIENTE', 'CONFIRMADO', 'PREPARANDO', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO']
        if nuevo_estado in estados_validos:
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Pedido #{pedido.id} actualizado a "{nuevo_estado}"')
        else:
            messages.error(request, 'Estado no válido')
    
    return redirect('usuarios:admin_pedido_detalle', pedido_id=pedido_id)


@login_required
def admin_pedido_cancelar_view(request, pedido_id):
    """Vista para cancelar un pedido (marcar como cancelado)"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'CANCELADO'
    pedido.save()
    
    messages.success(request, f'Pedido #{pedido.id} ha sido cancelado')
    return redirect('usuarios:admin_pedidos')


@login_required
def admin_fidelizacion_view(request):
    """Vista para gestionar fidelización - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_fidelizacion.models import ProgramaFidelizacion
    
    # Obtener programas de fidelización
    programas = ProgramaFidelizacion.objects.all()
    
    context = {
        'programas': programas,
    }
    
    return render(request, 'usuarios/admin_fidelizacion.html', context)


@login_required
def admin_fidelizacion_toggle_view(request, programa_id):
    """Vista para activar/desactivar un programa de fidelización"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_fidelizacion.models import ProgramaFidelizacion
    
    programa = get_object_or_404(ProgramaFidelizacion, id=programa_id)
    programa.activo = not programa.activo
    programa.save()
    
    estado = "activado" if programa.activo else "desactivado"
    messages.success(request, f'Programa "{programa.nombre}" {estado} correctamente')
    return redirect('usuarios:admin_fidelizacion')


# ============================================
# VISTAS DE CRUD PARA PRODUCTOS Y CATEGORÍAS
# ============================================

@login_required
def admin_productos_view(request):
    """Vista para listar productos - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Producto, Categoria
    
    productos = Producto.objects.select_related('categoria').order_by('categoria', 'nombre')
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos,
        'categorias': categorias,
    }
    
    return render(request, 'usuarios/admin_productos.html', context)


@login_required
def admin_producto_crear_view(request):
    """Vista para crear un producto - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Producto, Categoria
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        categoria_id = request.POST.get('categoria')
        disponible = request.POST.get('disponible') == 'on'
        es_recomendado = request.POST.get('es_recomendado') == 'on'
        
        if nombre and precio and categoria_id:
            producto = Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=int(precio),
                categoria_id=categoria_id,
                disponible=disponible,
                es_recomendado=es_recomendado
            )
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente')
            return redirect('usuarios:admin_productos')
        else:
            messages.error(request, 'Por favor completa todos los campos requeridos')
    
    categorias = Categoria.objects.filter(activa=True)
    return render(request, 'usuarios/admin_producto_form.html', {'categorias': categorias, 'accion': 'crear'})


@login_required
def admin_producto_editar_view(request, producto_id):
    """Vista para editar un producto - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Producto, Categoria
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = int(request.POST.get('precio'))
        producto.categoria_id = request.POST.get('categoria')
        producto.disponible = request.POST.get('disponible') == 'on'
        producto.es_recomendado = request.POST.get('es_recomendado') == 'on'
        producto.save()
        
        messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente')
        return redirect('usuarios:admin_productos')
    
    categorias = Categoria.objects.filter(activa=True)
    return render(request, 'usuarios/admin_producto_form.html', {
        'producto': producto,
        'categorias': categorias,
        'accion': 'editar'
    })


@login_required
def admin_producto_eliminar_view(request, producto_id):
    """Vista para eliminar un producto - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Producto
    
    producto = get_object_or_404(Producto, id=producto_id)
    nombre = producto.nombre
    producto.delete()
    
    messages.success(request, f'Producto "{nombre}" eliminado exitosamente')
    return redirect('usuarios:admin_productos')


# ============================================
# VISTAS DE CRUD PARA CATEGORÍAS
# ============================================

@login_required
def admin_categorias_view(request):
    """Vista para listar categorías - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Categoria
    
    categorias = Categoria.objects.all().order_by('orden', 'nombre')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'usuarios/admin_categorias.html', context)


@login_required
def admin_categoria_crear_view(request):
    """Vista para crear una categoría - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Categoria
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        orden = request.POST.get('orden') or 0
        activa = request.POST.get('activa') == 'on'
        
        if nombre:
            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                orden=int(orden),
                activa=activa
            )
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente')
            return redirect('usuarios:admin_categorias')
        else:
            messages.error(request, 'Por favor ingresa el nombre de la categoría')
    
    return render(request, 'usuarios/admin_categoria_form.html', {'accion': 'crear'})


@login_required
def admin_categoria_editar_view(request, categoria_id):
    """Vista para editar una categoría - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Categoria
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        categoria.nombre = request.POST.get('nombre')
        categoria.descripcion = request.POST.get('descripcion')
        categoria.orden = int(request.POST.get('orden') or 0)
        categoria.activa = request.POST.get('activa') == 'on'
        categoria.save()
        
        messages.success(request, f'Categoría "{categoria.nombre}" actualizada exitosamente')
        return redirect('usuarios:admin_categorias')
    
    return render(request, 'usuarios/admin_categoria_form.html', {
        'categoria': categoria,
        'accion': 'editar'
    })


@login_required
def admin_categoria_eliminar_view(request, categoria_id):
    """Vista para eliminar una categoría - solo accesible para DUENO"""
    if request.user.rol != 'DUENO':
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect('usuarios:perfil')
    
    from app_carta.models import Categoria
    
    categoria = get_object_or_404(Categoria, id=categoria_id)
    nombre = categoria.nombre
    categoria.delete()
    
    messages.success(request, f'Categoría "{nombre}" eliminada exitosamente')
    return redirect('usuarios:admin_categorias')
