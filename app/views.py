from django.forms import inlineformset_factory
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.clickjacking import xframe_options_sameorigin
import os
import base64
from django.utils import timezone
from app.models import *
from django.db.models import Count, Q, Max
from django.db import transaction
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.utils import (
    generate_lote_qr_image,
    generate_empleado_qr_image,
    delete_lote_qr_images,
    parse_qr_id_for_prefix,
    delete_orden_qr_folder,
    get_pedido_qr_folder,
)
from app.forms import *
from app.temp_seed_data import insertar_datos_prueba_temporales

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
    ordenes_prioritarias = (
        Ordendepedido.objects
        .select_related('idcliente')
        .filter(fechafin__isnull=True)
        .annotate(
            total_pedidos=Count('pedido'),
            pedidos_completados=Count('pedido', filter=Q(pedido__fechafin__isnull=False)),
        )
    )
    return render(request, 'administrador/homeAdmin.html', {'ordenes_prioritarias': ordenes_prioritarias})

#TEMPORALES
def pedidoEspecifico(request):
    return render(request, 'administrador/catalogos/pedidoEspecifico.html')
def lotes(request):
    return render(request, 'administrador/lotes.html')


def _calcular_lotes_por_cantidad(cantidad_total):
    cantidad_total = int(cantidad_total or 0)
    if cantidad_total <= 0:
        return []

    lotes = []
    lotes_base = cantidad_total // 10
    residuo = cantidad_total % 10

    if lotes_base == 0:
        return [cantidad_total]

    lotes.extend([10] * lotes_base)

    if residuo == 0:
        return lotes

    if 1 <= residuo <= 4:
        lotes[-1] += residuo
    else:
        lotes.append(residuo)

    return lotes


def _actualizar_fecha_fin_orden(orden_id):
    try:
        orden = Ordendepedido.objects.get(pk=orden_id)
    except Ordendepedido.DoesNotExist:
        return

    pedidos_qs = Pedido.objects.filter(idordenpedido_id=orden_id)

    if not pedidos_qs.exists() or pedidos_qs.filter(fechafin__isnull=True).exists():
        if orden.fechafin is not None:
            orden.fechafin = None
            orden.save(update_fields=['fechafin'])
        return

    fecha_fin_orden = pedidos_qs.aggregate(ultima_fecha_fin=Max('fechafin')).get('ultima_fecha_fin')
    if orden.fechafin != fecha_fin_orden:
        orden.fechafin = fecha_fin_orden
        orden.save(update_fields=['fechafin'])

    #CRUD ORDENES
class ListaOrdenes(ListView):
    model = Ordendepedido
    template_name = 'administrador/catalogos/listaOrdenes.html'
    context_object_name = 'ordenes'
    
    def get_queryset(self):
        return (
            Ordendepedido.objects
            .filter(fechafin__isnull=True)
            .select_related('idcliente')
            .annotate(
                pedidos_count=Count('pedido'),
                total_pedidos=Count('pedido'),
                pedidos_completados=Count('pedido', filter=Q(pedido__fechafin__isnull=False)),
            )
        )


class ListaOrdenesTerminadas(ListView):
    """Muestra las órdenes que ya tienen fecha de fin (terminadas)."""
    model = Ordendepedido
    template_name = 'administrador/catalogos/listaOrdenesTerminadas.html'
    context_object_name = 'ordenes'

    def get_queryset(self):
        # filtrar solo órdenes con fecha de fin no nula
        return (
            Ordendepedido.objects
            .filter(fechafin__isnull=False)
            .select_related('idcliente')
            .annotate(pedidos_count=Count('pedido'))
        )

class CrearOrden(CreateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'

class ActualizarOrden(UpdateView):
    model = Ordendepedido
    template_name = 'administrador/forms/formOrden.html'
    form_class = OrdenForm
    success_url = '/administrador/ordenes'
    def get_object(self):
        return Ordendepedido.objects.get(pk=self.kwargs['orden_pk'])

class EliminarOrden(DeleteView):
    model = Ordendepedido
    template_name = 'administrador/forms/confirmarEliminar.html'
    success_url = '/administrador/ordenes'
    
    def get_object(self):
        return Ordendepedido.objects.get(pk=self.kwargs['orden_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = 'orden'
        context['numeroorden'] = self.object.numeroorden
        context['cliente'] = self.object.idcliente.nombre
        context['fechainicio'] = self.object.fechainicio
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        order_num = self.object.numeroorden
        print(f"\n=== Iniciando eliminación de Orden: {order_num} ===")
        
        # Obtener todos los pedidos antes de eliminar (para limpiar QR)
        pedidos = Pedido.objects.filter(idordenpedido=self.object)
        print(f"Pedidos a eliminar: {pedidos.count()}")
        try:
            for pedido in pedidos:
                try:
                    # Eliminar carpeta QR de cada pedido
                    color_str = pedido.color
                    folio_str = pedido.idmodelo.folio
                    print(f"Eliminando QR del pedido {pedido.idpedido} - Folio: {folio_str}, Color: {color_str}")
                    delete_lote_qr_images(order_num, color_str, folio_str)
                except Exception as e:
                    print(f"Error eliminando carpeta QR del pedido {pedido.idpedido}: {e}")
        except Exception as e:
            print(f"Error procesando carpetas QR: {e}")
        
        # Eliminar carpeta QR de la orden
        print(f"Eliminando carpeta QR de la orden: {order_num}")
        try:
            delete_orden_qr_folder(order_num)
        except Exception as e:
            print(f"Error eliminando carpeta QR de orden: {e}")
        
        # Django y la base de datos se encargarán del resto con CASCADE
        try:
            print(f"Eliminando registro de orden de la base de datos...")
            result = super().delete(request, *args, **kwargs)
            print(f"Orden eliminada exitosamente")
            print(f"=== Eliminación completada ===\n")
            return result
        except Exception as e:
            print(f"Error eliminando orden: {e}")
            import traceback
            traceback.print_exc()
            raise

    #CRUD PEDIDOS
class ListaPedidos(ListView):
    model = Pedido
    template_name = 'administrador/catalogos/listaPedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        orden_pk = self.kwargs.get('orden_pk')
        if orden_pk:
            return (
                Pedido.objects
                .filter(idordenpedido_id=orden_pk)
                .annotate(
                    lotes_terminados_calc=Count(
                        'lote',
                        filter=(
                            Q(lote__idemptejido__isnull=False)
                            & Q(lote__idempplanchapre__isnull=False)
                            & Q(lote__idempplanchapost__isnull=False)
                            & Q(lote__idempcorte__isnull=False)
                        ),
                    )
                )
            )
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
        # calculate totallotes by business rule:
        # residuo 1-4 se queda en lote anterior, residuo 5-9 crea lote nuevo
        try:
            cantidad = form.cleaned_data.get('cantidad') or 0
            cantidad_val = int(float(cantidad))
            lotes_por_cantidad = _calcular_lotes_por_cantidad(cantidad_val)
            self.object.totallotes = len(lotes_por_cantidad)
        except Exception:
            # fallback: set 0
            self.object.totallotes = 0
            lotes_por_cantidad = []
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
                total_lotes = len(lotes_por_cantidad)
                # delete any existing lotes just in case (shouldn't be any on create)
                Lote.objects.filter(idpedido=self.object).delete()
                if total_lotes > 0:
                    for i, lote_cant in enumerate(lotes_por_cantidad):
                        created_lote = Lote.objects.create(idpedido=self.object, cantidad=lote_cant)
                        # generate QR image for this lote (contains lote id)
                        try:
                            generate_lote_qr_image(created_lote, i+1, total_lotes)
                        except Exception:
                            # if image generation fails, continue without stopping the transaction
                            pass
        except IntegrityError:
            # fallback: ensure object saved
            self.object.save()

        _actualizar_fecha_fin_orden(orden_pk)
        return redirect('listaPedidos', orden_pk=orden_pk)
    
class ActualizarPedido(UpdateView):
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
        # Obtener valores originales ANTES de actualizar
        original_pedido = Pedido.objects.get(pk=self.object.pk)
        try:
            original_order_num = original_pedido.idordenpedido.numeroorden
        except Exception:
            original_order_num = getattr(original_pedido, 'idordenpedido_id', '')
        try:
            original_folio = original_pedido.idmodelo.folio
        except Exception:
            original_folio = getattr(original_pedido, 'idmodelo_id', '')
        original_color = getattr(original_pedido, 'color', '')
        
        # update totallotes based on cantidad
        self.object = form.save(commit=False)
        try:
            cantidad = form.cleaned_data.get('cantidad') or 0
            cantidad_val = int(float(cantidad))
            lotes_por_cantidad = _calcular_lotes_por_cantidad(cantidad_val)
            self.object.totallotes = len(lotes_por_cantidad)
        except Exception:
            self.object.totallotes = 0
            lotes_por_cantidad = []
        # save and recreate lotes according to new cantidad
        from django.db import IntegrityError
        try:
            with transaction.atomic():
                # delete existing QR images using ORIGINAL values before saving changes
                try:
                    delete_lote_qr_images(original_order_num, original_color, original_folio)
                except Exception as e:
                    print(f"Error deleting old QR folder: {e}")
                
                self.object.save()
                total_lotes = len(lotes_por_cantidad)
                # remove existing lotes for this pedido and recreate
                Lote.objects.filter(idpedido=self.object).delete()
                if total_lotes > 0:
                    for i, lote_cant in enumerate(lotes_por_cantidad):
                        created_lote = Lote.objects.create(idpedido=self.object, cantidad=lote_cant)
                        # generate QR image for this lote (contains lote id)
                        try:
                            generate_lote_qr_image(created_lote, i+1, total_lotes)
                        except Exception:
                            pass
        except IntegrityError:
            self.object.save()
        orden_pk = getattr(self.object, 'idordenpedido_id', None)
        _actualizar_fecha_fin_orden(orden_pk)
        return redirect('listaPedidos', orden_pk=orden_pk)

class EliminarPedido(DeleteView):
    model = Pedido
    template_name = 'administrador/forms/confirmarEliminar.html'
    
    def get_object(self):
        return Pedido.objects.get(pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = 'pedido'
        context['numeroorden'] = self.object.idordenpedido.numeroorden
        context['cliente'] = self.object.idordenpedido.idcliente.nombre
        context['fechainicio'] = self.object.idordenpedido.fechainicio
        context['modelo'] = self.object.idmodelo.modelo
        context['folio'] = self.object.idmodelo.folio
        context['color'] = self.object.color
        context['talla'] = self.object.talla
        context['cantidad'] = self.object.cantidad
        return context
    
    def get_success_url(self):
        orden_pk = getattr(self.object, 'idordenpedido_id', None)
        return f'/administrador/ordenes/{orden_pk}/pedidos/'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        orden_pk = getattr(self.object, 'idordenpedido_id', None)
        # Eliminar carpeta QR del pedido antes de eliminar
        try:
            order_num = self.object.idordenpedido.numeroorden
            color_str = self.object.color
            folio_str = self.object.idmodelo.folio
            delete_lote_qr_images(order_num, color_str, folio_str)
        except Exception as e:
            print(f"Error eliminando carpeta QR del pedido: {e}")
        
        try:
            result = super().delete(request, *args, **kwargs)
            _actualizar_fecha_fin_orden(orden_pk)
            return result
        except Exception as e:
            print(f"Error eliminando pedido: {e}")
            import traceback
            traceback.print_exc()
            raise
    
class ListaLotes(ListView):
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
        lotes_qs = getattr(self, 'object_list', None) or ctx.get('lotes', Lote.objects.none())
        if hasattr(lotes_qs, 'count'):
            total_lotes = lotes_qs.count()
            corte_count = lotes_qs.filter(idempcorte__isnull=False).count()
            tejido_count = lotes_qs.filter(idemptejido__isnull=False).count()
            plancha_count = lotes_qs.filter(
                idempplanchapre__isnull=False,
                idempplanchapost__isnull=False,
            ).count()
            empaque_count = lotes_qs.filter(fechaempa__isnull=False).count()
        else:
            total_lotes = len(lotes_qs)
            corte_count = sum(1 for lote in lotes_qs if getattr(lote, 'idempcorte', None))
            tejido_count = sum(1 for lote in lotes_qs if getattr(lote, 'idemptejido', None))
            plancha_count = sum(
                1 for lote in lotes_qs
                if getattr(lote, 'idempplanchapre', None) and getattr(lote, 'idempplanchapost', None)
            )
            empaque_count = sum(1 for lote in lotes_qs if getattr(lote, 'fechaempa', None))
        ctx['resumen_lotes'] = {
            'total': total_lotes,
            'corte': corte_count,
            'tejido': tejido_count,
            'plancha': plancha_count,
            'empaque': empaque_count,
        }
        return ctx


@login_required
def lotes_imprimir_qrs(request, orden_pk, pk):
    try:
        pedido = Pedido.objects.select_related('idordenpedido', 'idmodelo').get(pk=pk, idordenpedido_id=orden_pk)
    except Pedido.DoesNotExist:
        messages.error(request, 'No se encontró el pedido para imprimir QRs.')
        return redirect('listaLotes', orden_pk=orden_pk, pk=pk)

    qr_folder = get_pedido_qr_folder(
        pedido.idordenpedido.numeroorden,
        pedido.idmodelo.folio,
        pedido.color,
    )

    qr_images = []
    if qr_folder.exists() and qr_folder.is_dir():
        for image_path in sorted(qr_folder.glob('*.png')):
            try:
                with open(image_path, 'rb') as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')
                qr_images.append({
                    'name': image_path.name,
                    'data': encoded,
                })
            except Exception:
                continue

    if not qr_images:
        messages.warning(request, 'No se encontraron imágenes QR para este pedido.')
        return redirect('listaLotes', orden_pk=orden_pk, pk=pk)

    return render(request, 'administrador/catalogos/imprimirQrs.html', {
        'pedido': pedido,
        'qr_images': qr_images,
        'orden_pk': orden_pk,
    })


@login_required
def lotes_abrir_carpeta_qrs(request, orden_pk, pk):
    try:
        pedido = Pedido.objects.select_related('idordenpedido', 'idmodelo').get(pk=pk, idordenpedido_id=orden_pk)
    except Pedido.DoesNotExist:
        return redirect('listaLotes', orden_pk=orden_pk, pk=pk)

    qr_folder = get_pedido_qr_folder(
        pedido.idordenpedido.numeroorden,
        pedido.idmodelo.folio,
        pedido.color,
    )

    if not qr_folder.exists() or not qr_folder.is_dir():
        return redirect('listaLotes', orden_pk=orden_pk, pk=pk)

    try:
        os.startfile(str(qr_folder))
    except Exception:
        pass

    return redirect('listaLotes', orden_pk=orden_pk, pk=pk)

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

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            generate_empleado_qr_image(self.object)
        except Exception as e:
            print(f"Error generando QR de empleado {self.object.idempleado}: {e}")
        return response

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

def _validar_flujo_lote(lote, area_type):
    area = area_type.lower()

    tiene_tejido = bool(getattr(lote, 'idemptejido', None) or getattr(lote, 'fechatermtejido', None))
    tiene_plancha_pre = bool(getattr(lote, 'idempplanchapre', None) or getattr(lote, 'fechatermplanchapre', None))
    tiene_plancha_post = bool(getattr(lote, 'idempplanchapost', None) or getattr(lote, 'fechatermplanchapost', None))
    tiene_plancha_completa = tiene_plancha_pre and tiene_plancha_post
    tiene_corte = bool(getattr(lote, 'idempcorte', None) or getattr(lote, 'fechatermcorte', None))

    if area == 'plancha' and not tiene_tejido:
        return 'No se puede registrar Plancha si primero no está registrado Tejido.'

    if area == 'corte':
        if not tiene_tejido:
            return 'No se puede registrar Corte si primero no está registrado Tejido.'
        if not tiene_plancha_completa:
            return 'No se puede registrar Corte si Plancha no tiene Pre y Post completos.'

    if area == 'empaquetado':
        if not tiene_tejido:
            return 'No se puede registrar Empaque si primero no está registrado Tejido.'
        if not tiene_plancha_completa:
            return 'No se puede registrar Empaque si Plancha no tiene Pre y Post completos.'
        if not tiene_corte:
            return 'No se puede registrar Empaque si primero no está registrado Corte.'

    return None

def registrar_lote_empleado(request, area_type):
    """
    Vista genérica para registrar un empleado y máquina en un lote usando QR.
    area_type puede ser 'corte', 'tejido', 'plancha' o 'empaquetado'
    """
    from django.utils import timezone
    
    # Formatear nombre del área para el título
    area_titles = {
        'corte': 'Corte',
        'tejido': 'Tejido',
        'plancha': 'Plancha',
        'empaquetado': 'Empaquetado',
    }
    
    area_capitalizada = area_titles.get(area_type.lower(), area_type)
    
    mensaje_error = None
    mensaje_exito = None
    empleado_actual = None
    
    if request.method == 'POST':
        form = LoteEmpleadoForm(request.POST, area=area_capitalizada)
        if form.is_valid():
            empleado_id = None
            lote_id = None
            try:
                empleado_qr = form.cleaned_data['empleado_qr']
                lote_qr = form.cleaned_data['lote_qr']
                maquina = form.cleaned_data['maquina']
                plancha_etapa = form.cleaned_data.get('plancha_etapa')

                empleado_id = parse_qr_id_for_prefix(empleado_qr, 'E')
                lote_id = parse_qr_id_for_prefix(lote_qr, 'L')

                empleado = Empleado.objects.get(idempleado=empleado_id, estatus=1)
                empleado_actual = empleado
                lote = Lote.objects.get(idlote=lote_id)

                mensaje_flujo = _validar_flujo_lote(lote, area_type)
                if mensaje_flujo:
                    mensaje_error = mensaje_flujo
                    raise ValueError(mensaje_error)

                # Actualizar el lote con el empleado, maquina y la fecha segun el area
                now = timezone.now()

                if area_type.lower() == 'corte':
                    lote.idempcorte = empleado
                    lote.idmaqcorte = maquina
                    lote.fechatermcorte = now
                elif area_type.lower() == 'tejido':
                    lote.idemptejido = empleado
                    lote.idmqutejido = maquina
                    lote.fechatermtejido = now
                elif area_type.lower() == 'plancha':
                    lote.idmaqplancha = maquina
                    if plancha_etapa == 'pre':
                        lote.idempplanchapre = empleado
                        lote.fechatermplanchapre = now
                    elif plancha_etapa == 'post':
                        lote.idempplanchapost = empleado
                        lote.fechatermplanchapost = now
                    else:
                        mensaje_error = 'Selecciona si el registro es Pre-Plancha o Post-Plancha'
                        raise ValueError(mensaje_error)
                elif area_type.lower() == 'empaquetado':
                    lote.fechaempa = now

                lote.save()
                if area_type.lower() == 'plancha':
                    etapa_texto = 'Pre-Plancha' if plancha_etapa == 'pre' else 'Post-Plancha'
                    mensaje_exito = f"Empleado {empleado.nombre} y maquina {maquina} registrados en {etapa_texto} del lote {lote_id}"
                elif area_type.lower() == 'empaquetado':
                    mensaje_exito = f"Empaque registrado correctamente en el lote {lote_id}"
                else:
                    mensaje_exito = f"Empleado {empleado.nombre} y maquina {maquina} registrados correctamente en el lote {lote_id}"
            except ValueError as exc:
                mensaje_error = str(exc)
            except Empleado.DoesNotExist:
                if empleado_id is None:
                    mensaje_error = 'No se encontro el empleado leido en el QR.'
                else:
                    mensaje_error = f'No se encontro un empleado activo con ID {empleado_id}.'
            except Lote.DoesNotExist:
                if lote_id is None:
                    mensaje_error = 'No se encontro el lote leido en el QR.'
                else:
                    mensaje_error = f'No se encontro el lote con ID {lote_id}.'
            except Exception as e:
                mensaje_error = f"Error al procesar el formulario: {str(e)}"
        else:
            if form.errors.get('empleado_qr'):
                mensaje_error = 'Primero escanea un QR de empleado.'
            elif form.errors.get('lote_qr'):
                mensaje_error = 'Escanea un QR de lote para guardar.'
            elif form.errors.get('maquina'):
                mensaje_error = form.errors['maquina'][0]
            elif form.errors.get('plancha_etapa'):
                mensaje_error = form.errors['plancha_etapa'][0]
            else:
                mensaje_error = 'Completa los datos requeridos para guardar el registro.'
    else:
        form = LoteEmpleadoForm(area=area_capitalizada)

    empleados_lookup = {
        str(empleado.idempleado): f"{empleado.nombre} {empleado.apellidos}".strip()
        for empleado in Empleado.objects.filter(estatus=1).order_by('idempleado')
    }

    if empleado_actual is None:
        empleado_qr_val = ''
        if getattr(form, 'is_bound', False):
            empleado_qr_val = str(form.data.get('empleado_qr', '')).strip()
        if empleado_qr_val:
            try:
                empleado_id = parse_qr_id_for_prefix(empleado_qr_val, 'E')
                empleado_actual = Empleado.objects.filter(idempleado=empleado_id).first()
            except ValueError:
                empleado_actual = None
    
    context = {
        'form': form,
        'area': area_capitalizada,
        'mensaje_error': mensaje_error,
        'mensaje_exito': mensaje_exito,
        'empleados_lookup': empleados_lookup,
        'empleado_actual': empleado_actual,
    }
    
    template_name = f'empleados/{area_type.lower()}.html'
    return render(request, template_name, context)

def tejido(request):
    return registrar_lote_empleado(request, 'tejido')

def plancha(request):
    return registrar_lote_empleado(request, 'plancha')

def corte(request):
    return registrar_lote_empleado(request, 'corte')

def empaquetado(request):
    mensaje_error = None
    mensaje_exito = None

    ordenes = Ordendepedido.objects.select_related('idcliente').order_by('-idordendepedido')
    pedidos = Pedido.objects.select_related('idordenpedido', 'idmodelo').order_by('-idpedido')

    selected_orden_id = request.POST.get('orden_id') or request.GET.get('orden_id') or ''
    selected_pedido_id = request.POST.get('pedido_id') or ''

    if request.method == 'POST':
        if not selected_orden_id or not selected_pedido_id:
            mensaje_error = 'Selecciona una orden y un pedido para registrar empaquetado.'
        else:
            try:
                pedido = Pedido.objects.select_related('idordenpedido', 'idmodelo').get(
                    idpedido=selected_pedido_id,
                    idordenpedido_id=selected_orden_id,
                )
                lotes_qs = Lote.objects.filter(idpedido=pedido)

                if not lotes_qs.exists():
                    mensaje_error = 'El pedido seleccionado no tiene lotes para empaquetar.'
                else:
                    lotes_bloqueados = []
                    for lote in lotes_qs:
                        error_flujo = _validar_flujo_lote(lote, 'empaquetado')
                        if error_flujo:
                            lotes_bloqueados.append(lote.idlote)

                    if lotes_bloqueados:
                        mensaje_error = (
                            'No se puede registrar Empaque porque hay lotes sin etapas previas completas. '
                            f'Lotes bloqueados: {", ".join(str(lid) for lid in lotes_bloqueados)}.'
                        )
                    else:
                        now = timezone.now()
                        total_actualizados = lotes_qs.update(fechaempa=now)
                        pedido.fechafin = now
                        pedido.save(update_fields=['fechafin'])
                        _actualizar_fecha_fin_orden(pedido.idordenpedido_id)
                        mensaje_exito = (
                            f'Se registró empaquetado para {total_actualizados} lote(s) '
                            f'del pedido {pedido.idpedido}. El pedido quedó finalizado.'
                        )
            except Pedido.DoesNotExist:
                mensaje_error = 'La combinación de orden y pedido no es válida.'
            except Exception as exc:
                mensaje_error = f'Error al registrar empaquetado: {exc}'

    context = {
        'area': 'Empaquetado',
        'ordenes': ordenes,
        'pedidos': pedidos,
        'selected_orden_id': str(selected_orden_id),
        'selected_pedido_id': str(selected_pedido_id),
        'mensaje_error': mensaje_error,
        'mensaje_exito': mensaje_exito,
    }
    return render(request, 'empleados/empaquetado.html', context)

def reportes(request):
    return render(request, 'administrador/reportes.html')


@login_required
@user_passes_test(lambda user: user.is_staff)
def cargar_datos_prueba(request):
    if request.method != 'POST':
        return redirect('homeAdmin')

    try:
        resultado = insertar_datos_prueba_temporales()
        total_pedidos = len(resultado.get('pedidos', []))
        total_lotes = sum(cantidad_lotes for _, cantidad_lotes in resultado.get('pedidos', []))
        total_clientes = len(resultado.get('clientes', []))
        total_modelos = len(resultado.get('modelos', []))
        total_empleados = len(resultado.get('empleados', []))
        total_maquinas = len(resultado.get('maquinas', []))
        total_ordenes = len(resultado.get('ordenes', []))
        total_comentarios = len(resultado.get('comentarios', []))
        messages.success(
            request,
            (
                f"Datos de prueba insertados correctamente: "
                f"{total_clientes} clientes, {total_modelos} modelos, {total_empleados} empleados, "
                f"{total_maquinas} máquinas, {total_ordenes} órdenes, {total_pedidos} pedidos, "
                f"{total_lotes} lotes con QR y {total_comentarios} comentarios."
            ),
        )
    except Exception as exc:
        messages.error(request, f"Error al insertar datos de prueba: {exc}")

    return redirect('homeAdmin')