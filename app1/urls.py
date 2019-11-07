from django.conf.urls import url

from . import views

urlpatterns=[
##admin
	url(r'^$',views.index, name='index2'),
	url(r'^administrador/',views.administrador, name='administrador'),
	url(r'^ingresos/',views.arqueo, name='ingresos'),
	url(r'^arqueo_admin/$',views.arqueo_admin, name='arqueo_admin'),
	url(r'^arqueo_admin/(?P<data>[\w\-]+)/$',views.toExcel, name='toExcel'),
	url(r'^modificar/ingreso/$',views.mod_ingreso, name='mod_ingreso'),
	url(r'^modificar/salida/$',views.mod_salida, name='mod_salida'),
	url(r'^modificar/salida/(?P<mat>[0-9]+)$',views.mod_salida_id, name='mod_salida_id'),
	url(r'^modificar/modificado/$',views.modificado, name='modificado'),

	url(r'^contrato/$',views.contrato, name='contrato'),
	url(r'^contratos/$',views.contratos_all, name='contratos_all'),

	

	#URL AJAX
	
##operador
	url(r'^home/',views.home, name='home'),
	url(r'^arqueo/',views.arqueo, name='arqueo'),
	url(r'^salidas/',views.salidas, name='salidas'),
	url(r'^ingreso/',views.ingreso, name='ingreso'),
	url(r'^salida/',views.salida, name='salida'),
	url(r'^total_pagar/',views.total_pagar, name='total_pagar'),

]