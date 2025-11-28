from django.forms import inlineformset_factory
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from functools import wraps
from django.http import HttpResponseForbidden
from app.models import *
from django.db.models import Count
from django.db import transaction
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.utils import generate_lote_qr_image
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

    return render(request, 'administrador/login.html')


def admin_group_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/administrador/login/?next={request.path}")
        if not request.user.groups.filter(name='Administradores').exists():
            return HttpResponseForbidden('Acceso denegado: se requieren permisos de administrador')
        return view_func(request, *args, **kwargs)
    return _wrapped


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/administrador/login/'

    def test_func(self):
        return self.request.user.groups.filter(name='Administradores').exists()


def group_required(group_name):
    """Decorator: require authenticated user in given group_name."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/administrador/login/?next={request.path}")
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden(f'Acceso denegado: se requieren permisos del grupo {group_name}')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/administrador/login/'
    group_name = None

    def test_func(self):
        if not self.group_name:
            return False
        return self.request.user.groups.filter(name=self.group_name).exists()

@admin_group_required
def catalogos(request):
    return render(request, 'administrador/catalogos.html')

@admin_group_required
def homeAdmin(request):
    ordenes_prioritarias = Ordendepedido.objects.select_related('idcliente')
    return render(request, 'administrador/homeAdmin.html', {'ordenes_prioritarias': ordenes_prioritarias})

#TEMPORALES
@admin_group_required
def pedidoEspecifico(request):
    return render(request, 'administrador/catalogos/pedidoEspecifico.html')


@admin_group_required
def lotes(request):
    return render(request, 'administrador/lotes.html')

    #CRUD ORDENES
class ListaOrdenes(AdminRequiredMixin, ListView):
    model = Ordendepedido
    template_name = 'administrador/catalogos/listaOrdenes.html'
    context_object_name = 'ordenes'
    
    def get_queryset(self):
        return Ordendepedido.objects.select_related('idcliente').annotate(pedidos_count=Count('pedido'))

class CrearOrden(AdminRequiredMixin, CreateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'

class ActualizarOrden(AdminRequiredMixin, UpdateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'
    def get_object(self):
        return Ordendepedido.objects.get(pk=self.kwargs['orden_pk'])

    #CRUD PEDIDOS
class ListaPedidos(AdminRequiredMixin, ListView):
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
    
class CrearPedido(AdminRequiredMixin, CreateView):
    model = Pedido
    template_name = 'administrador/forms/formPedido.html'
    form_class = PedidoForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # pass orden_pk from URL to template for cancel link
        ctx['orden_pk'] = self.kwargs.get('orden_pk')
        # initial totallotes for display (0 by default)
        ctx['initial_totallotes'] = 0
        return ctx

    def form_valid(self, form):
        # assign the parent orden (from URL) before saving
        orden_pk = self.kwargs.get('orden_pk')
        self.object = form.save(commit=False)
        # field on model is `idordenpedido` (foreign key to Ordendepedido)
        self.object.idordenpedido_id = orden_pk
        # calculate totallotes as ceil(cantidad / 10)
        try:
            import math
            cantidad = form.cleaned_data.get('cantidad') or 0
            # use float to handle non-integer inputs, then round up
            cantidad_val = float(cantidad)
            self.object.totallotes = math.ceil(cantidad_val / 10) if cantidad_val > 0 else 0
        except Exception:
            # fallback: set 0
            self.object.totallotes = 0
        # initialize loteterminado to 0 on creation
        try:
            self.object.loteterminado = 0
        except Exception:
            pass
        # save pedido and create lotes atomically
        from django.db import IntegrityError
        try:
            with transaction.atomic():
                self.object.save()
                # create lotes: totallotes already set above
                cantidad_val = int(float(form.cleaned_data.get('cantidad') or 0))
                total_lotes = int(self.object.totallotes or 0)
                # delete any existing lotes just in case (shouldn't be any on create)
                Lote.objects.filter(idpedido=self.object).delete()
                if total_lotes > 0 and cantidad_val > 0:
                    for i in range(total_lotes):
                        if i < total_lotes - 1:
                            lote_cant = 10
                        else:
                            lote_cant = cantidad_val - 10 * (total_lotes - 1)
                        created_lote = Lote.objects.create(idpedido=self.object, cantidad=lote_cant)
                        # generate QR image for this lote (contains lote id)
                        try:
                            # fetch readable fields
                            order_num = None
                            try:
                                order_num = self.object.idordenpedido.numeroorden
                            except Exception:
                                order_num = getattr(self.object, 'idordenpedido_id', '')
                            modelo_str = ''
                            try:
                                modelo_str = self.object.idmodelo.modelo
                            except Exception:
                                modelo_str = getattr(self.object, 'idmodelo_id', '')
                            color_str = getattr(self.object, 'color', '')
                            generate_lote_qr_image(order_num, modelo_str, color_str, i+1, total_lotes, created_lote.idlote)
                        except Exception:
                            # if image generation fails, continue without stopping the transaction
                            pass
        except IntegrityError:
            # fallback: ensure object saved
            self.object.save()
        return redirect('listaPedidos', orden_pk=orden_pk)
    
class ActualizarPedido(AdminRequiredMixin, UpdateView):
    model = Pedido
    template_name = 'administrador/forms/formPedido.html'
    form_class = PedidoForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # include orden_pk so template can build cancel/back links
        if hasattr(self, 'object') and self.object:
            ctx['orden_pk'] = getattr(self.object, 'idordenpedido_id', None)
            ctx['initial_totallotes'] = getattr(self.object, 'totallotes', 0)
        else:
            ctx['initial_totallotes'] = 0
        return ctx

    def form_valid(self, form):
        # update totallotes based on cantidad
        self.object = form.save(commit=False)
        try:
            import math
            cantidad = form.cleaned_data.get('cantidad') or 0
            cantidad_val = float(cantidad)
            self.object.totallotes = math.ceil(cantidad_val / 10) if cantidad_val > 0 else 0
        except Exception:
            self.object.totallotes = 0
        # save and recreate lotes according to new cantidad
        from django.db import IntegrityError
        try:
            with transaction.atomic():
                self.object.save()
                cantidad_val = int(float(form.cleaned_data.get('cantidad') or 0))
                total_lotes = int(self.object.totallotes or 0)
                # remove existing lotes for this pedido and recreate
                Lote.objects.filter(idpedido=self.object).delete()
                if total_lotes > 0 and cantidad_val > 0:
                    for i in range(total_lotes):
                        if i < total_lotes - 1:
                            lote_cant = 10
                        else:
                            lote_cant = cantidad_val - 10 * (total_lotes - 1)
                        created_lote = Lote.objects.create(idpedido=self.object, cantidad=lote_cant)
                        # generate QR image for this lote (contains lote id)
                        try:
                            order_num = None
                            try:
                                order_num = self.object.idordenpedido.numeroorden
                            except Exception:
                                order_num = getattr(self.object, 'idordenpedido_id', '')
                            modelo_str = ''
                            try:
                                modelo_str = self.object.idmodelo.modelo
                            except Exception:
                                modelo_str = getattr(self.object, 'idmodelo_id', '')
                            color_str = getattr(self.object, 'color', '')
                            generate_lote_qr_image(order_num, modelo_str, color_str, i+1, total_lotes, created_lote.idlote)
                        except Exception:
                            pass
        except IntegrityError:
            self.object.save()
        orden_pk = getattr(self.object, 'idordenpedido_id', None)
        return redirect('listaPedidos', orden_pk=orden_pk)
    
class ListaLotes(AdminRequiredMixin, ListView):
    model = Lote
    template_name = 'administrador/catalogos/listaLotes.html'
    context_object_name = 'lotes'
    
    def get_queryset(self):
        # filter lotes by the current pedido (pk in the URL)
        pedido_pk = self.kwargs.get('pk')
        if pedido_pk:
            return Lote.objects.filter(idpedido_id=pedido_pk)
        return Lote.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['orden_pk'] = self.kwargs.get('orden_pk')
        ctx['pedido_pk'] = self.kwargs.get('pk')
        try:
            ctx['pedido'] = Pedido.objects.get(pk=self.kwargs.get('pk'))
        except Exception:
            ctx['pedido'] = None
        return ctx

    #CRUD EMPLEADOS
class ListaEmpleados(AdminRequiredMixin, ListView):
    model = Empleado
    template_name = 'administrador/catalogos/listaEmpleados.html'
    context_object_name = 'empleados'

class CrearEmpleado(AdminRequiredMixin, CreateView):
    model = Empleado
    template_name = 'administrador/forms/formEmpleado.html'
    form_class = EmpleadoForm
    success_url = '/administrador/empleados/'

class ActualizarEmpleado(AdminRequiredMixin, UpdateView):
    model = Empleado
    template_name = 'administrador/forms/formEmpleado.html'
    form_class = EmpleadoForm
    success_url = '/administrador/empleados/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    #CRUD MAQUINAS
class ListaMaquinas(AdminRequiredMixin, ListView):
    model = Maquina
    template_name = 'administrador/catalogos/listaMaquinas.html'
    context_object_name = 'maquinas'
    
class CrearMaquina(AdminRequiredMixin, CreateView):
    model = Maquina
    template_name = 'administrador/forms/formMaquina.html'
    form_class = MaquinaForm
    success_url = '/administrador/maquinas/'

class ActualizarMaquina(AdminRequiredMixin, UpdateView):
    model = Maquina
    template_name = 'administrador/forms/formMaquina.html'
    form_class = MaquinaForm
    success_url = '/administrador/maquinas/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    #CRUD MODELOS
class ListaModelos(AdminRequiredMixin, ListView):
    model = Modelo
    template_name = 'administrador/catalogos/listaModelos.html'
    context_object_name = 'modelos'
    
class CrearModelo(AdminRequiredMixin, CreateView):
    model = Modelo
    template_name = 'administrador/forms/formModelo.html'
    form_class = ModeloForm
    success_url = '/administrador/modelos/'

class ActualizarModelo(AdminRequiredMixin, UpdateView):
    model = Modelo
    template_name = 'administrador/forms/formModelo.html'
    form_class = ModeloForm
    success_url = '/administrador/modelos/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx
    
    #CRUD CLIENTES
    
class ListaClientes(AdminRequiredMixin, ListView):
    model = Cliente
    template_name = 'administrador/catalogos/listaClientes.html'
    context_object_name = 'clientes'
    
class CrearCliente(AdminRequiredMixin, CreateView):
    model = Cliente
    template_name = 'administrador/forms/formCliente.html'
    form_class = ClienteForm
    success_url = '/administrador/clientes/'

class ActualizarCliente(AdminRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'administrador/forms/formCliente.html'
    form_class = ClienteForm
    success_url = '/administrador/clientes/'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

#VISTAS EMPLEADOS

@group_required('Tejido')
def tejido(request):
    return render(request, 'empleados/tejido.html')


@group_required('Plancha')
def plancha(request):
    return render(request, 'empleados/plancha.html')


@group_required('Corte')
def corte(request):
    return render(request, 'empleados/corte.html')


@group_required('Empaquetado')
def empaquetado(request):
    return render(request, 'empleados/empaquetado.html')

def reportes(request):
    return render(request, 'administrador/reportes.html')