# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import User, Group

from django.forms import ModelForm



class Parking(models.Model):
	matricula=models.CharField(max_length=10,blank=False)
	user=models.CharField(max_length=10)
	fecha_ingreso=models.DateTimeField(null=True)
	fecha_salida=models.DateTimeField(null=True,blank=True)

	abierto=models.BooleanField(default=True)
##Modificación pAra motos realizada el 21 de Feb 2020
	moto=models.BooleanField(default=False)

	fecha=models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.matricula

class ParkingForm(ModelForm):
	class Meta:
		model=Parking
		exclude=['fecha_ingreso','user','fecha']


class Vitacora(models.Model):
	user=models.CharField(max_length=10)

	matricula=models.CharField(max_length=10)
	obs=models.CharField(max_length=100)
	fecha=models.DateTimeField(auto_now=True)

@python_2_unicode_compatible
class Pagos(models.Model):
	matricula=models.ForeignKey(Parking,on_delete=models.PROTECT)
	#pago=models.IntegerField()
	pago=models.DecimalField(max_digits=4,decimal_places=2)
	fecha=models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.matricula)


class Contrato(models.Model):

	matricula=models.CharField(max_length=10,blank=False)
	inicio=models.DateField(null=False)
	final=models.DateField(null=False)
	coste=models.IntegerField(default=0)
	cliente=models.CharField(max_length=70)
	obs=models.TextField(max_length=200)
	vigente=models.BooleanField(default=True)
	fecha=models.DateField(auto_now=True)
	user=models.CharField(max_length=20,default="")

	def is_vigente(cls,date):
		inicio=cls.inicio
		final=cls.final

		flag=True

		if date>=inicio:
			if date<=final:

				flag=True
			else:
				flag=False
		else:
			flag=False

		return flag





class ContratoForm(ModelForm):
	class Meta:
		model=Contrato
		exclude=['user']