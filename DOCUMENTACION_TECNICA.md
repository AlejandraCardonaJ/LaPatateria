# 📚 Documentación Técnica - La Patatería

> Explicación detallada de la arquitectura, flujo de datos y conexiones entre aplicaciones

---

## Flujo General de la Aplicación

```
Usuario → URL → Vista → Modelos → Base de Datos
                ↓
            Templates
                ↓
            HTML/CSS/JS
```

---

##  Estructura de Conexiones

### Request típico: "Ver carta de productos"

```
1. URL: /carta/
   ↓
2. app_carta/urls.py → carta/
   ↓
3. app_carta/views.py → carta()
   ↓
4. app_carta/models.py → Categoria.objects.filter(), Producto.objects.filter()
   ↓
5. Base de datos SQLite (db.sqlite3)
   ↓
6. Render: templates/carta/carta.html
   ↓
7. Usuario ve la página
```

---

## 📦 APP_CARTA - Gestión del Menú

### Propósito
Administrar los productos y categorías que se muestran en la carta del restaurante.

### Modelos (`app_carta/models.py`)

#### Categoria
```python
class Categoria(models.Model):
    nombre = CharField(100)           # Ej: "Pizzas", "Bebidas"
    descripcion = TextField           # Descripción opcional
    orden = PositiveIntegerField      # Para ordenar en la carta
    activa = BooleanField             # Mostrar/ocultar categoría
```

#### Producto
```python
class Producto(models.Model):
    categoria = ForeignKey(Categoria) # Relación con categoría
    nombre = CharField(200)           # Ej: "Pizza Hawaiana"
    descripcion = TextField           # Descripción del producto
    precio = DecimalField(10, 0)      # Precio en pesos
    imagen = ImageField               # Foto del producto
    disponible = BooleanField         # Si se puede ordenar
    es_recomendado = BooleanField     # Producto destacado
```

### Vistas (`app_carta/views.py`)

| Vista | URL | Función |
|-------|-----|---------|
| `home()` | `/` | Página principal con categorías y productos destacados |
| `carta()` | `/carta/` | Carta completa con todas las categorías |
| `carta_pdf()` | `/carta/pdf/` | Genera PDF del menú |

### Flujo de Datos
```
URL /carta/ 
  → views.carta()
  → models.Categoria.objects.filter(activa=True)
  → models.Producto.objects.filter(disponible=True)
  → template: carta/carta.html
  → HTML con Bootstrap
```

---

## 👥 APP_USUARIOS - Autenticación y Perfiles

### Propósito
Manejar registro, login, perfiles de usuarios y el panel de administración.

### Modelo (`app_usuarios/models.py`)

```python
class Usuario(AbstractUser):  # Hereda de Django User
    ROLES_CHOICES = [
        ('CLIENTE', 'Cliente'),
        ('DUENO', 'Dueño/Administrador'),
    ]
    
    rol = CharField(10, choices=ROLES_CHOICES, default='CLIENTE')
    telefono = CharField(15)
    fecha_nacimiento = DateField  # Importante para Papa Cumpleañera
    puntos = PositiveIntegerField   # Sistema de puntos
    domicilios_mes = PositiveIntegerField  # Contador para 4x3
    mes_ultimo_domicilio = PositiveIntegerField  # Mes actual
    direccion = TextField
```

### Vistas Principales (`app_usuarios/views.py`)

#### Autenticación
| Vista | URL | Función |
|-------|-----|---------|
| `login_view()` | `/usuarios/login/` | Inicio de sesión |
| `logout_view()` | `/usuarios/logout/` | Cerrar sesión |
| `registro_view()` | `/usuarios/registro/` | Registro de nuevos clientes |

#### Perfil de Cliente
| Vista | URL | Función |
|-------|-----|---------|
| `perfil_view()` | `/usuarios/perfil/` | Ver perfil y pedidos |
| `actualizar_perfil_view()` | `/usuarios/perfil/actualizar/` | Editar datos |

#### Panel de Administrador
| Vista | URL | Función |
|-------|-----|---------|
| `admin_panel_view()` | `/usuarios/admin-panel/` | Dashboard principal |
| `admin_productos_view()` | `/usuarios/admin-panel/productos/` | Gestionar productos |
| `admin_categorias_view()` | `/usuarios/admin-panel/categorias/` | Gestionar categorías |
| `admin_clientes_view()` | `/usuarios/admin-panel/clientes/` | Ver clientes |
| `admin_pedidos_view()` | `/usuarios/admin-panel/pedidos/` | Ver todos los pedidos |
| `admin_fidelizacion_view()` | `/usuarios/admin-panel/fidelizacion/` | Gestionar programas |

### Flujo de Login
```
1. Usuario va a /usuarios/login/
2. Vista: login_view()
3. Formulario: AuthenticationForm de Django
4. Validación: authenticate(username, password)
5. Login: login(request, user)
6. Según rol:
   - DUENO → /usuarios/admin-panel/
   - CLIENTE → /usuarios/perfil/
```

---

## 🛒 APP_PEDIDOS - Carrito y Pedidos

### Propósito
Gestionar el carrito de compras y la creación/seguimiento de pedidos.

### Modelos (`app_pedidos/models.py`)

#### Pedido
```python
class Pedido(models.Model):
    # Estados del pedido
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),      # Nuevo pedido
        ('CONFIRMADO', 'Confirmado'),    # Aceptado por el admin
        ('PREPARANDO', 'Preparando'),    # En preparación
        ('EN_CAMINO', 'En camino'),     # Enviado
        ('ENTREGADO', 'Entregado'),      # Completado
        ('CANCELADO', 'Cancelado'),      # Cancelado
    ]
    
    usuario = ForeignKey(Usuario)        # Cliente que ordenó
    tipo_entrega = CharField             # TIENDA o DOMICILIO
    direccion_entrega = TextField        # Dirección (si es domicilio)
    telefono_contacto = CharField        # Teléfono
    total = DecimalField                 # Total a pagar
    estado = CharField                   # Estado actual
    aplica_papa_cumpleañera = BooleanField  # Fidelización
    aplica_papa_oclock = BooleanField       # Fidelización
    aplica_4x3 = BooleanField                # Fidelización
    descuento_aplicado = DecimalField     # Descuento total
    costo_envio = DecimalField            # Costo de envío
    observaciones = TextField             # Notas del cliente
    fecha_pedido = DateTimeField         # Fecha de creación
```

#### DetallePedido
```python
class DetallePedido(models.Model):
    pedido = ForeignKey(Pedido)          # Pedido al que pertenece
    producto_nombre = CharField(200)    # Nombre del producto
    cantidad = PositiveIntegerField     # Cuántos pidió
    precio_unitario = DecimalField       # Precio al momento de comprar
    subtotal = DecimalField              # cantidad * precio_unitario
```

### Vistas (`app_pedidos/views.py`)

#### Carrito
| Vista | URL | Función |
|-------|-----|---------|
| `ver_carrito()` | `/pedidos/carrito/` | Mostrar productos en carrito |
| `agregar_al_carrito()` | `/pedidos/carrito/agregar/<id>/` | Agregar producto (AJAX) |
| `actualizar_cantidad_carrito()` | `/pedidos/carrito/actualizar/<id>/<cantidad>/` | Cambiar cantidad |
| `eliminar_del_carrito()` | `/pedidos/carrito/eliminar/<id>/` | Quitar producto |

#### Pedidos
| Vista | URL | Función |
|-------|-----|---------|
| `confirmar_pedido()` | `/pedidos/confirmar/` | Crear pedido desde carrito |
| `mis_pedidos()` | `/pedidos/mis-pedidos/` | Historial del cliente |

### Flujo de un Pedido
```
1. Cliente ve productos en /carta/
2. Click "Agregar" → AJAX → /pedidos/carrito/agregar/1/
3. Carrito se guarda en sesión: request.session['carrito']
4. Cliente va a /pedidos/carrito/
5. Llena formulario (tipo entrega, dirección, teléfono)
6. Click "Confirmar Pedido" → POST a /pedidos/confirmar/
7. Vista confirmar_pedido():
   - Lee carrito de la sesión
   - Calcula total
   - Aplica fidelización (llama a app_fidelizacion)
   - Crea Pedido en BD
   - Crea DetallePedido para cada producto
   - Limpia carrito de la sesión
8. Redirige a /pedidos/confirmacion/
```

---

## 🎁 APP_FIDELIZACIÓN - Sistema de Recompensas (EN DETALLE)

### Propósito
Gestionar programas de fidelización para aumentar la retención de clientes.

### ⭐️ Programas de Fidelización

#### 1. Papa Cumpleañera 🎂
- **Cómo funciona**: Si es el cumpleaños del cliente, obtiene un pedido gratis hasta $80,000
- **Activación automática**: Se verifica cada vez que el usuario inicia sesión o visita el perfil
- **Restricción**: Solo un pedido gratis por día (cumpleaños)

#### 2. Papa O'clock ⏰
- **Cómo funciona**: Envío gratis en las primeras 2 horas (12:00 PM - 2:00 PM)
- **Activación**: Automática según la hora actual
- **Verificación**: Se compara con la hora de Colombia (UTC-5)

#### 3. Papa Lovers 4x3 🍟
- **Cómo funciona**: El 4to domicilio del mes es gratis (tope $60,000)
- **Contador**: Se cuenta cada pedido a domicilio
- **Reinicio**: El contador se reinicia cada mes

#### 4. Dado Dinámico 🎲
- **Cómo funciona**: Al pedir a domicilio, se lanza un dado virtual
- **Recompensas posibles**:
  - 1: Postre de la casa Gratis
  - 2: Porción de papas a la francesa Gratis
  - 3: Vuelve a intentarlo
  - 4: Bebida gratis (Piña Colada o Coco)
  - 5: Gaseosa 400ml Gratis
  - 6: Vuelve a intentarlo
- **Condición**: Solo se muestra si NO tiene otras fidelizaciones gratuitas

### Modelo (`app_fidelizacion/models.py`)

```python
class ProgramaFidelizacion(models.Model):
    """Programas de fidelización configurables"""
    TIPO_CHOICES = [
        ('DADO_DINAMICO', 'Dado Dinámico'),
        ('PAPA_CUMPLEANERA', 'Papa Cumpleañera'),
        ('PAPA_OCLOCK', 'Papa Oclock'),
        ('PAPA_LOVERS_4X3', 'Papa Lovers 4x3'),
    ]
    
    nombre = CharField(100)
    tipo = CharField(30, choices=TIPO_CHOICES)
    descripcion = TextField
    icono = CharField(50, default='🎁')
    activo = BooleanField
    valor_descuento = DecimalField  # Porcentaje
    monto_maximo = DecimalField     # Tope máximo


class ResultadoFidelizacion(models.Model):
    """Historial de fidelizaciones por usuario"""
    usuario = ForeignKey(Usuario)
    programa = ForeignKey(ProgramaFidelizacion)
    resultado = CharField(100)      # Resultado del dado
    recompensa = CharField(200)     # Recompensa obtenida
    pedido = ForeignKey(Pedido)     # Pedido relacionado
    fecha = DateTimeField
```

### Función Principal: `verificar_fidelizacion()` (`app_fidelizacion/views.py`)

Esta es la función más importante del sistema de fidelización:

```python
def verificar_fidelizacion(usuario):
    """
    Verifica las fidelizaciones aplicables para el usuario.
    Retorna un diccionario con las fidelizaciones activas.
    """
    # 1. Obtener hora actual de Colombia
    ahora_utc = timezone.now()
    ahora = (ahora_utc - timedelta(hours=5)).time()
    hoy = (ahora_utc - timedelta(hours=5)).date()
    
    # 2. Contar domicilios del mes actual
    domicilios_mes = Pedido.objects.filter(
        usuario=usuario,
        tipo_entrega='DOMICILIO',
        fecha_pedido__month=mes_actual
    ).count()
    
    # 3. Inicializar diccionario de fidelización
    fidelizacion = {
        'papa_cumpleañera': False,
        'papa_oclock': False,
        'toma_4x3': False,
        'mensaje': '',
        'domicilios_mes': domicilios_mes
    }
    
    # 4. Verificar PAPA CUMPLEAÑERA
    if usuario.fecha_nacimiento:
        if (usuario.fecha_nacimiento.month == hoy.month and 
            usuario.fecha_nacimiento.day == hoy.day):
            # Verificar si ya usó el beneficio hoy
            pedidos_hoy = Pedido.objects.filter(
                usuario=usuario,
                tipo_entrega='DOMICILIO',
                fecha_pedido__date=hoy
            ).count()
            
            if pedidos_hoy == 0:
                fidelizacion['papa_cumpleañera'] = True
                fidelizacion['mensaje'] = '🎂 ¡Feliz cumpleaños! Tienes un pedido gratis'
    
    # 5. Verificar PAPA O'CLOCK (12pm - 2pm)
    hora_apertura = datetime.strptime('12:00', '%H:%M').time()
    hora_limite = datetime.strptime('14:00', '%H:%M').time()
    
    if hora_apertura <= ahora <= hora_limite:
        fidelizacion['papa_oclock'] = True
        fidelizacion['mensaje'] = '🕐 ¡Envío gratis en las primeras 2 horas!'
    
    # 6. Verificar PAPA LOVERS 4x3 (4to domicilio gratis)
    if domicilios_mes == 3:
        fidelizacion['toma_4x3'] = True
        fidelizacion['mensaje'] = '🎉 ¡Tu 4to domicilio es gratis!'
    
    return fidelizacion
```

### Cómo se Aplica la Fidelización al hacer un Pedido

En `app_pedidos/views.py` → función `confirmar_pedido()`:

```python
def confirmar_pedido(request):
    # 1. Obtener fidelizaciones del usuario
    fidelizacion = verificar_fidelizacion(usuario)
    
    # 2. Calcular descuento según cada programa
    descuento = 0
    costo_envio = 5000  # Costo base
    
    if tipo_entrega == 'DOMICILIO':
        # Dado dinámico (solo si no tiene otras fidelizaciones)
        if not fidelizacion['papa_cumpleañera'] and not fidelizacion['toma_4x3']:
            resultado_dado, recompensa_dado = obtener_resultado_dado()
        
        # Envío gratis por Papa O'clock
        if fidelizacion['papa_oclock']:
            costo_envio = 0
    
    # Descuento por Papa Cumpleañera
    if fidelizacion['papa_cumpleañera'] and total >= 80000:
        descuento = total  # Hasta $80k
    
    # Descuento por 4x3
    elif fidelizacion['toma_4x3'] and tipo_entrega == 'DOMICILIO':
        descuento = min(costo_envio, 60000)  # Tope $60k
    
    # 3. Crear pedido con los datos de fidelización
    pedido = Pedido.objects.create(
        ...
        aplica_papa_cumpleañera=fidelizacion['papa_cumpleañera'],
        aplica_papa_oclock=fidelizacion['papa_oclock'],
        aplica_4x3=fidelizacion['toma_4x3'],
        descuento_aplicado=descuento,
        costo_envio=costo_envio,
        ...
    )
```

### Dónde se Muestra la Fidelización

1. **Perfil del cliente** (`app_usuarios/templates/usuarios/perfil.html`)
   - Muestra programas disponibles
   - Muestra mensaje de fidelización activo

2. **Burbuja flotante** (en `app_carta/templates/carta/index.html`)
   - Aparece si el usuario tiene fidelización activa
   - Muestra el beneficio disponible

3. **Confirmación de pedido** (`app_pedidos/templates/pedidos/confirmacion.html`)
   - Muestra resultado del dado si aplica
   - Muestra descuentos aplicados

---

## 🔗 Conexión Entre Apps

### Diagrama de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    LAPATATERIA (Proyecto)                   │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   APP_CARTA     │  │   APP_PEDIDOS   │  │  APP_USUARIOS   │
│                 │  │                 │  │                 │
│ - Categoria     │◄─┤ - Pedido        │  │ - Usuario       │
│ - Producto      │  │ - DetallePedido │─►│ (AbstractUser)  │
│                 │  │                 │  │                 │
└─────────────────┘  └────────┬────────┘  └────────┬────────┘
                              │                    │
                              ▼                    │
┌─────────────────────────────────────────────────────────────┐
│                    APP_FIDELIZACIÓN                         │
│                                                            │
│ - ProgramaFidelizacion ◄───────────────────────────────────┘
│ - ResultadoFidelizacion                                    │
│                                                            │
│ ◄── verifica_fidelizacion(usuario)                        │
│ ◄── obtener_resultado_dado()                               │
│ ◄── aplicar_fidelizacion(usuario, tipo, total)            │
└─────────────────────────────────────────────────────────────┘
```

### Ejemplo de Flujo Completo: Cliente hace pedido a domicilio

```
1. CLIENTE inicia sesión
   URL: /usuarios/login/
   → app_usuarios/views.py: login_view()
   → Autenticación Django

2. CLIENTE ve la carta
   URL: /carta/
   → app_carta/views.py: home()
   → app_carta/models.py: Categoria, Producto
   → Template: carta/index.html

3. CLIENTE agrega producto al carrito
   URL: /pedidos/carrito/agregar/5/
   → app_pedidos/views.py: agregar_al_carrito()
   → Guarda en request.session['carrito']
   → JSON response

4. CLIENTE confirma el pedido
   URL: /pedidos/confirmar/ (POST)
   → app_pedidos/views.py: confirmar_pedido()
   
   ▲ Durante este proceso:
   │
   ├─► Llama a app_fidelizacion/views.py: verificar_fidelizacion()
   │   ├─► Verifica si es cumpleaños
   │   ├─► Verifica hora actual (Papa O'clock)
   │   ├─► Cuenta domicilios del mes (4x3)
   │   └─► Retorna diccionario con fidelizaciones
   │
   ├─► Crea Pedido en app_pedidos/models.py
   │   └─► Guarda aplica_papa_cumpleañera, aplica_papa_oclock, aplica_4x3
   │
   └─► Crea DetallePedido para cada producto

5. DUEÑO ve el pedido en su panel
   URL: /usuarios/admin-panel/pedidos/
   → app_usuarios/views.py: admin_pedidos_view()
   → app_pedidos/models.py: Pedido.objects.all()
   → Template: admin_pedidos.html

6. DUEÑO cambia estado del pedido
   URL: /usuarios/admin-panel/pedidos/1/estado/ (POST)
   → app_usuarios/views.py: admin_pedido_estado_view()
   → Actualiza pedido.estado = 'PREPARANDO'
```

---

## 📁 Archivos Clave Explicados

### `lapatateriaa/settings.py`
Configuración principal de Django:
- `AUTH_USER_MODEL`: Define el modelo de usuario personalizado
- `INSTALLED_APPS`: Apps del proyecto
- `DATABASES`: Configuración de SQLite

### `lapatateriaa/urls.py`
Define las rutas principales:
```python
urlpatterns = [
    path('admin/', admin.site.urls),           # Panel técnico Django
    path('', include('app_carta.urls')),       # Carta pública
    path('usuarios/', include('app_usuarios.urls')),  # Login/registro
    path('pedidos/', include('app_pedidos.urls')),     # Carrito/pedidos
]
```

### `app_usuarios/forms.py`
Formulario de registro:
```python
class RegistroForm(UserCreationForm):
    # Campos: username, email, telefono, fecha_nacimiento, direccion
    # Guardar con rol='CLIENTE' por defecto
```

---

## 🎯 Resumen: Cuándo usar cada App

| Necesidad | App | Modelos/Vistas |
|-----------|-----|----------------|
| Mostrar productos | app_carta | Categoria, Producto, home(), carta() |
| Registro/Login | app_usuarios | Usuario, login_view(), registro_view() |
| Carrito de compras | app_pedidos | ver_carrito(), agregar_al_carrito() |
| Crear pedido | app_pedidos | Pedido, DetallePedido, confirmar_pedido() |
| Ver fidelización | app_fidelizacion | verificar_fidelizacion() |
| Panel admin | app_usuarios | admin_panel_view(), admin_productos_view(), etc. |

---

## 🚀 Próximos Pasos para Extensiones

1. **Reportes**: Crear vista en app_usuarios para exportar PDF de ventas
2. **Notificaciones**: Agregar emails cuando cambie estado del pedido
3. **Pagos**: Integrar pasarela de pago (MercadoPago, PayU)
4. **Estadísticas**: Gráficos de ventas en dashboard admin
