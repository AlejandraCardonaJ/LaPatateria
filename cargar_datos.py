import sys
import os
from django.core.management import call_command
from django.apps import apps
from django.db import connection

def main():
    print("🚀 INICIANDO SCRIPT DE CARGA DE DATOS")
    
    # Verificar si ya hay categorías
    try:
        Categoria = apps.get_model('app_carta', 'Categoria')
        categoria_count = Categoria.objects.count()
        print(f"📊 Categorías existentes: {categoria_count}")
        
        if categoria_count > 0:
            print("✅ Ya existen categorías. No se cargarán datos de nuevo.")
            # Mostrar todas las categorías para confirmar
            for cat in Categoria.objects.all():
                print(f"   - {cat.nombre}")
            return
    except LookupError:
        print("⚠️ Modelo Categoria no encontrado. Asegúrate de que las migraciones estén aplicadas.")
        return

    # Listar archivos JSON disponibles
    json_files = ['app_carta.json', 'app_fidelizacion.json']
    for f in json_files:
        if os.path.exists(f):
            print(f"📄 Archivo encontrado: {f} (tamaño: {os.path.getsize(f)} bytes)")
        else:
            print(f"❌ Archivo NO encontrado: {f}")
            return

    # Cargar datos
    print("📦 Cargando datos...")
    try:
        call_command('loaddata', 'app_carta.json', verbosity=2)
        call_command('loaddata', 'app_fidelizacion.json', verbosity=2)
        print("✅ Datos cargados exitosamente.")
    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        import traceback
        traceback.print_exc()
        return

    # Mostrar conteos después de cargar
    print("\n📊 CONTEOS FINALES:")
    try:
        print(f"  - Categorías: {Categoria.objects.count()}")
        Producto = apps.get_model('app_carta', 'Producto')
        print(f"  - Productos: {Producto.objects.count()}")
        Programa = apps.get_model('app_fidelizacion', 'ProgramaFidelizacion')
        print(f"  - Programas: {Programa.objects.count()}")
    except LookupError as e:
        print(f"  - Error al obtener conteos: {e}")

if __name__ == "__main__":
    main()