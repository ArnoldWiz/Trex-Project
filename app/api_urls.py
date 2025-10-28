from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import api_views

router = DefaultRouter()
router.register(r'clientes', api_views.ClienteViewSet, basename='cliente')
router.register(r'modelos', api_views.ModeloViewSet, basename='modelo')
router.register(r'lotes', api_views.LoteViewSet, basename='lote')

urlpatterns = [
    path('', include(router.urls)),
]
