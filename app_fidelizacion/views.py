"""
Vistas para el módulo de fidelización.
Contiene la lógica de los programas de fidelización.
"""
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
import random
import time


def verificar_fidelizacion(usuario):
    """
    Verifica las fidelizaciones aplicables para el usuario.
    Retorna un diccionario con las fidelizaciones activas.
    """
    # Obtener hora local de Colombia (UTC-5) restando 5 horas a la hora UTC
    ahora_utc = timezone.now()
    ahora = (ahora_utc - timedelta(hours=5)).time()
    hoy = (ahora_utc - timedelta(hours=5)).date()
    mes_actual = hoy.month
    
    # Contar pedidos de domicilio del mes actual desde la base de datos
    from app_pedidos.models import Pedido
    try:
        domicilios_mes = Pedido.objects.filter(
            usuario=usuario,
            tipo_entrega='DOMICILIO',
            fecha_pedido__month=mes_actual,
            fecha_pedido__year=hoy.year
        ).count()
    except:
        # Si hay error, usar el contador del usuario
        if usuario.mes_ultimo_domicilio == mes_actual:
            domicilios_mes = usuario.domicilios_mes
        else:
            domicilios_mes = 0
    
    fidelizacion = {
        'papa_cumpleañera': False,
        'papa_oclock': False,
        'toma_4x3': False,
        'mensaje': '',
        'domicilios_mes': domicilios_mes
    }
    
    # 1. Papa Cumpleañera: Si es su cumpleaños, pedido gratis de $80,000 (solo una vez por día)
    if usuario.fecha_nacimiento:
        if (usuario.fecha_nacimiento.month == hoy.month and 
            usuario.fecha_nacimiento.day == hoy.day):
            # Verificar si ya hizo un pedido a domicilio hoy (sin importar el estado del campo aplica_papa_cumpleañera)
            fecha_inicio = datetime(hoy.year, hoy.month, hoy.day, 0, 0, 0)
            fecha_fin = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
            
            # Contar pedidos de domicilio hechos hoy
            pedidos_hoy = Pedido.objects.filter(
                usuario=usuario,
                tipo_entrega='DOMICILIO',
                fecha_pedido__gte=fecha_inicio,
                fecha_pedido__lte=fecha_fin
            ).count()
            
            if pedidos_hoy == 0:
                # Es su cumpleaños y no ha hecho ningún pedido a domicilio hoy
                fidelizacion['papa_cumpleañera'] = True
                fidelizacion['mensaje'] = '🎂 ¡Feliz cumpleaños! Tienes un pedido gratis de hasta $80.000'
            else:
                # Ya hizo un pedido a domicilio hoy
                fidelizacion['papa_cumpleañera'] = False
                fidelizacion['mensaje'] = '🎂 Ya usaste tu beneficio de Papa Cumpleañera hoy. ¡Vuelve mañana!'
    
    # 2. Papa O'clock: Envío gratis en las primeras 2 horas (12:00 PM - 2:00 PM)
    hora_apertura = datetime.strptime('12:00', '%H:%M').time()
    hora_limite = datetime.strptime('14:00', '%H:%M').time()
    
    if hora_apertura <= ahora <= hora_limite:
        fidelizacion['papa_oclock'] = True
        if fidelizacion['mensaje']:
            fidelizacion['mensaje'] += ' + ¡Envío gratis en las primeras 2 horas!'
        else:
            fidelizacion['papa_oclock'] = True
            fidelizacion['mensaje'] = '🕐 ¡Envío gratis en las primeras 2 horas!'
    
    # 3. Papa Lovers 4x3: Si llevó exactamente 3 domicilios este mes, el 4to es gratis (tope $60.000)
    # Solo aplica si tiene exactamente 3 pedidos y está en el mismo mes
    if domicilios_mes == 3:
        fidelizacion['toma_4x3'] = True
        if fidelizacion['mensaje']:
            fidelizacion['mensaje'] += ' + Tu próximo domicilio es gratis (tope $60.000)'
        else:
            fidelizacion['mensaje'] = '🎉 ¡Tu 4to domicilio es gratis! (tope $60.000)'
    elif domicilios_mes > 3:
        # Ya usó su beneficio del mes - no hace nada
        pass
    
    return fidelizacion


def obtener_resultado_dado():
    """
    Retorna un número aleatorio del 1 al 6 y su recompensa.
    """
    random.seed(int(time.time() * 1000) % 1000000)
    resultado = random.randint(1, 6)
    
    recompensas = {
        1: 'Postre de la casa Gratis',
        2: 'Porción personal de papas a la francesa Gratis',
        3: 'Vuelve a intentarlo en una próxima compra',
        4: 'Bebida de la Casa Gratis "Piña Colada o Coco"',
        5: 'Gaseosa 400ml Gratis',
        6: 'Vuelve a intentarlo en una próxima compra'
    }
    
    return resultado, recompensas[resultado]


def aplicar_fidelizacion(usuario, tipo_entrega, total_pedido):
    """
    Aplica las fidelizaciones correspondientes al pedido.
    Retorna un diccionario con los resultados.
    """
    fidelizacion = verificar_fidelizacion(usuario)
    
    resultado = {
        'resultado_dado': None,
        'recompensa_dado': None,
        'aplica_papa_cumpleañera': False,
        'aplica_papa_oclock': False,
        'aplica_4x3': False,
        'descuento': 0,
        'costo_envio': 5000,  # Costo base
    }
    
    # Si es domicilio, aplicar dado dinámico
    if tipo_entrega == 'DOMICILIO':
        # Solo mostrar dado si NO tiene otras fidelizaciones gratuitas
        if not fidelizacion['papa_cumpleañera'] and not fidelizacion['toma_4x3']:
            resultado['resultado_dado'], resultado['recompensa_dado'] = obtener_resultado_dado()
        
        # Aplicar costo de envío
        if fidelizacion['papa_oclock']:
            resultado['costo_envio'] = 0  # Envío gratis por Papa O'clock
    
    # Aplicar descuentos según fidelización
    if fidelizacion['papa_cumpleañera'] and total_pedido >= 80000:
        resultado['aplica_papa_cumpleañera'] = True
        resultado['descuento'] = total_pedido  # Pedido completo gratis hasta $80k
    elif fidelizacion['toma_4x3'] and tipo_entrega == 'DOMICILIO':
        resultado['aplica_4x3'] = True
        if resultado['costo_envio'] > 60000:
            resultado['descuento'] = 60000  # Tope de $60k
        else:
            resultado['descuento'] = resultado['costo_envio']
    
    # Si hay resultado del dado, aplicar descuento si es 4
    if resultado['resultado_dado'] == 4 and not (resultado['aplica_papa_cumpleañera'] or resultado['aplica_4x3']):
        resultado['descuento'] += int(total_pedido * 0.15)  # 15% de descuento
    
    return resultado


def programas_disponibles(usuario):
    """
    Retorna lista de programas de fidelización disponibles para el usuario.
    """
    fidelizacion = verificar_fidelizacion(usuario)
    programas = []
    
    if fidelizacion['papa_cumpleañera']:
        programas.append({
            'codigo': 'papa_cumpleañera',
            'nombre': 'Papa Cumpleañera',
            'descripcion': 'Pedido gratis hasta $80.000 en tu cumpleaños',
            'icono': '🎂'
        })
    
    if fidelizacion['papa_oclock']:
        programas.append({
            'codigo': 'papa_oclock',
            'nombre': 'Papa Oclock',
            'descripcion': 'Envío gratis de 12pm a 2pm',
            'icono': '⏰'
        })
    
    if fidelizacion['toma_4x3']:
        programas.append({
            'codigo': 'papa_lovers_4x3',
            'nombre': 'Papa Lovers 4x3',
            'descripcion': 'Tu 4º domicilio gratis (tope $60.000)',
            'icono': '🍟'
        })
    
    return programas
