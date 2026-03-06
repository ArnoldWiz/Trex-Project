from django import forms
from app.models import *


class CatalogoEstatusCreateMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_create = not (getattr(self.instance, 'pk', None))

        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['pill_select'] = '1'

        if is_create and 'estatus' in self.fields:
            self.fields['estatus'].required = False
            self.initial.setdefault('estatus', 1)

    def clean_estatus(self):
        valor = self.cleaned_data.get('estatus')
        return 1 if valor in (None, '') else valor

class EmpleadoForm(CatalogoEstatusCreateMixin, forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellidos', 'area', 'estatus']
        labels = {
            'nombre': 'Nombre',
            'apellidos': 'Apellidos',
            'area': 'Área',
            'estatus': 'Estatus',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':'Nombre'}),
            'apellidos': forms.TextInput(attrs={'class':'form-control','placeholder':'Apellidos'}),
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

class MaquinaForm(CatalogoEstatusCreateMixin, forms.ModelForm):
    class Meta:
        model = Maquina
        fields = ['area', 'numero', 'estatus']
        labels = {
            'area': 'Área',
            'numero': 'Número',
            'estatus': 'Estatus',
        }
        widgets = {
            'area': forms.Select(attrs={'class':'form-control'}, choices=[('Corte', 'Corte'), ('Tejido', 'Tejido'), ('Plancha', 'Plancha')]),
            'numero': forms.TextInput(attrs={'class':'form-control','placeholder':'Número'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }
        
class ModeloForm(CatalogoEstatusCreateMixin, forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['folio', 'modelo', 'cantidadhilo', 'estatus']
        labels = {
            'folio': 'Folio',
            'modelo': 'Modelo',
            'cantidadhilo': 'Cantidad de Hilo',
            'estatus': 'Estatus',
        }
        widgets = {
            'folio': forms.TextInput(attrs={'class':'form-control','placeholder':'Folio'}),
            'modelo': forms.TextInput(attrs={'class':'form-control','placeholder':'Modelo'}),
            'cantidadhilo': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad de Hilo'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

class ClienteForm(CatalogoEstatusCreateMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'contacto', 'estatus']
        labels = {
            'nombre': 'Nombre',
            'contacto': 'Contacto',
            'estatus': 'Estatus',
        }
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
        fields = ['numeroorden','idcliente', 'fechainicio', 'fechaprevista']
        labels = {
            'numeroorden': 'Número de Orden',
            'idcliente': 'Cliente',
            'fechainicio': 'Fecha de Inicio',
            'fechaprevista': 'Fecha Prevista',
        }
        widgets = {
            'numeroorden': forms.TextInput(attrs={'class':'form-control','placeholder':'Número de Orden'}),
            'idcliente': forms.Select(attrs={'class':'form-control'}),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechaprevista': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
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
        labels = {
            'idmodelo': 'Modelo',
            'talla': 'Talla',
            'cantidad': 'Cantidad',
            'color': 'Color',
            'fechainicio': 'Fecha de Inicio',
            'fechaprevista': 'Fecha Prevista',
        }
        widgets = {
            'talla': forms.NumberInput(attrs={'class':'form-control','placeholder':'Talla'}),
            'cantidad': forms.NumberInput(attrs={'class':'form-control','placeholder':'Cantidad'}),
            'color': forms.TextInput(attrs={'class':'form-control','placeholder':'Color'}),
            'fechainicio': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'fechaprevista': forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
        }

class LoteEmpleadoForm(forms.Form):
    """Form para registrar un empleado y máquina en un lote mediante QR"""
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.none(),
        widget=forms.Select(attrs={'class':'form-control'}),
        empty_label="Selecciona un empleado",
        label="Empleado"
    )
    maquina = forms.ModelChoiceField(
        queryset=Maquina.objects.none(),
        widget=forms.Select(attrs={'class':'form-control'}),
        empty_label="Selecciona una máquina",
        label="Máquina"
    )
    qr_image = forms.ImageField(
        widget=forms.FileInput(attrs={'class':'form-control', 'accept':'image/*'}),
        label="Imagen QR del Lote"
    )
    plancha_etapa = forms.ChoiceField(
        choices=[('pre', 'Pre-Plancha'), ('post', 'Post-Plancha')],
        required=False,
        label="Etapa de Plancha",
        widget=forms.RadioSelect
    )
    
    def __init__(self, *args, **kwargs):
        area = kwargs.pop('area', None)
        super().__init__(*args, **kwargs)
        
        if area:
            # Filtrar empleados y máquinas por área
            self.fields['empleado'].queryset = Empleado.objects.filter(estatus=1)
            if area.lower() == 'empaquetado':
                self.fields['maquina'].queryset = Maquina.objects.filter(estatus=1)
                self.fields['maquina'].required = False
                self.fields['maquina'].label = 'Máquina (opcional)'
            else:
                self.fields['maquina'].queryset = Maquina.objects.filter(area=area, estatus=1)
                self.fields['maquina'].required = True

        if area and area.lower() == 'plancha':
            self.fields['plancha_etapa'].required = True
        else:
            self.fields.pop('plancha_etapa', None)