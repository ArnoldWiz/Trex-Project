from rest_framework import serializers
from .models import (
    Cliente, Modelo, Lote, Empleado, Maquina,
    Pedido, Ordendepedido, Comentariosmaquinas
)


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['idcliente', 'nombre', 'contacto', 'estatus']


class ModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelo
        fields = ['idmodelo', 'folio', 'modelo', 'cantidadhilo', 'estatus']


class LoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = [
            'idlote', 'idorden', 'idemptejido', 'idempplancha', 'idempcorte',
            'idmqutejido', 'idmaqplancha', 'idmaqcorte', 'cantidad',
            'fechatermtejido', 'fechatermplancha', 'fechatermcorte', 'fechaempa'
        ]


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ['idempleado', 'area', 'nombre', 'apellidos', 'estatus']


class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = ['idmaquina', 'area', 'numero', 'estatus']


class OrdendepedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='idcliente.nombre', read_only=True)

    class Meta:
        model = Ordendepedido
        fields = ['idordendepedido', 'numeroorden', 'idcliente', 'cliente_nombre', 'fechainicio', 'fechafin']


class PedidoSerializer(serializers.ModelSerializer):
    modelo_folio = serializers.CharField(source='idmodelo.folio', read_only=True)
    orden_numero = serializers.CharField(source='idordenpedido.numeroorden', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'idpedido', 'idordenpedido', 'idmodelo', 'modelo_folio', 'talla',
            'cantidad', 'color', 'totallotes', 'loteterminado', 'fechainicio',
            'fechafin', 'fechaprevista', 'orden_numero'
        ]


class ComentariosMaquinasSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='idempleado.nombre', read_only=True)
    maquina_numero = serializers.IntegerField(source='idmaquina.numero', read_only=True)

    class Meta:
        model = Comentariosmaquinas
        fields = ['idcomentariosmaquinas', 'idmaquina', 'maquina_numero', 'idempleado', 'empleado_nombre', 'comentario', 'fecharegistro', 'solucionado']
