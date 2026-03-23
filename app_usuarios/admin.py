from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


# Personalizamos la vista del usuario en el panel administrativo
class UsuarioAdmin(UserAdmin):
    # Campos que se verán en la lista principal
    list_display = ('username', 'email', 'rol', 'puntos', 'is_staff', 'is_superuser')
    
    # Filtros laterales para encontrar usuarios rápido
    list_filter = ('rol', 'is_staff', 'is_superuser')
    
    # Agregamos nuestros campos personalizados a los formularios de edición
    fieldsets = UserAdmin.fieldsets + (
        ('Información de La Patatería', {'fields': ('rol', 'puntos', 'telefono', 'fecha_nacimiento', 'direccion')}),
    )
    
    # Campos para cuando se crea un usuario nuevo
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de La Patatería', {'fields': ('rol', 'puntos', 'telefono', 'fecha_nacimiento', 'direccion')}),
    )
    
    def get_queryset(self, request):
        """
        Restringe que el administrador (no superusuario) no pueda ver ni editar al superusuario.
        Solo el superusuario puede ver y gestionar a otros superusuarios.
        """
        qs = super().get_queryset(request)
        
        # Si es superusuario, puede ver todos los usuarios
        if request.user.is_superuser:
            return qs
        
        # Si es staff (administrador) pero NO superusuario, ocultamos los superusuarios
        return qs.filter(is_superuser=False)
    
    def has_view_permission(self, request, obj=None):
        """
        Si es superusuario, puede ver todo.
        Si es staff pero no superusuario, puede ver usuarios normales.
        """
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_view_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """
        Si es superusuario, puede editar todo.
        Si es staff pero no superusuario, no puede editar superusuarios.
        """
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Si es superusuario, puede eliminar todo.
        Si es staff pero no superusuario, no puede eliminar superusuarios.
        """
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


# Registramos el modelo con la configuración personalizada
admin.site.register(Usuario, UsuarioAdmin)
