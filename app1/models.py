# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User, Group


class Parking(models.Model):
	matricula=models.CharField(max_length=10,blank=False)
	user=models.CharField(max_length=10)
	fecha_ingreso=models.DateTimeField(null=True)
	fecha_salida=models.DateTimeField(null=True,blank=True)

	abierto=models.BooleanField(default=True)

	fecha=models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.matricula

class Vitacora(models.Model):
	user=models.CharField(max_length=10)

	matricula=models.CharField(max_length=10)
	obs=models.CharField(max_length=100)
	fecha=models.DateTimeField(auto_now=True)

@python_2_unicode_compatible
class Pagos(models.Model):
	matricula=models.ForeignKey(Parking,on_delete=models.PROTECT)
	pago=models.IntegerField()
	fecha=models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.matricula)


class Contrato(models.Model):

	matricula=models.CharField(max_length=10,blank=False)
	dueno=models.CharField(max_length=50)
	inicio=models.DateTimeField(null=False)
	final=models.DateTimeField(null=False)
	cliente=models.CharField(max_length=70)
	obs=models.TextField(max_length=200)