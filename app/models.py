# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Cliente(models.Model):
    idcliente = models.AutoField(db_column='idCliente', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.
    contacto = models.CharField(db_column='Contacto', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cliente'


class Comentariosmaquinas(models.Model):
    idcomentariosmaquinas = models.AutoField(db_column='idComentariosMaquinas', primary_key=True)  # Field name made lowercase.
    idmaquina = models.ForeignKey('Maquina', models.DO_NOTHING, db_column='idMaquina')  # Field name made lowercase.
    idempleado = models.ForeignKey('Empleado', models.DO_NOTHING, db_column='idEmpleado')  # Field name made lowercase.
    comentario = models.TextField(db_column='Comentario')  # Field name made lowercase.
    fecharegistro = models.DateTimeField(db_column='FechaRegistro')  # Field name made lowercase.
    solucionado = models.IntegerField(db_column='Solucionado')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'comentariosmaquinas'


class Empleado(models.Model):
    idempleado = models.AutoField(db_column='idEmpleado', primary_key=True)  # Field name made lowercase.
    area = models.CharField(db_column='Area', max_length=45)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=45)  # Field name made lowercase.
    apellidos = models.CharField(db_column='Apellidos', max_length=45)  # Field name made lowercase.
    estatus = models.IntegerField(db_column='Estatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'empleado'


class Lote(models.Model):
    idlote = models.AutoField(db_column='idLote', primary_key=True)  # Field name made lowercase.
    idorden = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='idOrden')  # Field name made lowercase.
    idemptejido = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='idEmpTejido', blank=True, null=True)  # Field name made lowercase.
    idempplancha = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='idEmpPlancha', related_name='lote_idempplancha_set', blank=True, null=True)  # Field name made lowercase.
    idempcorte = models.ForeignKey(Empleado, models.DO_NOTHING, db_column='idEmpCorte', related_name='lote_idempcorte_set', blank=True, null=True)  # Field name made lowercase.
    idmqutejido = models.ForeignKey('Maquina', models.DO_NOTHING, db_column='idMquTejido', blank=True, null=True)  # Field name made lowercase.
    idmaqplancha = models.ForeignKey('Maquina', models.DO_NOTHING, db_column='idMaqPlancha', related_name='lote_idmaqplancha_set', blank=True, null=True)  # Field name made lowercase.
    idmaqcorte = models.ForeignKey('Maquina', models.DO_NOTHING, db_column='idMaqCorte', related_name='lote_idmaqcorte_set', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.IntegerField(db_column='Cantidad')  # Field name made lowercase.
    fechatermtejido = models.DateTimeField(db_column='FechaTermTejido', blank=True, null=True)  # Field name made lowercase.
    fechatermplancha = models.DateTimeField(db_column='FechaTermPlancha', blank=True, null=True)  # Field name made lowercase.
    fechatermcorte = models.DateTimeField(db_column='FechaTermCorte', blank=True, null=True)  # Field name made lowercase.
    fechaempa = models.DateTimeField(db_column='FechaEmpa', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'lote'


class Maquina(models.Model):
    idmaquina = models.AutoField(db_column='idMaquina', primary_key=True)  # Field name made lowercase.
    area = models.CharField(db_column='Area', max_length=45)  # Field name made lowercase.
    numero = models.IntegerField(db_column='Numero')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'maquina'


class Modelo(models.Model):
    idmodelo = models.AutoField(db_column='idModelo', primary_key=True)  # Field name made lowercase.
    folio = models.CharField(db_column='Folio', max_length=45)  # Field name made lowercase.
    modelo = models.CharField(db_column='Modelo', max_length=45)  # Field name made lowercase.
    cantidadhilo = models.IntegerField(db_column='CantidadHilo')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'modelo'


class Ordendepedido(models.Model):
    idordendepedido = models.AutoField(db_column='idOrdenDePedido', primary_key=True)  # Field name made lowercase.
    idcliente = models.ForeignKey(Cliente, models.DO_NOTHING, db_column='idCliente')  # Field name made lowercase.
    fechainicio = models.DateTimeField(db_column='FechaInicio')  # Field name made lowercase.
    fechafin = models.DateTimeField(db_column='FechaFin', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ordendepedido'


class Pedido(models.Model):
    idpedido = models.AutoField(db_column='idPedido', primary_key=True)  # Field name made lowercase.
    idordenpedido = models.ForeignKey(Ordendepedido, models.DO_NOTHING, db_column='idOrdenPedido')  # Field name made lowercase.
    idmodelo = models.ForeignKey(Modelo, models.DO_NOTHING, db_column='idModelo')  # Field name made lowercase.
    talla = models.IntegerField(db_column='Talla')  # Field name made lowercase.
    cantidad = models.IntegerField(db_column='Cantidad')  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=45)  # Field name made lowercase.
    totallotes = models.IntegerField(db_column='TotalLotes')  # Field name made lowercase.
    loteterminado = models.IntegerField(db_column='LoteTerminado')  # Field name made lowercase.
    fechainicio = models.DateTimeField(db_column='FechaInicio')  # Field name made lowercase.
    fechafin = models.DateTimeField(db_column='FechaFin')  # Field name made lowercase.
    fechaprevista = models.DateTimeField(db_column='FechaPrevista')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pedido'
