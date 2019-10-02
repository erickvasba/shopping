# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

class AdminParking(admin.ModelAdmin):
	list_display=('matricula','user','fecha_ingreso','fecha_salida','abierto','fecha')

admin.site.register(Parking,AdminParking)

class AdminPagos(admin.ModelAdmin):
	list_display=('matricula','pago','fecha')

admin.site.register(Pagos,AdminPagos)

# Register your models here.
