from rest_framework import serializers
from .models import (
    Cliente, Modelo, Lote, Empleado, Maquina,
    Pedido, Ordendepedido, Comentariosmaquinas
)

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class ModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelo
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = '__all__'


class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = '__all__'


class OrdendepedidoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        source='idcliente',
        queryset=Cliente.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Ordendepedido
        fields = [
            'idordendepedido', 'numeroorden', 'cliente', 'cliente_id',
            'fechainicio', 'fechafin'
        ]


class PedidoSerializer(serializers.ModelSerializer):
    modelo = ModeloSerializer(source='idmodelo', read_only=True)
    orden = OrdendepedidoSerializer(source='idordenpedido', read_only=True)

    modelo_id = serializers.PrimaryKeyRelatedField(
        source='idmodelo',
        queryset=Modelo.objects.all(),
        write_only=True,
        required=False
    )
    orden_id = serializers.PrimaryKeyRelatedField(
        source='idordenpedido',
        queryset=Ordendepedido.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Pedido
        fields = [
            'idpedido',
            'orden', 'orden_id',
            'modelo', 'modelo_id',
            'talla', 'cantidad', 'color',
            'totallotes', 'loteterminado',
            'fechainicio', 'fechafin', 'fechaprevista'
        ]


class LoteSerializer(serializers.ModelSerializer):
    emp_tejido = EmpleadoSerializer(source='idemptejido', read_only=True)
    emp_plancha = EmpleadoSerializer(source='idempplancha', read_only=True)
    emp_corte = EmpleadoSerializer(source='idempcorte', read_only=True)

    maq_tejido = MaquinaSerializer(source='idmqutejido', read_only=True)
    maq_plancha = MaquinaSerializer(source='idmaqplancha', read_only=True)
    maq_corte = MaquinaSerializer(source='idmaqcorte', read_only=True)

    emp_tejido_id = serializers.PrimaryKeyRelatedField(
        source='idemptejido', queryset=Empleado.objects.all(), write_only=True, required=False
    )
    emp_plancha_id = serializers.PrimaryKeyRelatedField(
        source='idempplancha', queryset=Empleado.objects.all(), write_only=True, required=False
    )
    emp_corte_id = serializers.PrimaryKeyRelatedField(
        source='idempcorte', queryset=Empleado.objects.all(), write_only=True, required=False
    )

    maq_tejido_id = serializers.PrimaryKeyRelatedField(
        source='idmqutejido', queryset=Maquina.objects.all(), write_only=True, required=False
    )
    maq_plancha_id = serializers.PrimaryKeyRelatedField(
        source='idmaqplancha', queryset=Maquina.objects.all(), write_only=True, required=False
    )
    maq_corte_id = serializers.PrimaryKeyRelatedField(
        source='idmaqcorte', queryset=Maquina.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Lote
        fields = '__all__'



class ComentariosMaquinasSerializer(serializers.ModelSerializer):
    empleado = EmpleadoSerializer(source='idempleado', read_only=True)
    maquina = MaquinaSerializer(source='idmaquina', read_only=True)
    
    empleado_id = serializers.PrimaryKeyRelatedField(
        source='idempleado', queryset=Empleado.objects.all(), write_only=True, required=False
    )
    maquina_id = serializers.PrimaryKeyRelatedField(
        source='idmaquina', queryset=Maquina.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Comentariosmaquinas
        fields = [
            'idcomentariosmaquinas', 'comentario', 'fecharegistro', 'solucionado',
            'empleado', 'empleado_id', 'maquina', 'maquina_id'
        ]
