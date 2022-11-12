#!/usr/local/bin/python
import os
import sys
import subprocess
import printer
from escpos.printer import Usb

def pr(q,w):
	x=q+" "+w
	
	##IT WORKS!!!!
	#subprocess.call(["sudo python2.7 /home/erick/shop1/app1/printing.py "+x,"eri.124"],shell=True)

	##IT ALSO WORKS !!! 
	# if using container should point to the path where app is placed in WORKDIR etc...
	# take care when use "SUDO" not works in container PYTHON, and be sure to Point to call the exact printer.py file
	subprocess.call(["/usr/local/bin/python /app/app1/printer.py "+x],shell=True)


	
	
