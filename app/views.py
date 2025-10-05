from django.shortcuts import render

# Create your views here.
#VISTAS GENERICAS
def homeGenerico(request):
    return render(request, 'genericas/home.html')

#VISTAS ADMINISTRADOR

def login(request):
    return render(request, 'administrador/login.html')

#VISTAS EMPLEADOS

def tejido(request):
    return render(request, 'empleados/tejido.html')

def plancha(request):
    return render(request, 'empleados/plancha.html')

def corte(request):
    return render(request, 'empleados/corte.html')