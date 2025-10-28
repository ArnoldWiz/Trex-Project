from django.forms import inlineformset_factory
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.clickjacking import xframe_options_sameorigin
from app.models import *
from django.db.models import Count
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.forms import *

# Create your views here.
#VISTAS GENERICAS
def homeGenerico(request):
    return render(request, 'genericas/home.html')

#VISTAS ADMINISTRADOR

from django.contrib.auth import authenticate, login as auth_login


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(next_url or 'homeAdmin')
        else:
            return render(request, 'administrador/login.html', {'error': 'Usuario o contraseña incorrectos.'})

    # GET
    return render(request, 'administrador/login.html')

def catalogos(request):
    return render(request, 'administrador/catalogos.html')

def homeAdmin(request):
    ordenes_prioritarias = Ordendepedido.objects.select_related('idcliente')
    return render(request, 'administrador/homeAdmin.html', {'ordenes_prioritarias': ordenes_prioritarias})

#TEMPORALES
def pedidoEspecifico(request):
    return render(request, 'administrador/catalogos/pedidoEspecifico.html')
def lotes(request):
    return render(request, 'administrador/lotes.html')

    #CRUD ORDENES
class ListaOrdenes(ListView):
    model = Ordendepedido
    template_name = 'administrador/catalogos/listaOrdenes.html'
    context_object_name = 'ordenes'
    
    def get_queryset(self):
        return Ordendepedido.objects.select_related('idcliente').annotate(pedidos_count=Count('pedido'))

class CrearOrden(CreateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'

def crear_orden_con_pedidos(request):
    PedidoFormSet = inlineformset_factory(Ordendepedido, Pedido, form=PedidoForm, extra=1, can_delete=True)
    if request.method == 'POST':
        if orden_form.is_valid():
            orden = orden_form.save(commit=False)
            formset = PedidoFormSet(request.POST, instance=orden)
            if formset.is_valid():
                orden.save()
                formset.save()
                if 'save_add_more' in request.POST:
                    return redirect('actualizarOrden', pk=orden.pk)
                return redirect('listaOrdenes')
        else:
            formset = PedidoFormSet(request.POST)
    else:
        orden_form = OrdenForm()
        formset = PedidoFormSet()

    return render(request, 'administrador/forms/formOrden.html', {
        'form': orden_form,
        'formset': formset,
        'orden': None,
    })


def actualizar_orden_con_pedidos(request, pk):
    orden = Ordendepedido.objects.get(pk=pk)
    PedidoFormSet = inlineformset_factory(Ordendepedido, Pedido, form=PedidoForm, extra=1, can_delete=True)
    if request.method == 'POST':
        orden_form = OrdenForm(request.POST, instance=orden)
        formset = PedidoFormSet(request.POST, instance=orden)
        if orden_form.is_valid() and formset.is_valid():
            orden_form.save()
            formset.save()
            if 'save_add_more' in request.POST:
                return redirect('actualizarOrden', pk=orden.pk)
            return redirect('listaOrdenes')
    else:
        orden_form = OrdenForm(instance=orden)
        formset = PedidoFormSet(instance=orden)

    return render(request, 'administrador/forms/formOrden.html', {
        'form': orden_form,
        'formset': formset,
        'orden': orden,
    })

class ActualizarOrden(UpdateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    #CRUD PEDIDOS
class ListaPedidos(ListView):
    model = Pedido
    template_name = 'administrador/catalogos/listaPedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        orden_pk = self.kwargs.get('orden_pk')
        if orden_pk:
            return Pedido.objects.filter(idordenpedido_id=orden_pk)
        return Pedido.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        orden_pk = self.kwargs.get('orden_pk')
        orden = None
        if orden_pk:
            try:
                orden = Ordendepedido.objects.get(pk=orden_pk)
            except Ordendepedido.DoesNotExist:
                orden = None
        ctx['orden'] = orden
        return ctx
    
class CrearPedido(CreateView):
    model = Pedido
    template_name = 'administrador/forms/formPedido.html'
    form_class = PedidoForm
    success_url = '/administrador/pedidos/'
    
class ActualizarPedido(UpdateView):
    model = Pedido
    template_name = 'administrador/forms/formPedido.html'
    form_class = PedidoForm
    success_url = '/administrador/pedidos/'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx
    
class ListaLotes(ListView):
    model = Lote
    template_name = 'administrador/catalogos/listaLotes.html'
    context_object_name = 'lotes'

    #CRUD EMPLEADOS
class ListaEmpleados(ListView):
    model = Empleado
    template_name = 'administrador/catalogos/listaEmpleados.html'
    context_object_name = 'empleados'

class CrearEmpleado(CreateView):
    model = Empleado
    template_name = 'administrador/forms/formEmpleado.html'
    form_class = EmpleadoForm
    success_url = '/administrador/empleados/'

class ActualizarEmpleado(UpdateView):
    model = Empleado
    template_name = 'administrador/forms/formEmpleado.html'
    form_class = EmpleadoForm
    success_url = '/administrador/empleados/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    #CRUD MAQUINAS
class ListaMaquinas(ListView):
    model = Maquina
    template_name = 'administrador/catalogos/listaMaquinas.html'
    context_object_name = 'maquinas'
    
class CrearMaquina(CreateView):
    model = Maquina
    template_name = 'administrador/forms/formMaquina.html'
    form_class = MaquinaForm
    success_url = '/administrador/maquinas/'

class ActualizarMaquina(UpdateView):
    model = Maquina
    template_name = 'administrador/forms/formMaquina.html'
    form_class = MaquinaForm
    success_url = '/administrador/maquinas/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    #CRUD MODELOS
class ListaModelos(ListView):
    model = Modelo
    template_name = 'administrador/catalogos/listaModelos.html'
    context_object_name = 'modelos'
    
class CrearModelo(CreateView):
    model = Modelo
    template_name = 'administrador/forms/formModelo.html'
    form_class = ModeloForm
    success_url = '/administrador/modelos/'

class ActualizarModelo(UpdateView):
    model = Modelo
    template_name = 'administrador/forms/formModelo.html'
    form_class = ModeloForm
    success_url = '/administrador/modelos/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx
    
    #CRUD CLIENTES
    
class ListaClientes(ListView):
    model = Cliente
    template_name = 'administrador/catalogos/listaClientes.html'
    context_object_name = 'clientes'
    
class CrearCliente(CreateView):
    model = Cliente
    template_name = 'administrador/forms/formCliente.html'
    form_class = ClienteForm
    success_url = '/administrador/clientes/'

class ActualizarCliente(UpdateView):
    model = Cliente
    template_name = 'administrador/forms/formCliente.html'
    form_class = ClienteForm
    success_url = '/administrador/clientes/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

#VISTAS EMPLEADOS

def tejido(request):
    return render(request, 'empleados/tejido.html')

def plancha(request):
    return render(request, 'empleados/plancha.html')

def corte(request):
    return render(request, 'empleados/corte.html')

def empaquetado(request):
    return render(request, 'empleados/empaquetado.html')

def reportes(request):
    return render(request, 'administrador/reportes.html')