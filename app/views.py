from django.shortcuts import render
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from app.models import Empleado
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from app.forms import *

# Create your views here.
#VISTAS GENERICAS
def homeGenerico(request):
    return render(request, 'genericas/home.html')

#VISTAS ADMINISTRADOR

def login(request):
    return render(request, 'administrador/login.html')

def homeAdmin(request):
    return render(request, 'administrador/homeAdmin.html')

class ListaEmpleados(ListView):
    model = Empleado
    template_name = 'administrador/listaEmpleados.html'
    context_object_name = 'empleados'

class CrearEmpleado(CreateView):
    model = Empleado
    template_name = 'administrador/formEmpleado.html'
    form_class = EmpleadoForm
    success_url = '/administrador/listarEmpleados/'

class ActualizarEmpleado(UpdateView):
    model = Empleado
    template_name = 'administrador/formEmpleado.html'
    form_class = EmpleadoForm
    fields = ['nombre', 'apellidos', 'area', 'estatus']
    success_url = '/administrador/listarEmpleados/'

#VISTAS EMPLEADOS

def tejido(request):
    return render(request, 'empleados/tejido.html')

def plancha(request):
    return render(request, 'empleados/plancha.html')

def corte(request):
    return render(request, 'empleados/corte.html')