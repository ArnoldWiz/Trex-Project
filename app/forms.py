from django import forms
from app.models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellidos', 'area', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':'Nombre'}),
            'apellidos': forms.TextInput(attrs={'class':'form-control','placeholder':'Apellidos'}),
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')]),
        }