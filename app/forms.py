from django import forms
from app.models import *

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellidos', 'area', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':'Nombre'}),
            'apellidos': forms.TextInput(attrs={'class':'form-control','placeholder':'Apellidos'}),
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = ['area', 'numero', 'estatus']
        widgets = {
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'numero': forms.TextInput(attrs={'class':'form-control','placeholder':'Número'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }
        
class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['folio', 'modelo', 'cantidadhilo', 'estatus']
        widgets = {
            'folio': forms.TextInput(attrs={'class':'form-control','placeholder':'Folio'}),
            'modelo': forms.TextInput(attrs={'class':'form-control','placeholder':'Modelo'}),
            'cantidadhilo': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad de Hilo'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'contacto', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':'Nombre'}),
            'contacto': forms.TextInput(attrs={'class':'form-control','placeholder':'Contacto'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

class OrdenForm(forms.ModelForm):
    idcliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=forms.Select(attrs={'class':'form-control'}),
        empty_label="Selecciona un cliente",
        label="Cliente"
    )

    class Meta:
        model = Ordendepedido
        fields = ['numeroorden','idcliente', 'fechainicio', 'fechafin']
        widgets = {
            'numeroorden': forms.TextInput(attrs={'class':'form-control','placeholder':'Número de Orden'}),
            'idcliente': forms.Select(attrs={'class':'form-control'}),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechafin': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }

class PedidoForm(forms.ModelForm):
    # show Modelo.folio in the select instead of the default __str__
    class ModeloChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.folio

    idmodelo = ModeloChoiceField(queryset=Modelo.objects.all(),
                                 widget=forms.Select(attrs={'class':'form-control'}),
                                 label='Modelo')

    class Meta:
        model = Pedido
        # omit totallotes from the editable fields — it's computed automatically
        fields = ['idmodelo', 'talla', 'cantidad', 'color', 'fechainicio', 'fechaprevista']
        widgets = {
            'talla': forms.NumberInput(attrs={'class':'form-control','placeholder':'Talla'}),
            'cantidad': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad'}),
            'color': forms.TextInput(attrs={'class':'form-control','placeholder':'Color'}),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechaprevista': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }