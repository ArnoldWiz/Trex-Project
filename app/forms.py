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
        fields = ['folio', 'modelo', 'estatus']
        labels = {
            'folio': 'Folio',
            'modelo': 'Modelo',
            'estatus': 'Estatus',
        }
        widgets = {
            'folio': forms.TextInput(attrs={'class':'form-control','placeholder':'Folio'}),
            'modelo': forms.TextInput(attrs={'class':'form-control','placeholder':'Modelo'}),
            'estatus': forms.Select(attrs={'class':'form-control'}, choices=[(1, 'Activo'), (0, 'Inactivo')]),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if getattr(instance, 'cantidadhilo', None) in (None, ''):
            instance.cantidadhilo = 0
        if commit:
            instance.save()
        return instance

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
    division_lote = forms.IntegerField(
        required=True,
        min_value=1,
        initial=10,
        label='Dividir lotes entre',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tamaño de lote (ej. 10)'})
    )
    redondear_lote = forms.BooleanField(
        required=False,
        initial=True,
        label='Redondear residuo (1-4 suma, 5-9 nuevo lote)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

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
    """Form para registrar un empleado y maquina en un lote mediante lector QR"""
    empleado_qr = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
        label='QR Empleado'
    )
    lote_qr = forms.CharField(
        required=True,
        widget=forms.HiddenInput(),
        label='QR Lote'
    )
    maquina = forms.ModelChoiceField(
        queryset=Maquina.objects.none(),
        widget=forms.Select(attrs={'class':'form-control'}),
        empty_label="Selecciona una máquina",
        label="Máquina"
    )
    empleado_pre = forms.ModelChoiceField(
        queryset=Empleado.objects.none(),
        widget=forms.Select(attrs={'class':'form-control'}),
        empty_label="Selecciona empleado para Pre-Plancha",
        label="Empleado Pre-Plancha",
        required=False,
    )
    
    def __init__(self, *args, **kwargs):
        area = kwargs.pop('area', None)
        super().__init__(*args, **kwargs)
        
        if area:
            if area.lower() == 'empaquetado':
                self.fields['maquina'].queryset = Maquina.objects.filter(estatus=1)
                self.fields['maquina'].required = False
                self.fields['maquina'].label = 'Máquina (opcional)'
            else:
                self.fields['maquina'].queryset = Maquina.objects.filter(area=area, estatus=1)
                self.fields['maquina'].required = True

        if area and area.lower() == 'plancha':
            self.fields['empleado_pre'].queryset = Empleado.objects.filter(estatus=1).order_by('idempleado')
            self.fields['empleado_pre'].required = True
        else:
            self.fields.pop('empleado_pre', None)