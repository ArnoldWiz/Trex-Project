from django.urls import path
from app.views import *


urlpatterns = [
    #GENRICAS
    path('', homeGenerico, name='home'),
    
    #ADMINISTRADOR
    path('administrador/login/', login, name='login'),

    #EMPLEADOS
    path('empleados/tejido/', tejido, name='tejido'),
    path('empleados/plancha/', plancha, name='plancha'),
    path('empleados/corte/', corte, name='corte'),
]