import sys
from django.core.management import call_command
from django.apps import apps

def main():
    # Verificar si ya hay categorías
    try:
        Categoria = apps.get_model('app_carta', 'Categoria')
        if Categoria.objects.exists():
            print("✅ Ya existen categorías. No se cargarán datos de nuevo.")
            mostrar_conteos()
            return
    except LookupError:
        print("⚠️ Modelo Categoria no encontrado. Asegúrate de que las migraciones estén aplicadas.")
        return

    # Cargar solo datos de la carta
    print("📦 Cargando categorías y productos...")
    try:
        call_command('loaddata', 'app_carta.json', verbosity=1)
    except Exception as e:
        print(f"❌ Error cargando app_carta.json: {e}")

    # Intentar cargar fidelización, pero no detener el proceso si falla
    print("📦 Intentando cargar programas de fidelización...")
    try:
        call_command('loaddata', 'app_fidelizacion.json', verbosity=1)
    except Exception as e:
        print(f"⚠️ No se pudo cargar app_fidelizacion.json: {e}. Se continuará sin datos de fidelización.")

    mostrar_conteos()

def mostrar_conteos():
    print("\n📊 Conteo de registros en la base de datos:")
    try:
        Categoria = apps.get_model('app_carta', 'Categoria')
        print(f"  - Categorías: {Categoria.objects.count()}")
    except LookupError:
        print("  - Categorías: modelo no encontrado")

    try:
        Producto = apps.get_model('app_carta', 'Producto')
        print(f"  - Productos: {Producto.objects.count()}")
    except LookupError:
        print("  - Productos: modelo no encontrado")

if __name__ == "__main__":
    main()