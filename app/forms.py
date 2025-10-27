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
        fields = ['idcliente', 'fechainicio', 'fechafin']
        widgets = {
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechafin': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        # When using an inline formset the relation to the parent (idordenpedido)
        # is provided by the formset instance, so exclude it here to avoid
        # rendering it as a selectable field in each pedido form.
        fields = ['idmodelo', 'talla', 'cantidad', 'color', 'totallotes', 'loteterminado',
                  'fechainicio', 'fechafin', 'fechaprevista']
        widgets = {
            'idmodelo': forms.Select(attrs={'class':'form-control'}),
            'talla': forms.NumberInput(attrs={'class':'form-control','placeholder':'Talla'}),
            'cantidad': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad'}),
            'color': forms.TextInput(attrs={'class':'form-control','placeholder':'Color'}),
            'totallotes': forms.NumberInput(attrs={'class':'form-control','placeholder':'Total de Lotes'}),
            'loteterminado': forms.NumberInput(attrs={'class':'form-control','placeholder':'Lote Terminado'}),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechafin': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechaprevista': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }