from django.conf.urls import url

from . import views

urlpatterns=[
	url(r'^$',views.index, name='index'),
	url(r'^administrador/',views.administrador, name='administrador'),
	url(r'^ingresos/',views.ingresos, name='ingresos'),

	url(r'^home/',views.home, name='home'),
	url(r'^ingreso/',views.ingreso, name='ingreso'),
	url(r'^salida/',views.salida, name='salida'),
	url(r'^total_pagar/',views.total_pagar, name='total_pagar'),



]