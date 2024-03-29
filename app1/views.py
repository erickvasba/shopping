# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User, Group

from app1.forms import Ingreso, Buscar, Id_matricula
from app1.models import *
import json
import datetime
import time
### ESCPOS
from escpos.printer import Usb
from app1.decorators import *

##EXCEL
import xlwt

import os
import sys
import subprocess
import printer
import controller


# Create your views here.

def index(request):
	return redirect('login')

####VIEWS OPERADOR
@login_required
@group_required('Operador','Administrador')
def home(request):
	usuario=request.user
	##agarramos GRUPO de Usuario
	try:
		grupo=Group.objects.get(user=usuario)
	except:
		print "-> Usuario no tiene GRUPO!!!"
		grupo="Visita"
	f=datetime.datetime.now().date()
	if usuario.is_authenticated():
		if str(grupo)=='Operador':
			p=Parking.objects.filter(abierto=True).order_by('-fecha_ingreso')
			p_count=p.count()
			##todos los contratos vigentes
			c=Contrato.objects.filter(vigente=True)
			cont=({
				'parking':p,
				'count':p_count,
				'c':c,
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
		##modificado para motoc 21 FEb2020
		moto=str(data_dc[2]['moto'])
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

		print matricula+"<->"+moto+"<->"+user


		############### verficamos si la MAtricula es contrato
		try: ##vemos si la matricula esta en parking
			p=Parking.objects.filter(matricula=matricula,abierto=True)
			time_in=datetime.datetime.now()
			if p.last(): #si EXISTE 
				if (p.last().fecha_salida): #si tiene fecha de SALIDA, PODEMOS GUARDAR
					park=Parking.objects.create(matricula=matricula,user=user,fecha_ingreso=time_in,moto=moto)
					park.save()
					r.update({'status':"true"})
				else: # si no salio, NO podemos volver a guardar
					print "No se puede volver a INgresar"
					r.update({'status':"false"})
			else: ##si no existe PODEMOS GUARDAR
				park=Parking.objects.create(matricula=matricula,user=user,fecha_ingreso=time_in,moto=moto)
				park.save()
				imprimir_ticket(str(park.matricula),str(park.fecha_ingreso.strftime("%d-%m-%Y %H:%M:%S")))
				r.update({'status':"true"})
		except:
			print "eroor en query def ingreso()!!!"
		################
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
		##agarramos COntrato
		c=Contrato.objects.filter(matricula=matricula,vigente=True).last()
		
		if p.last():
			if(p.last().fecha_salida):	##si ya tiene fecha de salida no puede volver a salir
				print "no se puede realizar registro la Matricula Ya salio!!!"
				r.update({'status':"false"})
			else: ## si no tiene fecha de salida podemos realizar salida
			## la consulta nos devuelve solo un registro con Abierto TRUE
				parkpark=Parking.objects.filter(matricula=matricula,abierto=True)
				#Seleccionamos el unico registro 
				park=parkpark[0]

				t=datetime.datetime.now()
				park.fecha_salida=t
				park.abierto=False
				park.save()
				# SI es contrato no paga Nada
				if c:
					total=0
				else:
					##modificado para motocicletas 21 Feb 2020
					#Si es monto se debe calcular con otra tarifa
					## si el parking es moto
					if(park.moto):
						##debe ir una funcion que calcule el monto total para motos
						total=moto_pagar_(matricula)
					else:
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
@group_required('Operador',"Administrador")
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
@login_required
@group_required('Administrador')
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
@login_required
@group_required('Administrador')
def arqueo_admin(request):
	u=request.user
	if request.method=='POST':
		f=Buscar(request.POST)
		if f.is_valid():
			total=0
			fecha=datetime.datetime.now().date().strftime("%Y-%m-%d")
			fecha_a_buscar=f.cleaned_data.get("fecha_buscar")
			p=Pagos.objects.filter(fecha__date=fecha_a_buscar)
			for i in p:
				total=total+i.pago

			fb=Buscar()

			t=get_template('Admin/arqueo_admin.html')
			cont=({
				'p':p,
				'user':u,
				'fecha':fecha_a_buscar,
				'fb':fb,
				'total':total
				})
			
			return render(request,'Admin/arqueo_admin.html',cont)
		else:
			return redirect("arqueo_admin")
	else:
		total=0
		fecha=datetime.datetime.now().date().strftime("%Y-%m-%d")
		#p=Parking.objects.filter(fecha_salida__date=datetime.datetime.now().date())
		p=Pagos.objects.filter(fecha__date=fecha)
		fb=Buscar()

		for i in p:
			total=total+ i.pago

		cont=({
			'p':p,
			'user':u,
			'fecha':fecha,
			'total':total,
			'fb':fb
		})
		return render (request,'Admin/arqueo_admin.html',cont)


@login_required
@group_required('Administrador')
def toExcel(request,data):

	fecha=str(data)
	total=0
	
	response = HttpResponse(content_type='application/ms-excel')
	## .xlsx DOnt work on microsoft Office. better .xls
	response['Content-Disposition'] = 'attachment; filename="Arqueo_'+fecha+'.xls"' 
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Reporte Arqueo') # this will make a sheet named Users Data
	#Encabezados
	row_num=0
	font_style=xlwt.XFStyle()
	font_style.font.bold=True
	
	columns=['Matricula','Fecha Ingreso','Fecha Salida','Pago Bs.','Fecha de Pago']
	for col_num in range(len(columns)):
		ws.write(row_num,col_num,columns[col_num],font_style)

	font_style_data=xlwt.XFStyle()
	
	data=[]  #array for tuples

	#p=Pagos.objects.filter(fecha__date=fecha).values_list('matricula','pago','fecha')
	p=Pagos.objects.filter(fecha__date=fecha)
	row_num+=1
	for i in p:
		data.append((str(i.matricula.matricula),str(i.matricula.fecha_ingreso.strftime("%Y-%m-%d %H:%M:%S")),str(i.matricula.fecha_salida.strftime("%Y-%m-%d %H:%M:%S")),str(i.pago),str(i.fecha.strftime("%Y-%m-%d %H:%M:%S"))))

	for row in data:
		total=total+float(row[3])
		row_num+=1
		for col_ in range(len(row)):
			ws.write(row_num,col_,row[col_],font_style_data)
		


	row_num+=1
	row_num+=1
	total_data=["","",'Total Bs.',str(total)]
	for i in range(len(total_data)):
		ws.write(row_num,i,total_data[i],font_style)
	


	wb.save(response)
	return response
    
def toExcel_report(request,data):
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Users Data') # this will make a sheet named Users Data
	#Encabezados
	row_num=0
	font_style=xlwt.XFStyle()
	font_style.font.bold=True
	columns=['Matricula','Fecha Ingreso','Fecha Salida','Pago','Fecha de Pago']
	for col_num in range(len(columns)):
		ws.write(row_num,col_num,columns[col_num],font_style)

	font_style_data=xlwt.XFStyle()
	#    	p=Pagos.objects.filter(fecha__date=datetime.datetime.now().date())
	wb.save(response)
	return response

@login_required
@group_required('Administrador')
def mod_ingreso(request):
	user=request.user
	if request.method=='POST':
		f=Id_matricula(request.POST)
		if f.is_valid():
			id_mat=f.cleaned_data.get("id_mat")
			p=Parking.objects.get(id=id_mat)
			p.delete()
			print "MAt Borrada!!!"
			return redirect('mod_ingreso')
		else:
			print "Error"
			return HttpResponse("Error al borrar MAT")
	else:
		data=[]
		p=Parking.objects.filter(fecha_ingreso__date=datetime.datetime.now().date(),abierto=True)

		for i in p:
			f=Id_matricula(initial={'id_mat':i.id})
			data.append({'p':i,'f':f})
		cont=({
			'data':data
			})
		return render(request,'Admin/mod_ingreso.html',cont)

@login_required
@group_required('Administrador')
def mod_salida(request):
	if request.method=='POST':
		pass
	else:
		p=Parking.objects.filter(fecha_salida__date=datetime.datetime.now().date())
		f=ParkingForm()
		cont=({
			'p':p,
			})
		return render(request,'Admin/mod_salida.html',cont)

@login_required
@group_required('Administrador')
def mod_salida_id(request,mat):
	user=request.user
	if request.method=='POST':

		f=ParkingForm(request.POST)
		if f.is_valid():
			a= f.cleaned_data.get('matricula')
			b= f.cleaned_data.get('fecha_salida')
			c= f.cleaned_data.get('abierto')

			try:
				p=Parking.objects.filter(matricula=str(a)).last()
				p.fecha_salida=None
				p.abierto=c
				p.save()

			except:
				print "Error al modificar Reingreso"

			try:
				pa=Pagos.objects.get(matricula=Parking.objects.get(id=p.id))
				pa.delete()
				print "Pago Borrado"
			except:
				print "Error al agarrar pago"
		else:
			pass

		return redirect('modificado')
		
	else:

		p=Parking.objects.get(id=int(mat))
		if p.fecha_salida:
			f=ParkingForm({'matricula':p.matricula,'fecha_salida':p.fecha_salida,'abierto':p.abierto})
			cont=({
				'f':f,
				'id':p.id
				})
			return render(request,'Admin/mod_salida_id.html',cont)
		else:
			print "NICE TRY :)"
			return redirect('mod_salida')

@login_required
@group_required('Administrador','Operador')
def contrato(request):
	user=request.user
	grupo=Group.objects.get(user=user).name;
	if request.method=='POST':
		f=ContratoForm(request.POST)
		if f.is_valid():
			print "Form valid"
			#form tmp for editing data before saving it

			tmpf=f.save(commit=False)
			tmpf.user=str(user.username)
			tmpf.matricula=str(tmpf.matricula).upper();
			print "--<<<"+tmpf.matricula
			tmpf.save()

			return redirect('contrato')
		else:
			print "bad form"
			return redirect('contrato')
	else:
		f=ContratoForm()
		cont=({
			'f':f,
			'grupo':grupo
			})
		return render(request,'Admin/contrato.html',cont)

@login_required
@group_required('Administrador','Operador')
def contratos_all(request):
	user=request.user
	grupo=Group.objects.get(user=user).name;
	if request.method=='POST':

		if Id_matricula(request.POST).is_valid():
			f=Id_matricula(request.POST)
			if f.is_valid():
				id_mat=f.cleaned_data.get('id_mat')
				print id_mat
				c=Contrato.objects.get(id=id_mat)

				g=ContratoForm(initial={'matricula':c.matricula,'inicio':c.inicio,'final':c.final,'coste':c.coste,'cliente':c.cliente,'obs':c.obs,'vigente':c.vigente})

				cont=({
					'g':g,
					'grupo':grupo


					})
				return render(request,'Admin/mod_contrato.html',cont)
		else:
			print "MOdificandooo"
			
			if ContratoForm(request.POST).is_valid():

				f=ContratoForm(request.POST)
				if f.is_valid():
					tmpf=f.save(commit=False)

					matricula= f.cleaned_data.get('matricula')
					c=Contrato.objects.filter(matricula=matricula).last()


					c.inicio= f.cleaned_data.get('inicio')
					c.final= f.cleaned_data.get('final')
					c.coste= f.cleaned_data.get('coste')
					c.cliente= f.cleaned_data.get('cliente')
					c.obs= f.cleaned_data.get('obs')
					c.vigente= f.cleaned_data.get('vigente')
					#tmpf.fecha= f.cleaned_data.get('fecha')
					c.user=user.username

					c.save()
					print "Contrato Modificado!!!"

					return redirect('contratos_all')

###


	else:
		data=[]
		t='Admin/contratos_all.html'

		c=Contrato.objects.all().order_by('-fecha')[:30]

		for i in c:
			f=Id_matricula({'id_mat':i.id})
			data.append({'c':i,'f':f})



		cont=({
			'c':c,
			'data':data,
			'grupo':grupo
			})
		return render(request,t,cont)



#oagina solo de mensaje de modificacion
def modificado(request):
	if request.method=='POST':
		pass
	else:
		t=get_template('Admin/modificado.html')
		cont=({})
		html=t.render(cont)
		return HttpResponse(html)


##########fin admin ######
@login_required
@group_required('Administrador')

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


def imprimir_ticket2(x,y):
	print "OK!!! Ingresado -> "+str(x)+ " - "+str(y)

def imprimir_ticket(x,y):
	try:
		#subprocess.call(['sudo python /var/www/scripts_py/controller.py',"eri.124"],shell=True)
		controller.pr(x,y)
	except:
		print "subprocess not working"


def imprimir_ticket1(x,y):
	c=0
	print "Imprimiendo ----><"
	try:
		#p = Usb(0x04b8, 0x0202)
		p = Usb(0x067b, 0x2305)
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
		#p.text("  ---------- SHOPPING NORTE ---------- \n")
		#p.text("  ---------- Parking Ticket ---------- \n")
		#p.text("===================================== \n")
		#p.text("Matricula:        "+x+"          \n")
		#p.text("Fecha de ingreso: "+y+"\n")
		#p.text("       Gracias por su preferencia!!!  \n")
		#p.text("=====================================\n")
		#p.text("========== La Paz - Bolivia  ========\n")
		p.text("\n")
		p.cut()
	except:
		print"no se pudo imprimir"

##funcion para verificar cuanto se debe pagar
def total_pagar(request):
	r={}
	if request.is_ajax() and request.POST:
		data_j=request.POST.get('data')
		data_d=json.loads(data_j)
		x=data_d[0]['matricula'].upper()

		print "---->"+x

##verificamos si TIene COntrato
		c=Contrato.objects.filter(matricula=x,vigente=True)
		if c: #si es contrato no PAGA
			print "CONTRATO"
			r.update({'pagar':0,'horas':0,'min':0})
			resp_j=json.dumps(r)
		else:
			print "NO CONTRATO"

##end VErificar COntrato

			print x
			##Seleccionamos el parking Abierto, que en realidad es solo uno
			pp=Parking.objects.filter(matricula=x,abierto=True)
			#seleccionamos el unico parking disponible en el query
			p=pp[0]

			print p

			##aca se debe preguntar si es MOTO, para calcular nuevo Coste segun tarifario



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
			elif (total_seconds>=16200 and total_seconds<=18000):
				total_pagar=20
			
			else:
				segundos_adicionales=total_seconds-18000
				horas_adicionales=segundos_adicionales/3600
				print str(horas_adicionales)

				horas_pagar=round(horas_adicionales,0)*2
				#horas_pagar=round(horas_adicionales*2)

				total_pagar=20+horas_pagar


			
			minutos_totales=round(total_seconds/60)
			tiempo=divmod(minutos_totales,60)

			#total_horas=total_seconds/3600
			#total_pagar=round(total_horas*8,2)
			r.update({'pagar':total_pagar,'horas':tiempo[0],'min':tiempo[1]})

			resp_j=json.dumps(r)

		return HttpResponse (resp_j,content_type='application/json')

def busqueda(request):
	r={}
	rr=[]
	if request.is_ajax() and request.POST:
		data_j=request.POST.get('data')
		data_d=json.loads(data_j)
		buscar=data_d[0]['matricula']

		try:
			posibles=Parking.objects.filter(matricula__startswith=buscar,abierto=True)
			for i in posibles:
				rr.append({'mat':i.matricula})
				

		except:
			print "Error en buscar posibles matches"
			rr.append({'mat':000})

		resp_j=json.dumps(rr)


		return HttpResponse (resp_j,content_type='application/json')



def pagar_(x):
	#reemplazamos el "-" porque Contratos no tiene "-"
	##xx=x.replace("-","")
	c=Contrato.objects.filter(matricula=x,vigente=True)
	cc=c.last()
	print cc

	if(not c):
		pp=Parking.objects.filter(matricula=x).last()
		p=pp
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
		elif (total_seconds>=16200 and total_seconds<=18000):
			total_pagar=20

	##si es mayor a 18000() 5 horas
		else:
			segundos_adicionales=total_seconds-18000
			horas_adicionales=segundos_adicionales/3600
			print str(horas_adicionales)


			horas_pagar=round(horas_adicionales,0)*2

			#horas_pagar=horas_adicionales*2

			total_pagar=20+horas_pagar


		return total_pagar
		
	else:
		total_pagar=0.00
		return total_pagar

		


def moto_pagar_(mat):
	pp=Parking.objects.filter(matricula=mat).last()
	p=pp
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
	elif (total_seconds>=16200 and total_seconds<=18000):
		total_pagar=20

##si es mayor a 18000() 5 horas
	else:
		segundos_adicionales=total_seconds-18000
		horas_adicionales=segundos_adicionales/3600

		horas_pagar=round(horas_adicionales)*2

		total_pagar=20+horas_pagar
	##para pruebas
	#no importa nada de arriba devolvemos 9999
	total_pagar=9999


	return total_pagar













		
