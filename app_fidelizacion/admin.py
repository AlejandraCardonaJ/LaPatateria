from django.contrib import admin
from .models import ProgramaFidelizacion, ResultadoFidelizacion


@admin.register(ProgramaFidelizacion)
class ProgramaFidelizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'icono', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


@admin.register(ResultadoFidelizacion)
class ResultadoFidelizacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'programa', 'resultado', 'fecha')
    list_filter = ('programa', 'fecha')
    search_fields = ('usuario__username', 'recompensa')
    date_hierarchy = 'fecha'
