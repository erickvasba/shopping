from django.conf.urls import url

from . import views

urlpatterns=[
##admin
	url(r'^$',views.index, name='index2'),
	url(r'^administrador/',views.administrador, name='administrador'),
	url(r'^ingresos/',views.arqueo, name='ingresos'),
	url(r'^arqueo_admin/$',views.arqueo_admin, name='arqueo_admin'),
	url(r'^arqueo_admin/(?P<data>[\w\-]+)/$',views.toExcel, name='toExcel'),
	

	
	

	#URL AJAX
	
##operador
	url(r'^home/',views.home, name='home'),
	url(r'^arqueo/',views.arqueo, name='arqueo'),
	url(r'^salidas/',views.salidas, name='salidas'),
	url(r'^ingreso/',views.ingreso, name='ingreso'),
	url(r'^salida/',views.salida, name='salida'),
	url(r'^total_pagar/',views.total_pagar, name='total_pagar'),

]