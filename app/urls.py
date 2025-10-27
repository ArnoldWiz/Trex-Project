from django.urls import path
from app.views import *


urlpatterns = [
    #GENERICAS
    path('', homeGenerico, name='home'),
    
    #ADMINISTRADOR
    path('administrador/login/', login, name='login'),
    path('administrador/homeAdmin/', homeAdmin, name='homeAdmin'),
    path('administrador/catalogos/', catalogos, name='catalogos'),
        #CRUD EMPLEADOS
    path('administrador/empleados/', ListaEmpleados.as_view(), name='empleados'),
    path('administrador/empleados/form', CrearEmpleado.as_view(), name='formEmpleado'),
    path('administrador/empleados/actualizar/<int:pk>/', ActualizarEmpleado.as_view(), name='actualizarEmpleado'),
        #CRUD MÁQUINAS
    path('administrador/maquinas/', ListaMaquinas.as_view(), name='maquinas'),
    path('administrador/maquinas/form', CrearMaquina.as_view(), name='formMaquina'),
    path('administrador/maquinas/actualizar/<int:pk>/', ActualizarMaquina.as_view(), name='actualizarMaquina'),
        #CRUD MODELOS
    path('administrador/modelos/', ListaModelos.as_view(), name='modelos'),
    path('administrador/modelos/form', CrearModelo.as_view(), name='formModelo'),
    path('administrador/modelos/actualizar/<int:pk>/', ActualizarModelo.as_view(), name='actualizarModelo'),
        #CRUD CLIENTES
    path('administrador/clientes/', ListaClientes.as_view(), name='clientes'),
    path('administrador/clientes/form', CrearCliente.as_view(), name='formCliente'),
    path('administrador/clientes/actualizar/<int:pk>/', ActualizarCliente.as_view(), name='actualizarCliente'),
        #CRUD ORDENES DE PEDIDO
    path('administrador/ordenes', ListaOrdenes.as_view(), name='listaOrdenes'),
    path('administrador/ordenes/form/', CrearOrden.as_view(), name='crearOrden'),
    path('administrador/ordenes/actualizar/<int:pk>/', ActualizarOrden.as_view(), name='actualizarOrden'),
        #CRUD PEDIDOS
    path('administrador/ordenes/<int:orden_pk>/pedidos/', ListaPedidos.as_view(), name='listaPedidos'),
    path('administrador/ordenes/<int:orden_pk>/pedidos/form/', CrearPedido.as_view(), name='crearPedido'),
    path('administrador/ordenes/<int:orden_pk>/pedidos/actualizar/<int:pk>/', ActualizarPedido.as_view(), name='actualizarPedido'),
        #LOTES
    path("administrador/ordenes/<int:orden_pk>/pedidos/<int:pk>/lotes/", ListaLotes.as_view(), name="listaLotes"),

    #TEMPORALES
    path('administrador/catalogos/pedidoEspecifico/', pedidoEspecifico, name='pedidoEspecifico'),
    path('administrador/lotes/', lotes, name='lotes'),
    
    
    
    #VISTA GENERAL EMPLEADOS
    path('empleados/tejido/', tejido, name='tejido'),
    path('empleados/plancha/', plancha, name='plancha'),
    path('empleados/corte/', corte, name='corte'),

]