from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta

from app_carta.models import Producto
from app_pedidos.models import Pedido, DetallePedido
from app_usuarios.models import Usuario
from app_fidelizacion.views import verificar_fidelizacion, obtener_resultado_dado, aplicar_fidelizacion


@login_required
def ver_carrito(request):
    """Vista para mostrar el carrito de compras."""
    # Obtener carrito de la sesión
    carrito = request.session.get('carrito', {})
    
    productos_carrito = []
    total = 0
    
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id, disponible=True)
            subtotal = producto.precio * cantidad
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
        except Producto.DoesNotExist:
            continue
    
    # Verificar fidelizaciones
    fidelizacion = verificar_fidelizacion(request.user)
    
    # Verificar si ya usó su beneficio de Papa Cumpleañera hoy (para bloquear el carrito)
    bloqueado_cumpleañero = False
    if request.user.fecha_nacimiento:
        from django.utils import timezone
        from datetime import datetime, timedelta
        ahora_utc = timezone.now()
        hoy = (ahora_utc - timedelta(hours=5)).date()
        
        if (request.user.fecha_nacimiento.month == hoy.month and 
            request.user.fecha_nacimiento.day == hoy.day):
            # Es su cumpleaños hoy, verificar si ya hizo un pedido
            from app_pedidos.models import Pedido
            fecha_inicio = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
            fecha_fin = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
            
            pedidos_hoy = Pedido.objects.filter(
                usuario=request.user,
                tipo_entrega='DOMICILIO',
                fecha_pedido__gte=fecha_inicio,
                fecha_pedido__lte=fecha_fin
            ).count()
            
            if pedidos_hoy > 0:
                bloqueado_cumpleañero = True
    
    context = {
        'productos_carrito': productos_carrito,
        'total': total,
        'fidelizacion': fidelizacion,
        'tipo_entrega': 'TIENDA',  # Por defecto, se cambia al confirmar
        'bloqueado_cumpleañero': bloqueado_cumpleañero
    }
    
    return render(request, 'pedidos/carrito.html', context)


@require_POST
@login_required
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito."""
    producto = get_object_or_404(Producto, id=producto_id, disponible=True)
    
    # Obtener o crear carrito en sesión
    carrito = request.session.get('carrito', {})
    
    # Agregar o incrementar cantidad
    if str(producto_id) in carrito:
        carrito[str(producto_id)] += 1
    else:
        carrito[str(producto_id)] = 1
    
    request.session['carrito'] = carrito
    
    # Contador de items
    total_items = sum(carrito.values())
    
    return JsonResponse({
        'success': True,
        'message': f'{producto.nombre} agregado al carrito',
        'total_items': total_items
    })


@require_POST
@login_required
def actualizar_cantidad(request, producto_id):
    """Actualiza la cantidad de un producto en el carrito."""
    cantidad = int(request.POST.get('cantidad', 1))
    
    carrito = request.session.get('carrito', {})
    
    if cantidad > 0:
        carrito[str(producto_id)] = cantidad
    else:
        del carrito[str(producto_id)]
    
    request.session['carrito'] = carrito
    
    return JsonResponse({'success': True})


@require_POST
@login_required
def actualizar_cantidad_carrito(request, producto_id, cantidad):
    """Actualiza la cantidad de un producto en el carrito."""
    carrito = request.session.get('carrito', {})
    
    producto_id_str = str(producto_id)
    if cantidad > 0:
        carrito[producto_id_str] = cantidad
    else:
        # Si la cantidad es 0 o menos, eliminar el producto
        if producto_id_str in carrito:
            del carrito[producto_id_str]
    
    request.session['carrito'] = carrito
    
    return JsonResponse({'success': True})


@require_POST
@login_required
def eliminar_del_carrito(request, producto_id):
    """Elimina un producto del carrito."""
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
    
    return JsonResponse({'success': True})


@require_POST
@login_required
def confirmar_pedido(request):
    """Confirma el pedido y aplica fidelizaciones."""
    tipo_entrega = request.POST.get('tipo_entrega', 'TIENDA')
    direccion = request.POST.get('direccion', '')
    telefono = request.POST.get('telefono', '')
    observaciones = request.POST.get('observaciones', '')
    
    # Obtener carrito
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.error(request, 'El carrito está vacío')
        return redirect('pedidos:ver_carrito')
    
    # Calcular total
    total = 0
    productos = []
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id, disponible=True)
            subtotal = producto.precio * cantidad
            total += subtotal
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            continue
    
    usuario = request.user
    fidelizacion = verificar_fidelizacion(usuario)
    
    # Variables para el pedido
    descuento = 0
    costo_envio = 5000  # Costo base de envío
    
    # Si es domicilio, aplicar dado dinámico
    resultado_dado = None
    recompensa_dado = None
    
    if tipo_entrega == 'DOMICILIO':
        # Solo mostrar dado si NO tiene otras fidelizaciones gratuitas
        if not fidelizacion['papa_cumpleañera'] and not fidelizacion['toma_4x3']:
            resultado_dado, recompensa_dado = obtener_resultado_dado()
        
        # Aplicar costo de envío
        if fidelizacion['papa_oclock']:
            costo_envio = 0  # Envío gratis por Papa O'clock
    
    # Aplicar descuentos según fidelización
    aplica_papa_cumpleañera = False
    aplica_4x3 = False
    
    if fidelizacion['papa_cumpleañera'] and total >= 80000:
        aplica_papa_cumpleañera = True
        descuento = total  # Pedido completo gratis hasta $80k
    elif fidelizacion['toma_4x3'] and tipo_entrega == 'DOMICILIO':
        aplica_4x3 = True
        if costo_envio > 60000:
            descuento = 60000  # Tope de $60k
        else:
            descuento = costo_envio
    
    
    # Crear el pedido
    pedido = Pedido.objects.create(
        usuario=usuario,
        tipo_entrega=tipo_entrega,
        direccion_entrega=direccion if tipo_entrega == 'DOMICILIO' else '',
        telefono_contacto=telefono,
        total=total - descuento,
        estado='CONFIRMADO',  # Estado inicial confirmado
        resultado_dado=resultado_dado,
        recompensa_dado=recompensa_dado,
        aplica_papa_cumpleañera=aplica_papa_cumpleañera,
        aplica_papa_oclock=fidelizacion['papa_oclock'],
        aplica_4x3=aplica_4x3,
        descuento_aplicado=descuento,
        costo_envio=costo_envio,
        observaciones=observaciones
    )
    
    # Crear detalles del pedido
    for item in productos:
        DetallePedido.objects.create(
            pedido=pedido,
            producto_nombre=item['producto'].nombre,
            cantidad=item['cantidad'],
            precio_unitario=item['producto'].precio,
            subtotal=item['subtotal']
        )
    
    # Actualizar contador de domicilios si es entrega a domicilio
    if tipo_entrega == 'DOMICILIO':
        # Usar hora de Colombia para consistencia
        ahora_utc = timezone.now()
        mes_actual = (ahora_utc - timedelta(hours=5)).month
        if usuario.mes_ultimo_domicilio != mes_actual:
            usuario.domicilios_mes = 1
            usuario.mes_ultimo_domicilio = mes_actual
        else:
            usuario.domicilios_mes += 1
        usuario.save()
    
    # Limpiar carrito
    request.session['carrito'] = {}
    
    # Calcular el número de pedido para este usuario (empezando desde 1)
    numero_pedido = Pedido.objects.filter(usuario=usuario).count() + 1
    
    # Mostrar resultado del dado si aplica
    context = {
        'pedido': pedido,
        'numero_pedido': numero_pedido,
        'resultado_dado': resultado_dado,
        'recompensa_dado': recompensa_dado,
        'fidelizacion': fidelizacion,
        'descuento_total': descuento
    }
    
    return render(request, 'pedidos/confirmacion.html', context)


@login_required
def mis_pedidos(request):
    """Muestra los pedidos del usuario."""
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('detalles')
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})
