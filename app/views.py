from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from app.models import Empleado, Maquina, Modelo
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.forms import *

# Create your views here.
#VISTAS GENERICAS
def homeGenerico(request):
    return render(request, 'genericas/home.html')

#VISTAS ADMINISTRADOR

def login(request):
    return render(request, 'administrador/login.html')

def catalogos(request):
    return render(request, 'administrador/catalogos.html')

def lotes(request):
    return render(request, 'administrador/lotes.html')

def listaPedidos(request):
    return render(request, 'administrador/catalogos/listaPedidos.html')

def listaEmpleados(request):
    return render(request, 'administrador/catalogos/listaEmpleados.html')

def homeAdmin(request):
    return render(request, 'administrador/homeAdmin.html')

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

    #CRUD Maquinas
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

    #CRUD Modelos
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

#VISTAS EMPLEADOS

def tejido(request):
    return render(request, 'empleados/tejido.html')

def plancha(request):
    return render(request, 'empleados/plancha.html')

def corte(request):
    return render(request, 'empleados/corte.html')