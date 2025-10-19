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

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':'Nombre'}),
            'contacto': forms.TextInput(attrs={'class':'form-control','placeholder':'Contacto'}),
        }

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Ordendepedido
        fields = ['idcliente', 'fechainicio', 'fechafin']
        widgets = {
            'idcliente': forms.Select(attrs={'class':'form-control'}, 
                                      choices=[(cliente.idcliente, cliente.nombre) for cliente in Cliente.objects.all()]),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechafin': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['idordenpedido', 'idmodelo', 'talla', 'cantidad', 'color', 'totallotes', 'loteterminado',
                  'fechainicio', 'fechafin', 'fechaprevista']
        widgets = {
            'idordenpedido': forms.Select(attrs={'class':'form-control'}),
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