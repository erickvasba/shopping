
import os
import sys
from escpos.printer import Usb
## According to ESCpos docs we need to add FILE
from escpos.printer import File

def printing(x,y,z):
	try:
		#p = Usb(0x067b, 0x02305, profile="POS-5890")
		#if using File, need to change the connection directly pointing to the printer file
		p = File("/dev/usb/lp0")
		while(not p):
			#p = Usb(0x067b, 0x02305, profile="POS-5890")
			#if using File, need to change the connection directly pointing to the printer file.. and thats it
			p = File("/dev/usb/lp0")
			time.sleep(1)

	except:
		print ("Error con impresora!!!")
	try:
		p.text("======================================\n")
		p.text(" ---------- SHOPPING NORTE ---------- \n")
		p.text(" ---------- Parking Ticket ---------- \n")
		p.text("======================================\n")
		p.text("Matricula:           "+x+"          \n")
		p.text("Fecha Ingreso: "+y+"_"+z+"\n")
		p.text("     Gracias por su preferencia!!!    \n")
		p.text("======================================\n")
		p.text("           La Paz - Bolivia           \n")
		p.text("\n")
		
		p.cut()
	except:
		print ("no se pudo imprimir")

if __name__=="__main__":
	mat=str(sys.argv[1])
	fecha=str(sys.argv[2])
	hora=str(sys.argv[3])

	#printing(mat,fecha)
	printing(mat,fecha,hora)
