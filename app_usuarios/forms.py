from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroForm(UserCreationForm):
    """Formulario personalizado para el registro de clientes con todos los campos requeridos"""
    
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    telefono = forms.CharField(
        required=True,
        label='Teléfono',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '3001234567'
        })
    )
    
    fecha_nacimiento = forms.DateField(
        required=True,
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    direccion = forms.CharField(
        required=True,
        label='Dirección de domicilio',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Carrera 00 # 00-00'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'telefono', 'fecha_nacimiento', 'direccion')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data['telefono']
        user.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        user.direccion = self.cleaned_data['direccion']
        user.rol = 'CLIENTE'  # Por defecto, todos los registros son clientes
        
        if commit:
            user.save()
        
        return user
