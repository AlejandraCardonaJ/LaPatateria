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