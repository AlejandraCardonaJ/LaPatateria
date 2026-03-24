# #!/usr/bin/env bash
# set -o errexit

# pip install -r requirements.txt

# python manage.py collectstatic --no-input

# python manage.py migrate

# python manage.py createsuperuser --no-input || true

# # Carga directa de datos de la carta
# # echo "=== Cargando datos de la carta ==="
# # python manage.py loaddata app_carta.json --verbosity=2

# # echo "=== Proceso de construcción completado ==="

# # Cargar datos solo si la tabla de categorías está vacía
# if python manage.py shell -c "from app_carta.models import Categoria; exit(not Categoria.objects.exists())"; then
#     echo "=== Ya hay categorías, no se cargarán datos ==="
# else
#     echo "=== Cargando datos de la carta ==="
#     python manage.py loaddata app_carta.json --verbosity=2
# fi

# echo "=== Proceso de construcción completado ==="

#!/usr/bin/env bash
set -o errexit

echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo "=== Verificando instalación de django-storages ==="
python -c "import storages; print('✅ django-storages instalado correctamente')" || exit 1

echo "=== Recolectando archivos estáticos ==="
python manage.py collectstatic --no-input

echo "=== Aplicando migraciones ==="
python manage.py migrate

echo "=== Creando superusuario si no existe ==="
python manage.py createsuperuser --no-input || true

echo "=== Cargando datos de la carta (solo si la tabla está vacía) ==="
if python manage.py shell -c "from app_carta.models import Categoria; exit(not Categoria.objects.exists())"; then
    echo "✅ Ya hay categorías, no se cargan datos."
else
    echo "📦 Cargando datos iniciales..."
    python manage.py loaddata app_carta.json --verbosity=2
fi

echo "=== Verificando configuración de S3 (opcional) ==="
python -c "from django.conf import settings; print(f'DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE if not settings.DEBUG else "local"}')"

echo "=== Construcción completada ==="