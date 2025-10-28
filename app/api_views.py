from rest_framework import viewsets
from rest_framework import permissions
from .models import Cliente, Modelo, Lote, Empleado, Maquina, Pedido, Ordendepedido, Comentariosmaquinas
from .serializers import (
    ClienteSerializer, ModeloSerializer, LoteSerializer,
    EmpleadoSerializer, MaquinaSerializer, PedidoSerializer,
    OrdendepedidoSerializer, ComentariosMaquinasSerializer
)


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


class EmpleadoViewSet(viewsets.ModelViewSet):
    """CRUD para empleados (modelo básico)"""
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.AllowAny]


class MaquinaViewSet(viewsets.ModelViewSet):
    """CRUD para maquinas (modelo básico)"""
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
    permission_classes = [permissions.AllowAny]


class OrdendepedidoViewSet(viewsets.ModelViewSet):
    """CRUD para ordenes de pedido (relacionado con Cliente)"""
    queryset = Ordendepedido.objects.all()
    serializer_class = OrdendepedidoSerializer
    permission_classes = [permissions.AllowAny]


class PedidoViewSet(viewsets.ModelViewSet):
    """CRUD para pedidos (relacionado con Orden y Modelo)"""
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [permissions.AllowAny]


class ComentariosMaquinasViewSet(viewsets.ModelViewSet):
    """CRUD para comentarios de maquinas (relacionado con Maquina y Empleado)"""
    queryset = Comentariosmaquinas.objects.all()
    serializer_class = ComentariosMaquinasSerializer
    permission_classes = [permissions.AllowAny]
