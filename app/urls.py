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
    path('administrador/formEmpleado/', CrearEmpleado.as_view(), name='formEmpleado'),
    path('administrador/listarEmpleados/', ListaEmpleados.as_view(), name='listaEmpleados'),
    path('administrador/actualizarEmpleado/<int:pk>/', ActualizarEmpleado.as_view(), name='actualizarEmpleado'),

    #PEDIDOS LOTES
    path('administrador/listaPedidos/', listaPedidos, name='listaPedidos'),
    path('administrador/lotes/', lotes, name='lotes'),
    #EMPLEADOS
    path('empleados/tejido/', tejido, name='tejido'),
    path('empleados/plancha/', plancha, name='plancha'),
    path('empleados/corte/', corte, name='corte'),

]