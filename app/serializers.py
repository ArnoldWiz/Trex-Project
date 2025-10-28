from rest_framework import serializers
from .models import Cliente, Modelo, Lote


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        # use fields explicitly to avoid surprises with unmanaged models
        fields = ['idcliente', 'nombre', 'contacto', 'estatus']


class ModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelo
        fields = ['idmodelo', 'folio', 'modelo', 'cantidadhilo', 'estatus']


class LoteSerializer(serializers.ModelSerializer):
    # include nested/readable related fields if desired
    class Meta:
        model = Lote
        fields = [
            'idlote', 'idorden', 'idemptejido', 'idempplancha', 'idempcorte',
            'idmqutejido', 'idmaqplancha', 'idmaqcorte', 'cantidad',
            'fechatermtejido', 'fechatermplancha', 'fechatermcorte', 'fechaempa'
        ]
