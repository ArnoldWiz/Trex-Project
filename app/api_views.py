from rest_framework import viewsets
from rest_framework import permissions
from .models import Cliente, Modelo, Lote
from .serializers import ClienteSerializer, ModeloSerializer, LoteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """CRUD para clientes (modelo básico)"""
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.AllowAny]


class ModeloViewSet(viewsets.ModelViewSet):
    """CRUD para modelos (modelo básico)"""
    queryset = Modelo.objects.all()
    serializer_class = ModeloSerializer
    permission_classes = [permissions.AllowAny]


class LoteViewSet(viewsets.ModelViewSet):
    """CRUD para lotes (modelo relacionado con otros)"""
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer
    permission_classes = [permissions.AllowAny]
