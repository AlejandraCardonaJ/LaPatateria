from django.shortcuts import render
from .models import Categoria, Producto
from django.http import HttpResponse



def home(request):
    """
    Vista de la página principal (Home).
    Muestra las categorías y productos destacados.
    """
    categorias = Categoria.objects.filter(activa=True).order_by('orden', 'nombre')
    # Obtener productos recomendados o todos los disponibles
    productos_destacados = Producto.objects.filter(disponible=True).select_related('categoria')[:10]
    
    # Obtener información de fidelización si el usuario está autenticado
    fidelizacion = None
    total_items_carrito = 0
    if request.user.is_authenticated:
        try:
            from app_fidelizacion.views import verificar_fidelizacion
            fidelizacion = verificar_fidelizacion(request.user)
        except:
            pass
        
        # Contar total de items en el carrito
        carrito = request.session.get('carrito', {})
        total_items_carrito = sum(carrito.values()) if carrito else 0
    
    return render(request, 'carta/index.html', {
        'categorias': categorias,
        'productos_destacados': productos_destacados,
        'fidelizacion': fidelizacion,
        'total_items_carrito': total_items_carrito
    })


def carta(request):
    """
    Muestra la carta completa con todos los productos.
    """
    categorias = Categoria.objects.filter(activa=True).prefetch_related('productos').order_by('orden', 'nombre')
    
    # Contar total de items en el carrito
    total_items_carrito = 0
    if request.user.is_authenticated:
        carrito = request.session.get('carrito', {})
        total_items_carrito = sum(carrito.values()) if carrito else 0
    
    return render(request, 'carta/carta.html', {
        'categorias': categorias,
        'total_items_carrito': total_items_carrito
    })


def carta_pdf(request):
    """
    Genera la carta en formato PDF usando WeasyPrint.
    """
    from weasyprint import HTML
    from django.template.loader import render_to_string
    
    categorias = Categoria.objects.filter(activa=True).prefetch_related('productos').order_by('orden', 'nombre')
    
    # Renderizar el template HTML
    html_string = render_to_string('carta/pdf_template.html', {
        'categorias': categorias
    })
    
    # Generar PDF
    pdf_file = HTML(string=html_string).write_pdf()
    
    # Devolver respuesta
    from django.http import HttpResponse
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Menú_La_Patateria.pdf"'
    return response
