from datetime import timedelta
import random

from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Max

from app.models import (
    Cliente,
    Comentariosmaquinas,
    Empleado,
    Lote,
    Maquina,
    Modelo,
    Ordendepedido,
    Pedido,
)
from app.utils import generate_lote_qr_image, delete_orden_qr_folder


CLIENTES_SEED = [
    ('Calzado Rivera S.A. de C.V.', 'Laura Rivera - +52 33 1452 8890'),
    ('Distribuidora Norte Zapatera', 'Miguel Hernández - +52 81 2234 5560'),
    ('Comercializadora El Paso', 'Ana Sofía Torres - +52 55 3941 7702'),
    ('Grupo Textil Bajío', 'Carlos Mendoza - +52 442 817 3001'),
    ('Tiendas Urban Walk', 'Daniela Cruz - +52 664 240 1908'),
]

MODELOS_SEED = [
    ('TRX-CHN-1001', 'Chinela Confort Clásica', 135),
    ('TRX-CHN-1002', 'Chinela Sport Flex', 145),
    ('TRX-CHN-1003', 'Chinela Dama Soft', 125),
    ('TRX-CHN-1004', 'Chinela Kids Basic', 95),
    ('TRX-CHN-1005', 'Chinela Premium Max', 165),
]

EMPLEADOS_SEED = [
    ('Tejido', 'José', 'Martínez López'),
    ('Plancha', 'María', 'García Peña'),
    ('Plancha', 'Luis', 'Ramírez Soto'),
    ('Corte', 'Fernanda', 'Ortega Díaz'),
    ('Tejido', 'Carlos', 'Salazar Gómez'),
]

MAQUINAS_SEED = [
    ('Tejido', 301),
    ('Plancha', 302),
    ('Corte', 303),
    ('Tejido', 304),
    ('Plancha', 305),
]

ORDENES_SEED = [
    'TRX-2026-1001',
    'TRX-2026-1002',
    'TRX-2026-1003',
    'TRX-2026-1004',
    'TRX-2026-1005',
]

PEDIDOS_SEED = [
    ('Negro', 24, 26),
    ('Azul Marino', 17, 27),
    ('Rojo Vino', 31, 28),
    ('Beige Arena', 14, 25),
    ('Verde Olivo', 22, 29),
]

COLORES_EXTRA = [
    'Negro', 'Azul Marino', 'Rojo Vino', 'Beige Arena', 'Verde Olivo',
    'Gris Oxford', 'Miel', 'Blanco Perla', 'Café', 'Azul Rey'
]

COMENTARIOS_SEED = [
    'Ajuste preventivo de tensión de banda en máquina de tejido.',
    'Revisión de plancha por variación mínima de temperatura.',
    'Lubricación completada en eje principal de corte.',
    'Calibración de rodillos y prueba de funcionamiento correcta.',
    'Mantenimiento menor finalizado y equipo liberado.',
]


def _limpiar_datos_prueba_previos():
    ordenes_qs = Ordendepedido.objects.filter(
        Q(numeroorden__in=ORDENES_SEED)
        | Q(idcliente__nombre__startswith='Cliente Prueba')
    ).distinct()

    for orden in ordenes_qs:
        try:
            delete_orden_qr_folder(orden.numeroorden)
        except Exception:
            pass

    pedidos_qs = Pedido.objects.filter(idordenpedido__in=ordenes_qs)
    Lote.objects.filter(idpedido__in=pedidos_qs).delete()
    pedidos_qs.delete()
    ordenes_qs.delete()

    Comentariosmaquinas.objects.filter(
        Q(comentario__startswith='Comentario de prueba automático')
        | Q(comentario__in=COMENTARIOS_SEED)
    ).delete()

    Empleado.objects.filter(
        Q(nombre='Empleado')
        | Q(nombre__in=[empleado[1] for empleado in EMPLEADOS_SEED], apellidos__in=[empleado[2] for empleado in EMPLEADOS_SEED])
    ).delete()

    Maquina.objects.filter(
        numero__in=[maquina[1] for maquina in MAQUINAS_SEED]
    ).delete()

    Modelo.objects.filter(
        Q(modelo__startswith='Modelo Prueba')
        | Q(folio__in=[modelo[0] for modelo in MODELOS_SEED])
    ).delete()

    Cliente.objects.filter(
        Q(nombre__startswith='Cliente Prueba')
        | Q(nombre__in=[cliente[0] for cliente in CLIENTES_SEED])
    ).delete()


def _crear_lotes_con_qr(pedido):
    cantidad_total = int(pedido.cantidad or 0)
    lotes_creados = []

    if cantidad_total <= 0:
        return lotes_creados

    lotes_base = cantidad_total // 10
    residuo = cantidad_total % 10
    lotes_cantidades = [10] * lotes_base

    if lotes_base == 0:
        lotes_cantidades = [cantidad_total]
    elif residuo > 0:
        if 1 <= residuo <= 4:
            lotes_cantidades[-1] += residuo
        else:
            lotes_cantidades.append(residuo)

    total_lotes = len(lotes_cantidades)
    pedido.totallotes = total_lotes
    pedido.save(update_fields=['totallotes'])

    for indice, cantidad_lote in enumerate(lotes_cantidades):

        lote = Lote.objects.create(
            idpedido=pedido,
            cantidad=cantidad_lote,
        )
        generate_lote_qr_image(lote, indice + 1, total_lotes)
        lotes_creados.append(lote)

    return lotes_creados


@transaction.atomic
def insertar_datos_prueba_temporales():
    _limpiar_datos_prueba_previos()

    ahora = timezone.now()
    rng = random.Random()

    clientes = []
    modelos = []
    ordenes = []
    pedidos_creados = []
    comentarios = []

    for nombre, contacto in CLIENTES_SEED:
        cliente = Cliente.objects.create(
            nombre=nombre,
            contacto=contacto,
            estatus=1,
        )
        clientes.append(cliente)

    for folio, nombre_modelo, cantidad_hilo in MODELOS_SEED:
        modelo = Modelo.objects.create(
            folio=folio,
            modelo=nombre_modelo,
            cantidadhilo=cantidad_hilo,
            estatus=1,
        )
        modelos.append(modelo)

    empleados = []
    for area, nombre, apellidos in EMPLEADOS_SEED:
        empleados.append(
            Empleado.objects.create(area=area, nombre=nombre, apellidos=apellidos, estatus=1)
        )

    maquinas = []
    for area, numero in MAQUINAS_SEED:
        maquinas.append(Maquina.objects.create(area=area, numero=numero, estatus=1))

    empleado_tejido = empleados[0]
    empleado_plancha_pre = empleados[1]
    empleado_plancha_post = empleados[2]
    empleado_corte = empleados[3]

    maquina_tejido = maquinas[0]
    maquina_plancha = maquinas[1]
    maquina_corte = maquinas[2]

    for i in range(5):
        orden = Ordendepedido.objects.create(
            numeroorden=ORDENES_SEED[i],
            idcliente=clientes[i],
            fechainicio=ahora + timedelta(minutes=i),
            fechaprevista=ahora + timedelta(days=rng.randint(12, 24)),
            fechafin=None,
        )
        ordenes.append(orden)

        cantidad_pedidos = rng.randint(2, 4)
        for j in range(cantidad_pedidos):
            color_base, cantidad_base, talla_base = rng.choice(PEDIDOS_SEED)
            color = rng.choice(COLORES_EXTRA) if rng.random() > 0.45 else color_base
            cantidad = max(8, cantidad_base + rng.randint(-6, 18))
            talla = max(22, talla_base + rng.choice([-1, 0, 1]))

            pedido = Pedido.objects.create(
                idordenpedido=orden,
                idmodelo=rng.choice(modelos),
                talla=talla,
                cantidad=cantidad,
                color=color,
                totallotes=0,
                loteterminado=0,
                fechainicio=ahora + timedelta(minutes=i, hours=j),
                fechafin=None,
                fechaprevista=ahora + timedelta(days=rng.randint(6, 16)),
            )

            lotes = _crear_lotes_con_qr(pedido)
            lotes_terminados_proceso = 0
            lotes_empaquetados = 0

            for lote in lotes:
                etapa = rng.choices([1, 2, 3, 4, 5], weights=[15, 20, 25, 25, 15], k=1)[0]

                if etapa >= 1:
                    lote.idemptejido = empleado_tejido
                    lote.idmqutejido = maquina_tejido
                    lote.fechatermtejido = ahora + timedelta(hours=rng.randint(1, 8))

                if etapa >= 2:
                    if rng.random() < 0.5:
                        lote.idempplanchapre = empleado_plancha_pre
                        lote.fechatermplanchapre = ahora + timedelta(hours=rng.randint(2, 10))
                    else:
                        lote.idempplanchapost = empleado_plancha_post
                        lote.fechatermplanchapost = ahora + timedelta(hours=rng.randint(2, 10))
                    lote.idmaqplancha = maquina_plancha

                if etapa >= 3:
                    lote.idempplanchapre = empleado_plancha_pre
                    lote.fechatermplanchapre = ahora + timedelta(hours=rng.randint(2, 10))
                    lote.idempplanchapost = empleado_plancha_post
                    lote.fechatermplanchapost = ahora + timedelta(hours=rng.randint(3, 12))
                    lote.idmaqplancha = maquina_plancha

                if etapa >= 4:
                    lote.idempcorte = empleado_corte
                    lote.idmaqcorte = maquina_corte
                    lote.fechatermcorte = ahora + timedelta(hours=rng.randint(4, 14))
                    lotes_terminados_proceso += 1

                if etapa >= 5:
                    lote.fechaempa = ahora + timedelta(hours=rng.randint(6, 18))
                    lotes_empaquetados += 1

                lote.save()

            pedido.loteterminado = lotes_terminados_proceso
            if lotes and lotes_empaquetados == len(lotes):
                pedido.fechafin = ahora + timedelta(days=rng.randint(1, 5))
            pedido.save(update_fields=['loteterminado', 'fechafin'])

            pedidos_creados.append((pedido, len(lotes)))

        pedidos_orden_qs = Pedido.objects.filter(idordenpedido=orden)
        if pedidos_orden_qs.exists() and not pedidos_orden_qs.filter(fechafin__isnull=True).exists():
            orden.fechafin = pedidos_orden_qs.aggregate(max_fecha=Max('fechafin')).get('max_fecha')
            orden.save(update_fields=['fechafin'])

    for i in range(5):
        comentario = Comentariosmaquinas.objects.create(
            idmaquina=maquinas[i],
            idempleado=empleados[i],
            comentario=COMENTARIOS_SEED[i],
            fecharegistro=ahora + timedelta(minutes=i),
            solucionado=0 if i % 2 == 0 else 1,
        )
        comentarios.append(comentario)

    return {
        'clientes': clientes,
        'modelos': modelos,
        'ordenes': ordenes,
        'pedidos': pedidos_creados,
        'empleados': empleados,
        'maquinas': maquinas,
        'comentarios': comentarios,
    }