from django.core.management.base import BaseCommand
#from authentication.models import Account
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):
        if Group.objects.count() == 0:
            #create Administrador y Operador
            administrador = Group.objects.create(name="Administrador")
            administrador.save()
            operador = Group.objects.create(name="Operador")
            operador.save()
            print ('Groups Administrador y Operadro were created...')
        else:
            print ('Groups already exist')

        if User.objects.count() == 0:
            username = "erick"
            email = "erickvasba@gmail.com"
            password = 'p@rqueo_p@ss'
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')
        
        
