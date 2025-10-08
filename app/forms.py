from django import forms
from app.models import Empleado, Maquina, Modelo

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

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = ['area', 'numero']
        widgets = {
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'numero': forms.TextInput(attrs={'class':'form-control','placeholder':'Número'}),
        }
        
class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['folio', 'modelo', 'cantidadhilo']
        widgets = {
            'folio': forms.TextInput(attrs={'class':'form-control','placeholder':'Folio'}),
            'modelo': forms.TextInput(attrs={'class':'form-control','placeholder':'Modelo'}),
            'cantidadhilo': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad de Hilo'}),
        }