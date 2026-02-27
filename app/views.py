from django.forms import inlineformset_factory
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.clickjacking import xframe_options_sameorigin
from app.models import *
from django.db.models import Count
from django.db import transaction
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.utils import generate_lote_qr_image, delete_lote_qr_images, decode_qr_from_image, delete_orden_qr_folder
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
                            folio_str = ''
                            try:
                                folio_str = self.object.idmodelo.folio
                            except Exception:
                                folio_str = getattr(self.object, 'idmodelo_id', '')
                            color_str = getattr(self.object, 'color', '')
                            pedido_id = getattr(self.object, 'idpedido', None) or getattr(self.object, 'pk', '')
                            generate_lote_qr_image(order_num, pedido_id, color_str, i+1, total_lotes, created_lote.idlote, folio_str)
                        except Exception:
                            # if image generation fails, continue without stopping the transaction
                            pass
        except IntegrityError:
            # fallback: ensure object saved
            self.object.save()
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
                # delete existing QR images using ORIGINAL values before saving changes
                try:
                    delete_lote_qr_images(original_order_num, original_color, original_folio)
                except Exception as e:
                    print(f"Error deleting old QR folder: {e}")
                
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
                            folio_str = ''
                            try:
                                folio_str = self.object.idmodelo.folio
                            except Exception:
                                folio_str = getattr(self.object, 'idmodelo_id', '')
                            color_str = getattr(self.object, 'color', '')
                            pedido_id = getattr(self.object, 'idpedido', None) or getattr(self.object, 'pk', '')
                            generate_lote_qr_image(order_num, pedido_id, color_str, i+1, total_lotes, created_lote.idlote, folio_str)
                        except Exception:
                            pass
        except IntegrityError:
            self.object.save()
        orden_pk = getattr(self.object, 'idordenpedido_id', None)
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
        # Eliminar carpeta QR del pedido antes de eliminar
        try:
            order_num = self.object.idordenpedido.numeroorden
            color_str = self.object.color
            folio_str = self.object.idmodelo.folio
            delete_lote_qr_images(order_num, color_str, folio_str)
        except Exception as e:
            print(f"Error eliminando carpeta QR del pedido: {e}")
        
        try:
            return super().delete(request, *args, **kwargs)
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
            plancha_count = lotes_qs.filter(idempplancha__isnull=False).count()
            empaque_count = lotes_qs.filter(fechaempa__isnull=False).count()
        else:
            total_lotes = len(lotes_qs)
            corte_count = sum(1 for lote in lotes_qs if getattr(lote, 'idempcorte', None))
            tejido_count = sum(1 for lote in lotes_qs if getattr(lote, 'idemptejido', None))
            plancha_count = sum(1 for lote in lotes_qs if getattr(lote, 'idempplancha', None))
            empaque_count = sum(1 for lote in lotes_qs if getattr(lote, 'fechaempa', None))
        ctx['resumen_lotes'] = {
            'total': total_lotes,
            'corte': corte_count,
            'tejido': tejido_count,
            'plancha': plancha_count,
            'empaque': empaque_count,
        }
        return ctx

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

def registrar_lote_empleado(request, area_type):
    """
    Vista genérica para registrar un empleado y máquina en un lote usando QR.
    area_type puede ser 'corte', 'tejido' o 'plancha'
    """
    from django.utils import timezone
    
    # Formatear nombre del área para el título
    area_titles = {
        'corte': 'Corte',
        'tejido': 'Tejido',
        'plancha': 'Plancha'
    }
    
    area_capitalizada = area_titles.get(area_type.lower(), area_type)
    
    mensaje_error = None
    mensaje_exito = None
    
    if request.method == 'POST':
        form = LoteEmpleadoForm(request.POST, request.FILES, area=area_capitalizada)
        if form.is_valid():
            try:
                empleado = form.cleaned_data['empleado']
                maquina = form.cleaned_data['maquina']
                qr_image = form.cleaned_data['qr_image']
                
                # Decodificar el QR
                qr_data = decode_qr_from_image(qr_image)
                
                if qr_data:
                    try:
                        lote_id = int(qr_data)
                        lote = Lote.objects.get(idlote=lote_id)
                        
                        # Actualizar el lote con el empleado, máquina y la fecha según el área
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
                            lote.idempplancha = empleado
                            lote.idmaqplancha = maquina
                            lote.fechatermplancha = now
                        
                        lote.save()
                        mensaje_exito = f"Empleado {empleado.nombre} y máquina {maquina} registrados correctamente en el lote {lote_id}"
                    except ValueError:
                        mensaje_error = "El QR no contiene un ID de lote válido"
                    except Lote.DoesNotExist:
                        mensaje_error = f"No se encontró el lote con ID {qr_data}"
                else:
                    mensaje_error = "No se pudo decodificar el QR. Verifica que la imagen sea clara."
            except Exception as e:
                mensaje_error = f"Error al procesar el formulario: {str(e)}"
    else:
        form = LoteEmpleadoForm(area=area_capitalizada)
    
    context = {
        'form': form,
        'area': area_capitalizada,
        'mensaje_error': mensaje_error,
        'mensaje_exito': mensaje_exito,
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
    return render(request, 'empleados/empaquetado.html')

def reportes(request):
    return render(request, 'administrador/reportes.html')