from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import api_views

router = DefaultRouter()
router.register(r'clientes', api_views.ClienteViewSet, basename='cliente')
router.register(r'modelos', api_views.ModeloViewSet, basename='modelo')
router.register(r'lotes', api_views.LoteViewSet, basename='lote')
router.register(r'empleados', api_views.EmpleadoViewSet, basename='empleado')
router.register(r'maquinas', api_views.MaquinaViewSet, basename='maquina')
router.register(r'ordenes', api_views.OrdendepedidoViewSet, basename='ordendepedido')
router.register(r'pedidos', api_views.PedidoViewSet, basename='pedido')
router.register(r'comentariosmaquinas', api_views.ComentariosMaquinasViewSet, basename='comentariosmaquinas')

urlpatterns = [
    path('', include(router.urls)),
    
]
