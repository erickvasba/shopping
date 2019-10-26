# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User, Group

from app1.forms import Ingreso
from app1.models import *
import json
import datetime
import time
### ESCPOS
from escpos.printer import Usb
from app1.decorators import *


# Create your views here.

def index(request):
	return redirect('login')

####VIEWS OPERADOR
@login_required
@group_required('Operador','Admin')
def home(request):
	usuario=request.user
	##agarramos GRUPO de Usuario
	try:
		grupo=Group.objects.get(user=usuario)
	except:
		print "-> Usuario no tiene GRUPO!!!"
		grupo="Visita"
	if usuario.is_authenticated():
		if str(grupo)=='Operador':
			p=Parking.objects.filter(abierto=True).order_by('-fecha_ingreso')
			#seleccionamos laas ultimas salidas
			
			cont=({
				'parking':p,
				'user':usuario.username,
				
				})
			
			return render(request,'Operador/home.html',cont)

		elif str(grupo)=='Administrador':
			return redirect('administrador')

		else:
			return HttpResponse("Visita")
	else:
		return redirect('login')

##for ajax request

@login_required
@group_required('Operador')
def ingreso(request):
	r={}
	usuario=request.user.username
	if request.is_ajax() and request.POST:
		data_js=request.POST.get('data')
		data_dc=json.loads(data_js)
		mat=str(data_dc[0]['matricula']).upper()
		if len(mat)==6:
			num=mat[0:3]
			letra=mat[3:6]
			matricula=num+"-"+letra
		elif len(mat)==7:
			num=mat[0:4]
			letra=mat[4:7]
			matricula=num+"-"+letra
		else:
			matricula=mat
		user=str(data_dc[1]['user'])
		print matricula+"<->"+user
		try: ##vemos si la matricula esta en parking
			p=Parking.objects.filter(matricula=matricula)
			time_in=datetime.datetime.now()
			if p.last(): #si EXISTE 
				if (p.last().fecha_salida): #si tiene fecha de SALIDA, PODEMOS GUARDAR
					park=Parking.objects.create(matricula=matricula,user=user,fecha_ingreso=time_in)
					park.save()
					r.update({'status':"true"})
				else: # si no salio, NO podemos volver a guardar
					print "No se puede volver a INgresar"
					r.update({'status':"false"})
			else: ##si no existe PODEMOS GUARDAR
				park=Parking.objects.create(matricula=matricula,user=user,fecha_ingreso=time_in)
				park.save()
				imprimir_ticket(str(park.matricula),str(park.fecha_ingreso.strftime("%d-%m-%Y %H:%M:%S")))
				r.update({'status':"true"})
		except:
			print "eroor en query!!!"
	js_resp=json.dumps(r)
	return HttpResponse(js_resp, content_type='application/json')


@login_required
@group_required('Operador')
def salida(request):
	r={}

	if request.is_ajax() and request.POST:
		data_js=request.POST.get('data')
		data_dc=json.loads(data_js)
##en mayusculas
		mat=str(data_dc[0]['matricula']).upper()
		print "++++"+mat
		if len(mat)==6:
			num=mat[0:3]
			letra=mat[3:6]
			matricula=num+"-"+letra
		elif len(mat)==7:
			num=mat[0:4]
			letra=mat[4:7]
			matricula=num+"-"+letra
		else:
			matricula=mat
		p=Parking.objects.filter(matricula=matricula)
		if p.last():
			if(p.last().fecha_salida):	##si ya tiene fecha de salida no puede volver a salir
				print "no se puede realizar registro la Matricula Ya salio!!!"
				r.update({'status':"false"})
			else: ## si no tiene fecha de salida podemos realizar salida
				park=Parking.objects.get(matricula=matricula)
				t=datetime.datetime.now()
				park.fecha_salida=t
				park.abierto=False
				park.save()
				total=pagar_(matricula)
				r.update({'status':'true','pagar':total})
				##guardamoes le pago
				pp=Pagos.objects.create(matricula=park,pago=total)
		else: ## SI NO EXISTE no podemos guardar
			print "NO SE puede realizar registro de salida, por que la matricula no ingreso"
			r.update({'status':'false'})
	js_resp=json.dumps(r)
	return HttpResponse(js_resp, content_type='application/json')

@login_required
@group_required('Operador')
def arqueo (request):
	u=request.user.username
	if request.method=='POST':
		pass
	else:
		mat=[]
		total=0
		fecha=datetime.datetime.now().date()
		#p=Parking.objects.filter(fecha_salida__date=datetime.datetime.now().date())
		p=Pagos.objects.filter(fecha__date=fecha)
		t=get_template('Operador/arqueo.html')

		for i in p:
			total=total+ i.pago

		cont=({
			'p':p,
			'user':u,
			'fecha':fecha,
			'total':total
		})

		html=t.render(cont)

		return HttpResponse (html)
@login_required
@group_required('Operador')
def salidas(request):
	user=request.user
	if request.method=="POST":
		pass
	else:
		salidas=Parking.objects.filter(abierto=False,fecha_salida__date=datetime.datetime.now().date()).order_by('-fecha_salida')[:20]
		f=datetime.datetime.now().date()
		t=get_template('Operador/salidas.html')

		cont=({
			'salidas':salidas,
			'user':user,
			'fecha':f,

		})

		html=t.render(cont)

		return HttpResponse(html)





#########VIEWS ADMIN############

def administrador(request): ##INICIO
	u=request.user.username
	if request.method=='POST':
		pass
	else:
		mat=[]
		total=0
		t=get_template('Admin/index.html') # for admin

		p=Parking.objects.filter(abierto=True)
		for i in p:
			pp=pagar_(i.matricula)
			mat.append({'mat':i,'pagar':pp})
			total=total+pp

		cont=({
			'p':p,
			'user':u,
			'mat':mat,
			'total':total
			})
		html=t.render(cont)

		return HttpResponse(html)


##########fin admin ######

def ingresos(request):  #ARQUEO para ADMIN
	u=request.user.username
	if request.method=='POST':
		pass
	else:
		mat=[]
		total=0
		fecha=datetime.datetime.now().date()
		t=get_template('arqueo.html')
		p=Pagos.objects.filter(fecha__date=datetime.datetime.now().date())

		for i in p:
			pp=pagar_(i.matricula)
			mat.append({'mat':i,'pagar':pp})
			total=total+pp

		cont=({
			'p':p,
			'user':u,
			'mat':mat,
			'fecha':fecha,
			'total':total
		})

		html=t.render(cont)

		return HttpResponse(html)



def imprimir_ticket(x,y):
	c=0
	print "Imprimiendo ----><"
	try:
		p = Usb(0x04b8, 0x0202)
		while(not p ):
			print "gettin access to printer"
			c=c+1
			time.sleep(1)
			if(c==5):
				print "non se puede conectar a Impresora..."
				print "Saliendo sin Imprimir!!!!"
				break

	except:
		print "Error con impresora!!!"
	try:
		p.text("=====================================\n")
		p.text("  ---------- SHOPPING NORTE ---------- \n")
		p.text("  ---------- Parking Ticket ---------- \n")
		p.text("===================================== \n")
		p.text("Matricula:        "+x+"          \n")
		p.text("Fecha de ingreso: "+y+"\n")
		p.text("       Gracias por su preferencia!!!  \n")
		p.text("=====================================\n")
		p.text("========== La Paz - Bolivia  ========\n")
		p.text("\n")
		p.cut()
	except:
		print"no se pudo imprimir"


def total_pagar(request):
	r={}
	if request.is_ajax() and request.POST:
		data_j=request.POST.get('data')
		data_d=json.loads(data_j)
		x=data_d[0]['matricula'].upper()

		print x
		p=Parking.objects.get(matricula=x)
		print p
		inicio=p.fecha_ingreso
		salida=p.fecha_salida

		i=time.mktime(inicio.timetuple())
		#s=salida.mktime(salida.timetuple())
		now=datetime.datetime.now()
		s=time.mktime(now.timetuple())
		total_seconds=s-i

		if total_seconds<=2400:
			total_pagar=5
		elif (total_seconds>=2400 and total_seconds<=3600):
			total_pagar=8
		elif (total_seconds>=3600 and total_seconds<=5400):
			total_pagar=9.50
		elif (total_seconds>=5400 and total_seconds<=7200):
			total_pagar=11
		elif (total_seconds>=7200 and total_seconds<=9000):
			total_pagar=12.50
		elif (total_seconds>=9000 and total_seconds<=10800):
			total_pagar=14
		elif (total_seconds>=10800 and total_seconds<=12600):
			total_pagar=15.5
		elif (total_seconds>=12600 and total_seconds<=14400):
			total_pagar=17
		elif (total_seconds>=14400 and total_seconds<=16200):
			total_pagar=18.50
		elif (total_seconds>=16200 and total_seconds<=1800):
			total_pagar=20
		
		else:
			segundos_adicionales=total_seconds-18000
			horas_adicionales=segundos_adicionales/3600

			horas_pagar=round(horas_adicionales)*2

			total_pagar=20+horas_pagar

		minutos=round(total_seconds/60)

		#total_horas=total_seconds/3600
		#total_pagar=round(total_horas*8,2)
		r.update({'pagar':total_pagar,'min':minutos})

		resp_j=json.dumps(r)

		return HttpResponse (resp_j,content_type='application/json')

def pagar_(x):
	p=Parking.objects.get(matricula=x)
	##print p
	inicio=p.fecha_ingreso
	salida=p.fecha_salida
	i=time.mktime(inicio.timetuple())
	#s=salida.mktime(salida.timetuple())
	now=datetime.datetime.now()
	s=time.mktime(now.timetuple())
	total_seconds=s-i


	if total_seconds<=2400:
		total_pagar=5
	elif (total_seconds>=2400 and total_seconds<=3600):
		total_pagar=8
	elif (total_seconds>=3600 and total_seconds<=5400):
		total_pagar=9.50
	elif (total_seconds>=5400 and total_seconds<=7200):
		total_pagar=11
	elif (total_seconds>=7200 and total_seconds<=9000):
		total_pagar=12.50
	elif (total_seconds>=9000 and total_seconds<=10800):
		total_pagar=14
	elif (total_seconds>=10800 and total_seconds<=12600):
		total_pagar=15.5
	elif (total_seconds>=12600 and total_seconds<=14400):
		total_pagar=17
	elif (total_seconds>=14400 and total_seconds<=16200):
		total_pagar=18.50
	elif (total_seconds>=16200 and total_seconds<=1800):
		total_pagar=20

##si es mayor a 18000() 5 horas
	else:
		segundos_adicionales=total_seconds-18000
		horas_adicionales=segundos_adicionales/3600

		horas_pagar=round(horas_adicionales)*2

		total_pagar=20+horas_pagar


	return total_pagar












		
