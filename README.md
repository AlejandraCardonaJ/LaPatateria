# 🍟 La Patatería - Sistema de Gestión de Pedidos

> Sistema de pedidos y fidelización para restaurante de papas y comida rápida

![Django](https://img.shields.io/badge/Django-6.0-green)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Descripción

**La Patatería** es un sistema de gestión de pedidos desarrollado en Django para un restaurante de papas y comida rápida. El proyecto incluye un sistema de fidelización innovador con programas como "Papa Cumpleañera", "Papa O'clock" y "Papa Lovers 4x3".

##  Características Principales

### 👤 Gestión de Usuarios
- Registro e inicio de sesión de clientes
- Perfil de usuario con historial de pedidos
- Panel de administración personalizado para el dueño

### 🛒 Carrito de Compras
- Agregar productos al carrito
- Actualizar cantidades
- Eliminar productos
- Persistencia del carrito en sesión

### 📦 Sistema de Pedidos
- Pedidos para recoger en tienda
- Pedidos a domicilio
- Estados: Pendiente → Confirmado → Preparando → En Camino → Entregado
- Cancelación de pedidos

### 🎁 Sistema de Fidelización

| Programa | Descripción |
|----------|-------------|
| **Papa Cumpleañera** | Pedido gratis hasta $80,000 en tu cumpleaños |
| **Papa O'clock** | Envío gratis de 12pm a 2pm |
| **Papa Lovers 4x3** | 4to domicilio gratis (tope $60,000) |
| **Dado Dinámico** | Recompensas aleatorias al pedir a domicilio |

### 📱 Panel de Administración
- Dashboard con estadísticas (pedidos hoy, ingresos hoy)
- Gestión de productos y categorías
- Gestión de clientes
- Seguimiento de pedidos en tiempo real
- Activar/desactivar programas de fidelización

## 🏗️ Arquitectura del Proyecto

```
LaPatateriaa/
├── app_carta/           # Gestión de carta y productos
│   ├── models.py        # Modelos: Categoria, Producto
│   ├── views.py         # Vistas: home, carta, carta_pdf
│   ├── urls.py          # Rutas de la carta
│   └── templates/       # Templates de la carta
│
├── app_fidelizacion/    # Sistema de fidelización
│   ├── models.py        # Modelos: ProgramaFidelizacion, ResultadoFidelizacion
│   ├── views.py         # Lógica de fidelización
│   └── admin.py         # Configuración admin
│
├── app_pedidos/         # Gestión de pedidos y carrito
│   ├── models.py        # Modelos: Pedido, DetallePedido
│   ├── views.py         # Vistas del carrito y pedidos
│   ├── urls.py          # Rutas de pedidos
│   └── templates/       # Templates de pedidos
│
├── app_usuarios/        # Usuarios y autenticación
│   ├── models.py        # Modelo personalizado Usuario
│   ├── views.py         # Vistas: login, registro, perfil, admin
│   ├── forms.py        # Formularios personalizados
│   ├── urls.py         # Rutas de usuarios
│   └── templates/       # Templates de usuarios
│
├── lapatateriaa/        # Configuración principal
│   ├── settings.py     # Configuración de Django
│   ├── urls.py         # URLs principales
│   └── wsgi.py         # Configuración WSGI
│
├── static/             # Archivos estáticos
│   ├── css/            # Hojas de estilo
│   └── img/            # Imágenes del sitio
│
├── media/              # Archivos subidos por usuarios
│   └── img/carta/     # Imágenes de productos
│
└── templates/          # Templates base
    └── base.html      # Template base del proyecto
```

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Django** | 6.0 | Framework web principal |
| **Python** | 3.13 | Lenguaje de programación |
| **SQLite** | - | Base de datos |
| **Bootstrap** | 5.3 | Framework CSS |
| **Font Awesome** | 6.0 | Iconos |

## 🚀 Instalación

### Prerequisites
- Python 3.13 o superior
- pip (gestor de paquetes)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd LaPatateriaa
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install django
```

4. **Ejecutar migraciones**
```bash
python manage.py migrate
```

5. **Crear superusuario (opcional)**
```bash
python manage.py createsuperuser
```

6. **Iniciar servidor de desarrollo**
```bash
python manage.py runserver
```

7. **Acceder al proyecto**
- Frontend: http://127.0.0.1:8000/
- Admin Django: http://127.0.0.1:8000/admin/

## 📖 Uso del Sistema

### Para Clientes

1. **Registrarse**: Ir a `/usuarios/registro/`
2. **Explorar carta**: Ver productos en la página principal
3. **Agregar al carrito**: Click en "Agregar" en los productos
4. **Confirmar pedido**: Ir al carrito y seleccionar tipo de entrega
5. **Verificar fidelización**: En el perfil se muestran los programas disponibles

### Para Administradores (Dueño)

1. **Acceder al panel**: Login como usuario con rol `DUENO`
2. **Panel de admin**: http://127.0.0.1:8000/usuarios/admin-panel/

#### Funciones del Panel:
- **Gestionar Carta**: Agregar/editar/eliminar productos y categorías
- **Clientes**: Ver, editar, activar/desactivar clientes
- **Pedidos**: Ver detalles, cambiar estados, cancelar pedidos
- **Fidelización**: Activar/desactivar programas de fidelización

## 🔧 Modelos de Datos

### Usuario (app_usuarios)
```
- username: Nombre de usuario
- email: Correo electrónico
- rol: CLIENTE | DUENO
- telefono: Teléfono de contacto
- fecha_nacimiento: Fecha de nacimiento (para Papa Cumpleañera)
- puntos: Puntos acumulados
- domicilios_mes: Contador de domicilios del mes
- direccion: Dirección de domicilio
```

### Producto (app_carta)
```
- nombre: Nombre del producto
- descripcion: Descripción del producto
- precio: Precio del producto
- categoria: Relación con categoría
- imagen: Imagen del producto
- disponible: Si está disponible para ordenar
- es_recomendado: Si es producto recomendado
```

### Pedido (app_pedidos)
```
- usuario: Cliente que hizo el pedido
- tipo_entrega: TIENDA | DOMICILIO
- direccion_entrega: Dirección para domicilio
- telefono_contacto: Teléfono de contacto
- total: Total del pedido
- estado: PENDIENTE | CONFIRMADO | PREPARANDO | EN_CAMINO | ENTREGADO | CANCELADO
- aplica_papa_cumpleañera: Boolean
- aplica_papa_oclock: Boolean
- aplica_4x3: Boolean
- descuento_aplicado: Monto de descuento
- costo_envio: Costo de envío
- observaciones: Notas del pedido
- fecha_pedido: Fecha de creación
```

### DetallePedido (app_pedidos)
```
- pedido: Relación con Pedido
- producto_nombre: Nombre del producto
- cantidad: Cantidad ordenada
- precio_unitario: Precio por unidad
- subtotal: Cantidad * Precio unitario
```

## 🎨 Personalización

### Agregar Productos
Desde el panel de admin del dueño:
1. Ir a "Gestionar Carta"
2. Click en "Crear Producto"
3. Llenar: nombre, descripción, precio, categoría
4. Guardar

### Modificar Programas de Fidelización
Desde el panel de admin:
1. Ir a "Fidelización"
2. Activar/desactivar programas según necesidad

## 📝 Configuración

### Configuración de Produção

En `lapatateriaa/settings.py`:

```python
# Idioma
LANGUAGE_CODE = 'es-co'

# Zona horaria (Colombia)
TIME_ZONE = 'America/Bogota'

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Autores

- **Desarrollador** - Trabajo completo

---

⭐️ Si te gusta este proyecto, no olvides darle una estrella!
