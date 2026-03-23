import sys
from django.core.management import call_command
from django.apps import apps

def main():
    # 1. Verificar si ya hay datos (usando la existencia de alguna categoría)
    try:
        Categoria = apps.get_model('app_carta', 'Categoria')
        if Categoria.objects.exists():
            print("✅ Ya existen categorías. No se cargarán datos de nuevo.")
            return
    except LookupError:
        print("⚠️ El modelo Categoria no se encontró. Asegúrate de que las migraciones estén aplicadas.")
        return

    # 2. Cargar datos de la carta (categorías y productos)
    print("📦 Cargando categorías y productos...")
    try:
        call_command('loaddata', 'app_carta.json', verbosity=1)
    except Exception as e:
        print(f"❌ Error cargando app_carta.json: {e}")

    # 3. Cargar datos de fidelización (programas)
    print("📦 Cargando programas de fidelización...")
    try:
        call_command('loaddata', 'app_fidelizacion.json', verbosity=1)
    except Exception as e:
        print(f"❌ Error cargando app_fidelizacion.json: {e}")

    print("✅ Proceso de carga finalizado.")

if __name__ == "__main__":
    main()