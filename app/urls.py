from django import views
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
    #CRUD MAQUINAS
    path('administrador/maquinas/', ListaMaquinas.as_view(), name='maquinas'),
    path('administrador/maquinas/form', CrearMaquina.as_view(), name='formMaquina'),
    path('administrador/maquinas/actualizar/<int:pk>/', ActualizarMaquina.as_view(), name='actualizarMaquina'),
    #PEDIDOS LOTES
    path('administrador/catalogos/listaPedidos/', listaPedidos, name='listaPedidos'),
    path('administrador/lotes/', lotes, name='lotes'),
    #EMPLEADOS
    path('empleados/tejido/', tejido, name='tejido'),
    path('empleados/plancha/', plancha, name='plancha'),
    path('empleados/corte/', corte, name='corte'),

]