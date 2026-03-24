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

echo "=== Construcción completada ==="

echo "=== Prueba de escritura en S3 ==="
python manage.py shell -c "
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
try:
    path = default_storage.save('test.txt', ContentFile(b'Prueba de escritura'))
    print(f'✅ Archivo guardado en: {path}')
    print(f'URL: {default_storage.url(path)}')
except Exception as e:
    print(f'❌ Error: {e}')
"