#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py createsuperuser --no-input || true

# Carga directa de datos de la carta
# echo "=== Cargando datos de la carta ==="
# python manage.py loaddata app_carta.json --verbosity=2

# echo "=== Proceso de construcción completado ==="

# Cargar datos solo si la tabla de categorías está vacía
if python manage.py shell -c "from app_carta.models import Categoria; exit(not Categoria.objects.exists())"; then
    echo "=== Ya hay categorías, no se cargarán datos ==="
else
    echo "=== Cargando datos de la carta ==="
    python manage.py loaddata app_carta.json --verbosity=2
fi

echo "=== Proceso de construcción completado ==="