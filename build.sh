#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py createsuperuser --no-input || true

# python manage.py shell < cargar_datos.py

if [ "$FORCE_LOAD_DATA" = "true" ]; then
    echo "Forzando carga de datos adicional..."
    python manage.py loaddata app_carta.json --verbosity=2
    python manage.py loaddata app_fidelizacion.json --verbosity=2
fi